# coding: utf-8
#
# Copyright © Lyra Network.
# This file is part of OSB plugin for Odoo. See COPYING.md for license details.
#
# Author:    Lyra Network (https://www.lyra.com)
# Copyright: Copyright © Lyra Network
# License:   http://www.gnu.org/licenses/agpl.html GNU Affero General Public License (AGPL v3)

import logging
import pprint

from pkg_resources import parse_version
import werkzeug

from odoo import http, release
from odoo.http import request

_logger = logging.getLogger(__name__)

class OsbController(http.Controller):
    _notify_url = '/payment/osb/ipn'
    _return_url = '/payment/osb/return'

    def _get_return_url(self, result, **post):
        return_url = post.pop('return_url', '')

        if not return_url:
            return_url = '/payment/process' if result else '/shop/cart'

        return return_url

    @http.route('/payment/osb/return', type='http', auth='public', methods=['POST', 'GET'], csrf=False)
    def osb_return(self, **post):
        # Check payment result and create transaction.
        _logger.info('OSB: entering _handle_feedback with post data %s', pprint.pformat(post))
        request.env['payment.transaction'].sudo()._handle_feedback_data('osb', post)
        return request.redirect('/payment/status')

    @http.route('/payment/osb/ipn', type='http', auth='public', methods=['POST'], csrf=False)
    def osb_ipn(self, **post):
        # Check payment result and create transaction.
        _logger.info('OSB: entering IPN _handle_feedback with post data %s', pprint.pformat(post))
        result = request.env['payment.transaction'].sudo()._handle_feedback_data('osb', post)

        return 'Accepted payment, order has been updated.' if result else 'Payment failure, order has been cancelled.'
