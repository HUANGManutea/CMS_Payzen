/**
 * External dependencies
 */
import { decodeEntities } from '@wordpress/html-entities';
import { registerPaymentMethod } from '@woocommerce/blocks-registry';

/**
 * Internal dependencies
 */
import { getOsbServerData } from './osb-utils';

const PAYMENT_METHOD_NAME = 'osbstd';
var osb_data = getOsbServerData(PAYMENT_METHOD_NAME);

const Content = () => {
    return (osb_data?.description);
};

const Label = () => {
    const styles = {
        divWidth: {
            width: '95%'
        },
        imgFloat: {
            float: 'right'
        }
    }

    return (
        <div style={ styles.divWidth }>
            <span>{ osb_data?.title}</span>
            <img
                style={ styles.imgFloat }
                src={ osb_data?.logo_url + 'osb.png' }
                alt={ osb_data?.title }
            />
        </div>
    );
};

registerPaymentMethod( {
    name: PAYMENT_METHOD_NAME,
    label: <Label />,
    ariaLabel: 'Osb payment method',
    canMakePayment: () => true,
    content: <Content />,
    edit: <Content />,
    supports: {
        features: osb_data?.supports ?? [],
    },
} );
