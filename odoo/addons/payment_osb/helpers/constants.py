# coding: utf-8
#
# Copyright © Lyra Network.
# This file is part of OSB plugin for Odoo. See COPYING.md for license details.
#
# Author:    Lyra Network (https://www.lyra.com)
# Copyright: Copyright © Lyra Network
# License:   http://www.gnu.org/licenses/agpl.html GNU Affero General Public License (AGPL v3)

from odoo import _

# WARN: Do not modify code format here. This is managed by build files.
OSB_PLUGIN_FEATURES = {
    'multi': True,
    'restrictmulti': False,
    'qualif': False,
    'shatwo': True,
}

OSB_PARAMS = {
    'GATEWAY_CODE': 'OSB',
    'GATEWAY_NAME': 'OSB',
    'BACKOFFICE_NAME': 'OSB',
    'SUPPORT_EMAIL': 'support@osb.pf',
    'GATEWAY_URL': 'https://secure.osb.pf/vads-payment/',
    'SITE_ID': '12345678',
    'KEY_TEST': '1111111111111111',
    'KEY_PROD': '2222222222222222',
    'CTX_MODE': 'TEST',
    'SIGN_ALGO': 'SHA-256',
    'LANGUAGE': 'fr',

    'GATEWAY_VERSION': 'V2',
    'PLUGIN_VERSION': '2.0.3',
    'CMS_IDENTIFIER': 'Odoo_15',
}

OSB_LANGUAGES = {
    'cn': 'Chinese',
    'de': 'German',
    'es': 'Spanish',
    'en': 'English',
    'fr': 'French',
    'it': 'Italian',
    'jp': 'Japanese',
    'nl': 'Dutch',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'sv': 'Swedish',
    'tr': 'Turkish',
}

OSB_CARDS = {
            'CB': u'CB',
    'E-CARTEBLEUE': u'e-Carte Bleue',
    'MAESTRO': u'Maestro',
    'MASTERCARD': u'Mastercard',
            'VISA': u'Visa',
    'VISA_ELECTRON': u'Visa Electron',
    'VPAY': u'V PAY',
    'AMEX': u'American Express',
            'APETIZ': u'Apetiz',
    'BANCONTACT': u'Bancontact Mistercash',
    'CA_DO_CARTE': u'CA DO Carte',
            'CHQ_DEJ': u'Chèque Déjeuner',
    'DINERS': u'Diners',
    'DISCOVER': u'Discover',
    'EDENRED': u'Ticket Restaurant',
            'GOOGLEPAY': u'Google Pay',
    'JCB': u'JCB',
    'PAYPAL': u'PayPal',
    'PAYPAL_SB': u'PayPal Sandbox',
            'PRV_BDP': u'Banque de Polynésie',
    'PRV_BDT': u'Banque de Tahiti',
    'PRV_OPT': u'OPT',
            'PRV_SMART_CARD': u'Smart Card',
    'PRV_SOC': u'Banque Socredo',
    'PRV_SOC_GOLD': u'Banque Socredo Gold',
            'PRV_SOC_VERTE': u'Banque Socredo Verte',
    'SODEXO': u'Pass Restaurant',
}

OSB_CURRENCIES = [
            ['AUD', '036', 2],
    ['CNY', '156', 2],
    ['DJF', '262', 0],
    ['EUR', '978', 2],
            ['FJD', '242', 2],
    ['GBP', '826', 2],
    ['HKD', '344', 2],
    ['JPY', '392', 0],
            ['KHR', '116', 0],
    ['LAK', '418', 0],
    ['NZD', '554', 2],
    ['SBD', '090', 2],
            ['THB', '764', 2],
    ['USD', '840', 2],
    ['VUV', '548', 0],
    ['XPF', '953', 0],
]
