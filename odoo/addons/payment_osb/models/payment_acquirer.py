# coding: utf-8
#
# Copyright © Lyra Network.
# This file is part of OSB plugin for Odoo. See COPYING.md for license details.
#
# Author:    Lyra Network (https://www.lyra.com)
# Copyright: Copyright © Lyra Network
# License:   http://www.gnu.org/licenses/agpl.html GNU Affero General Public License (AGPL v3)

import base64
from datetime import datetime
from hashlib import sha1, sha256
import hmac
import logging
import math
from os import path

from pkg_resources import parse_version

from odoo import models, api, release, fields, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools import convert_xml_import
from odoo.tools import float_round
from odoo.tools.float_utils import float_compare

from ..controllers.main import OsbController
from ..helpers import constants, tools
from .card import OsbCard
from .language import OsbLanguage
from odoo.addons.payment import utils as payment_utils

import urllib.parse as urlparse
import re

_logger = logging.getLogger(__name__)

class AcquirerOsb(models.Model):
    _inherit = 'payment.acquirer'

    def _get_notify_url(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        return urlparse.urljoin(base_url, OsbController._notify_url)

    def _get_languages(self):
        languages = constants.OSB_LANGUAGES
        return [(c, _(l)) for c, l in languages.items()]

    @api.depends('provider')
    def _osb_compute_multi_warning(self):
        for acquirer in self:
            acquirer.osb_multi_warning = (constants.OSB_PLUGIN_FEATURES.get('restrictmulti') == True) if (acquirer.provider == 'osbmulti') else False

    sign_algo_help = _('Algorithm used to compute the payment form signature. Selected algorithm must be the same as one configured in the OSB Back Office.')

    if constants.OSB_PLUGIN_FEATURES.get('shatwo') == False:
        sign_algo_help += _('The HMAC-SHA-256 algorithm should not be activated if it is not yet available in the OSB Back Office, the feature will be available soon.')

    providers = [('osb', _('OSB - Standard payment'))]
    ondelete_policy = {'osb': 'set default'}

    if constants.OSB_PLUGIN_FEATURES.get('multi') == True:
        providers.append(('osbmulti', _('OSB - Payment in installments')))
        ondelete_policy['osbmulti'] = 'set default'

    provider = fields.Selection(selection_add=providers, ondelete = ondelete_policy)

    osb_site_id = fields.Char(string=_('Shop ID'), help=_('The identifier provided by OSB.'), default=constants.OSB_PARAMS.get('SITE_ID'))
    osb_key_test = fields.Char(string=_('Key in test mode'), help=_('Key provided by OSB for test mode (available in OSB Back Office).'), default=constants.OSB_PARAMS.get('KEY_TEST'), readonly=constants.OSB_PLUGIN_FEATURES.get('qualif'))
    osb_key_prod = fields.Char(string=_('Key in production mode'), help=_('Key provided by OSB (available in OSB Back Office after enabling production mode).'), default=constants.OSB_PARAMS.get('KEY_PROD'))
    osb_sign_algo = fields.Selection(string=_('Signature algorithm'), help=sign_algo_help, selection=[('SHA-1', 'SHA-1'), ('SHA-256', 'HMAC-SHA-256')], default=constants.OSB_PARAMS.get('SIGN_ALGO'))
    osb_notify_url = fields.Char(string=_('Instant Payment Notification URL'), help=_('URL to copy into your OSB Back Office > Settings > Notification rules.'), default=_get_notify_url, readonly=True)
    osb_gateway_url = fields.Char(string=_('Payment page URL'), help=_('Link to the payment page.'), default=constants.OSB_PARAMS.get('GATEWAY_URL'))
    osb_language = fields.Selection(string=_('Default language'), help=_('Default language on the payment page.'), default=constants.OSB_PARAMS.get('LANGUAGE'), selection=_get_languages)
    osb_available_languages = fields.Many2many('osb.language', string=_('Available languages'), column1='code', column2='label', help=_('Languages available on the payment page. If you do not select any, all the supported languages will be available.'))
    osb_capture_delay = fields.Char(string=_('Capture delay'), help=_('The number of days before the bank capture (adjustable in your OSB Back Office).'))
    osb_validation_mode = fields.Selection(string=_('Validation mode'), help=_('If manual is selected, you will have to confirm payments manually in your OSB Back Office.'), selection=[('-1', _('OSB Back Office Configuration')), ('0', _('Automatic')), ('1', _('Manual'))])
    osb_payment_cards = fields.Many2many('osb.card', string=_('Card types'), column1='code', column2='label', help=_('The card type(s) that can be used for the payment. Select none to use gateway configuration.'))
    osb_threeds_min_amount = fields.Char(string=_('Manage 3DS'), help=_('Amount below which customer could be exempt from strong authentication. Needs subscription to «Selective 3DS1» or «Frictionless 3DS2» options. For more information, refer to the module documentation.'))
    osb_redirect_enabled = fields.Selection(string=_('Automatic redirection'), help=_('If enabled, the buyer is automatically redirected to your site at the end of the payment.'), selection=[('0', _('Disabled')), ('1', _('Enabled'))])
    osb_redirect_success_timeout = fields.Char(string=_('Redirection timeout on success'), help=_('Time in seconds (0-300) before the buyer is automatically redirected to your website after a successful payment.'))
    osb_redirect_success_message = fields.Char(string=_('Redirection message on success'), help=_('Message displayed on the payment page prior to redirection after a successful payment.'), default=_('Redirection to shop in a few seconds...'))
    osb_redirect_error_timeout = fields.Char(string=_('Redirection timeout on failure'), help=_('Time in seconds (0-300) before the buyer is automatically redirected to your website after a declined payment.'))
    osb_redirect_error_message = fields.Char(string=_('Redirection message on failure'), help=_('Message displayed on the payment page prior to redirection after a declined payment.'), default=_('Redirection to shop in a few seconds...'))
    osb_return_mode = fields.Selection(string=_('Return mode'), help=_('Method that will be used for transmitting the payment result from the payment page to your shop.'), selection=[('GET', 'GET'), ('POST', 'POST')])
    osb_multi_warning = fields.Boolean(compute='_osb_compute_multi_warning')

    osb_multi_count = fields.Char(string=_('Count'), help=_('Installments number'))
    osb_multi_period = fields.Char(string=_('Period'), help=_('Delay (in days) between installments.'))
    osb_multi_first = fields.Char(string=_('1st installment'), help=_('Amount of first installment, in percentage of total amount. If empty, all installments will have the same amount.'))

    image = fields.Char()
    environment = fields.Char()

    osb_redirect = False

    @api.model
    def _get_compatible_acquirers(self, *args, currency_id=None, **kwargs):
        """ Override of payment to unlist OSB acquirers when the currency is not supported. """
        acquirers = super()._get_compatible_acquirers(*args, currency_id=currency_id, **kwargs)

        currency = self.env['res.currency'].browse(currency_id).exists()
        if currency and tools.find_currency(currency.name) is None:
            acquirers = acquirers.filtered(
                lambda a: a.provider not in ['osb', 'osbmulti']
            )

        return acquirers

    @api.model
    def multi_add(self, filename):
        if (constants.OSB_PLUGIN_FEATURES.get('multi') == True):
            file = path.join(path.dirname(path.dirname(path.abspath(__file__)))) + filename
            convert_xml_import(self._cr, 'payment_osb', file)

        return None

    def _get_ctx_mode(self):
        ctx_key = self.state
        ctx_value = 'TEST' if ctx_key == 'test' else 'PRODUCTION'

        return ctx_value

    def _osb_generate_sign(self, acquirer, values):
        key = self.osb_key_prod if self._get_ctx_mode() == 'PRODUCTION' else self.osb_key_test

        sign = ''
        for k in sorted(values.keys()):
            if k.startswith('vads_'):
                sign += values[k] + '+'

        sign += key

        if self.osb_sign_algo == 'SHA-1':
            shasign = sha1(sign.encode('utf-8')).hexdigest()
        else:
            shasign = base64.b64encode(hmac.new(key.encode('utf-8'), sign.encode('utf-8'), sha256).digest()).decode('utf-8')

        return shasign

    def _get_payment_config(self, amount):
        if self.provider == 'osbmulti':
            if (self.osb_multi_first):
                first = int(float(self.osb_multi_first) / 100 * int(amount))
            else:
                first = int(float(amount) / float(self.osb_multi_count))

            payment_config = u'MULTI:first=' + str(first) + u';count=' + self.osb_multi_count + u';period=' + self.osb_multi_period
        else:
            payment_config = u'SINGLE'

        return payment_config

    def osb_form_generate_values(self, values):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        # trans_id is the number of 1/10 seconds from midnight.
        now = datetime.now()
        midnight = now.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
        delta = int((now - midnight).total_seconds() * 10)
        trans_id = str(delta).rjust(6, '0')

        threeds_mpi = u''
        if self.osb_threeds_min_amount and float(self.osb_threeds_min_amount) > values['amount']:
            threeds_mpi = u'2'

        # Check currency.
        if 'currency' in values:
            currency = values['currency']
        else:
            currency = self.env['res.currency'].browse(values['currency_id']).exists()

        currency_num = tools.find_currency(currency.name)
        if currency_num is None:
            _logger.error('The plugin cannot find a numeric code for the current shop currency {}.'.format(currency.name))
            raise ValidationError(_('The shop currency {} is not supported.').format(currency.name))

        # Amount in cents.
        k = int(currency.decimal_places)
        amount = int(float_round(float_round(values['amount'], k) * (10 ** k), 0))

        # List of available languages.
        available_languages = ''
        for value in self.osb_available_languages:
            available_languages += value.code + ';'

        # List of available payment cards.
        payment_cards = ''
        for value in self.osb_payment_cards:
            payment_cards += value.code + ';'

        # Validation mode.
        validation_mode = self.osb_validation_mode if self.osb_validation_mode != '-1' else ''

        # Enable redirection?
        AcquirerOsb.osb_redirect = True if str(self.osb_redirect_enabled) == '1' else False

        order_id = re.sub("[^0-9a-zA-Z_-]+", "", values.get('reference'))

        tx_values = dict() # Values to sign in unicode.
        tx_values.update({
            'vads_site_id': self.osb_site_id,
            'vads_amount': str(amount),
            'vads_currency': currency_num,
            'vads_trans_date': str(datetime.utcnow().strftime("%Y%m%d%H%M%S")),
            'vads_trans_id': str(trans_id),
            'vads_ctx_mode': str(self._get_ctx_mode()),
            'vads_page_action': u'PAYMENT',
            'vads_action_mode': u'INTERACTIVE',
            'vads_payment_config': self._get_payment_config(amount),
            'vads_version': constants.OSB_PARAMS.get('GATEWAY_VERSION'),
            'vads_url_return': urlparse.urljoin(base_url, OsbController._return_url),
            'vads_order_id': str(order_id),
            'vads_ext_info_order_ref': str(values.get('reference')),
            'vads_contrib': constants.OSB_PARAMS.get('CMS_IDENTIFIER') + u'_' + constants.OSB_PARAMS.get('PLUGIN_VERSION') + u'/' + release.version,

            'vads_language': self.osb_language or '',
            'vads_available_languages': available_languages,
            'vads_capture_delay': self.osb_capture_delay or '',
            'vads_validation_mode': validation_mode,
            'vads_payment_cards': payment_cards,
            'vads_return_mode': str(self.osb_return_mode),
            'vads_threeds_mpi': threeds_mpi
        })

        if AcquirerOsb.osb_redirect:
            tx_values.update({
                'vads_redirect_success_timeout': self.osb_redirect_success_timeout or '',
                'vads_redirect_success_message': self.osb_redirect_success_message or '',
                'vads_redirect_error_timeout': self.osb_redirect_error_timeout or '',
                'vads_redirect_error_message': self.osb_redirect_error_message or ''
            })

        osb_tx_values = dict() # Values encoded in UTF-8.

        for key in tx_values.keys():
            if tx_values[key] == ' ':
                tx_values[key] = ''

            osb_tx_values[key] = tx_values[key].encode('utf-8')

        return osb_tx_values

    def osb_get_form_action_url(self):
        return self.osb_gateway_url

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'osb' and self.provider != 'osbmulti':
            return super()._get_default_payment_method_id()

        if self.provider == 'osb':
            return self.env.ref('payment_osb.payment_method_osb').id
        if self.provider == 'osbmulti':
            return self.env.ref('payment_osb.payment_method_osbmulti').id
