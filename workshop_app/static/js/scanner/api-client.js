/**
 * API Client Module
 * Handles all API interactions with the server
 */

/**
 * Process a scanned code by sending it to the server
 * @param {string} code - The scanned code
 * @param {string} csrfToken - CSRF token for the request
 * @returns {Promise<Object>} - Server response
 */
async function processScannedCode(code, csrfToken) {
    try {
        const response = await fetch('/scan/process/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `code=${encodeURIComponent(code)}&scan_type=auto`
        });
        
        return await response.json();
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
 * @param {string} csrfToken - CSRF token for the request
 * @returns {Promise<Object>} - Server response
 */
async function withdrawMaterial(materialId, quantity, notes, csrfToken) {
    try {
        const response = await fetch(`/materials/${materialId}/withdraw/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `quantity=${encodeURIComponent(quantity)}&notes=${encodeURIComponent(notes)}`
        });
        
        return await response.json();
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
 * @param {string} csrfToken - CSRF token for the request
 * @returns {Promise<Object>} - Server response
 */
async function returnMaterial(materialId, quantity, notes, csrfToken) {
    try {
        const response = await fetch(`/materials/${materialId}/return/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `quantity=${encodeURIComponent(quantity)}&notes=${encodeURIComponent(notes)}`
        });
        
        return await response.json();
    } catch (error) {
        console.error('Error returning material:', error);
        throw new Error('An error occurred while returning the material.');
    }
}

export {
    processScannedCode,
    withdrawMaterial,
    returnMaterial
};
