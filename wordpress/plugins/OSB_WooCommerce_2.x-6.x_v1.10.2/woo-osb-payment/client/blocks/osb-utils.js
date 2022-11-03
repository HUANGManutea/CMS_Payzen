/**
 * External dependencies
 */
import { getSetting } from '@woocommerce/settings';

/**
 * Osb data comes form the server passed on a global object.
 */

export const getOsbServerData = (name) => {
    const osbServerData = getSetting( name + '_data', null );

    if ( ! osbServerData ) {
        throw new Error( 'Osb initialization data for ' + name + ' submodule is not available' );
    }

    return osbServerData;
};
