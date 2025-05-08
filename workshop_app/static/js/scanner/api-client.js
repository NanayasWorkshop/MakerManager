/**
 * API Client Module for Scanner
 * Uses the global utility modules for API interactions
 */

/**
 * Process a scanned code by sending it to the server
 * @param {string} code - The scanned code
 * @returns {Promise<Object>} - Server response
 */
async function processScannedCode(code) {
    try {
        return await WMSAPI.apiRequest('/scan/process/', 'POST', {
            code: code,
            scan_type: 'auto'
        });
    } catch (error) {
        console.error('Error processing scan:', error);
        throw new Error('An error occurred while processing the scan.');
    }
}

/**
 * Handle a withdrawal request
 * @param {string} materialId - Material ID
 * @param {number} quantity - Quantity to withdraw
 * @param {string} notes - Optional notes
 * @returns {Promise<Object>} - Server response
 */
async function withdrawMaterial(materialId, quantity, notes) {
    try {
        return await WMSAPI.apiRequest(`/materials/${materialId}/withdraw/`, 'POST', {
            quantity: quantity,
            notes: notes
        });
    } catch (error) {
        console.error('Error withdrawing material:', error);
        throw new Error('An error occurred while withdrawing the material.');
    }
}

/**
 * Handle a return request
 * @param {string} materialId - Material ID
 * @param {number} quantity - Quantity to return
 * @param {string} notes - Optional notes
 * @returns {Promise<Object>} - Server response
 */
async function returnMaterial(materialId, quantity, notes) {
    try {
        return await WMSAPI.apiRequest(`/materials/${materialId}/return/`, 'POST', {
            quantity: quantity,
            notes: notes
        });
    } catch (error) {
        console.error('Error returning material:', error);
        throw new Error('An error occurred while returning the material.');
    }
}

// Export scanner API functions
window.ScannerAPI = {
    processScannedCode,
    withdrawMaterial,
    returnMaterial
};
