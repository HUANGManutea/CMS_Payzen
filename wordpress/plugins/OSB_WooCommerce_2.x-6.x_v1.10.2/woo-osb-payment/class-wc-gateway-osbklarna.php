<?php
/**
 * Copyright © Lyra Network and contributors.
 * This file is part of OSB plugin for WooCommerce. See COPYING.md for license details.
 *
 * @author    Lyra Network (https://www.lyra.com/)
 * @author    Geoffrey Crofte, Alsacréations (https://www.alsacreations.fr/)
 * @copyright Lyra Network and contributors
 * @license   http://www.gnu.org/licenses/old-licenses/gpl-2.0.html GNU General Public License (GPL v2)
 */

if (! defined('ABSPATH')) {
    exit; // Exit if accessed directly.
}

class WC_Gateway_OsbKlarna extends WC_Gateway_OsbStd
{
    protected $osb_countries = array('AT', 'DE', 'DK', 'FI', 'NL', 'NO', 'SE');

    public function __construct()
    {
        $this->id = 'osbklarna';
        $this->icon = apply_filters('woocommerce_osbklarna_icon', WC_OSB_PLUGIN_URL . 'assets/images/klarna.png');
        $this->has_fields = true;
        $this->method_title = self::GATEWAY_NAME . ' - ' . __('Klarna payment', 'woo-osb-payment');

        // Init common vars.
        $this->osb_init();

        // Load the form fields.
        $this->init_form_fields();

        // Load the module settings.
        $this->init_settings();

        // Define user set variables.
        $this->title = $this->get_title();
        $this->description = $this->get_description();
        $this->testmode = ($this->get_general_option('ctx_mode') == 'TEST');
        $this->debug = ($this->get_general_option('debug') == 'yes') ? true : false;

        if ($this->osb_is_section_loaded()) {
            // Reset klarna payment admin form action.
            add_action('woocommerce_settings_start', array($this, 'osb_reset_admin_options'));

            // Update klarna payment admin form action.
            add_action('woocommerce_update_options_payment_gateways_' . $this->id, array($this, 'process_admin_options'));

            // Adding style to admin form action.
            add_action('admin_head-woocommerce_page_' . $this->admin_page, array($this, 'osb_admin_head_style'));

            // Adding JS to admin form action.
            add_action('admin_head-woocommerce_page_' . $this->admin_page, array($this, 'osb_admin_head_script'));
        }

        // Generate klarna payment form action.
        add_action('woocommerce_receipt_' . $this->id, array($this, 'osb_generate_form'));
    }

    /**
     * Initialise gateway settings form fields.
     */
    public function init_form_fields()
    {
        parent::init_form_fields();

        unset($this->form_fields['validation_mode']);
        unset($this->form_fields['payment_cards']);
        unset($this->form_fields['advanced_options']);
        unset($this->form_fields['card_data_mode']);
        unset($this->form_fields['payment_by_token']);

        $this->form_fields['capture_delay']['default'] = 0;
        $this->form_fields['capture_delay']['description'] = __('The number of days before the bank capture. Should be between 0 and 7.', 'woo-osb-payment');

        // By default, disable Klarna payment submodule.
        $this->form_fields['enabled']['default'] = 'no';
        $this->form_fields['enabled']['description'] = __('Enables / disables Klarna payment.', 'woo-osb-payment');

        $this->form_fields['title']['default'] = __('Payment with Klarna', 'woo-osb-payment');

        // If WooCommecre Multilingual is not available (or installed version not allow gateways UI translation).
        // Let's suggest our translation feature.
        if (! class_exists('WCML_WC_Gateways')) {
            $this->form_fields['title']['default'] = array(
                'en_US' => 'Payment with Klarna',
                'en_GB' => 'Payment with Klarna',
                'fr_FR' => 'Paiement avec Klarna',
                'de_DE' => 'Zahlung mit Klarna',
                'es_ES' => 'Pago con Klarna',
                'pt_BR' => 'Pagamento com Klarna'
            );
        }
    }

    protected function get_rest_fields()
    {
        // REST API fields are not available for this payment.
    }

    public function validate_capture_delay_field($key, $value = null)
    {
        $new_value = parent::validate_text_field($key, $value);

        if (! is_numeric($new_value) || ($new_value < 0) || ($value > 7)) {
            return $this->get_option($key); // Restore old value.
        }

        return $new_value;
    }

    /**
     * Prepare form params to send to payment gateway.
     **/
    protected function osb_fill_request($order)
    {
        parent::osb_fill_request($order);

        $this->send_cart_data($order);

        // Specific fields for klarna payment.
        $this->osb_request->set('payment_cards', 'KLARNA');
        $this->osb_request->set('validation_mode', '1');
    }
}
