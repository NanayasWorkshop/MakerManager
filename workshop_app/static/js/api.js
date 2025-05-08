/**
 * Workshop Management System - API Utilities
 * Functions for interacting with the server API
 */

// Get CSRF token
function getCSRFToken() {
    return document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
}

// Make an API request with CSRF token
async function apiRequest(url, method = 'GET', data = null, includeCSRF = true) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    };
    
    // Add CSRF token for non-GET requests
    if (method !== 'GET' && includeCSRF) {
        const csrfToken = getCSRFToken();
        if (csrfToken) {
            options.headers['X-CSRFToken'] = csrfToken;
        }
    }
    
    // Add body data for non-GET requests
    if (method !== 'GET' && data) {
        if (data instanceof FormData) {
            // Use FormData as is
            options.body = data;
            // Remove Content-Type to let browser set it with boundary
            delete options.headers['Content-Type'];
        } else if (typeof data === 'object') {
            // Convert object to URL-encoded string
            options.body = new URLSearchParams(data).toString();
        } else {
            // Use data as is
            options.body = data;
        }
    }
    
    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        
        // Try to parse JSON response
        try {
            return await response.json();
        } catch (e) {
            // If not JSON, return text
            return await response.text();
        }
    } catch (error) {
        console.error('API request error:', error);
        throw error;
    }
}

// GET request shorthand
async function getData(url) {
    return apiRequest(url, 'GET');
}

// POST request shorthand
async function postData(url, data, includeCSRF = true) {
    return apiRequest(url, 'POST', data, includeCSRF);
}

// Process a material transaction (withdraw/return/restock)
async function processMaterialTransaction(materialId, action, data) {
    return postData(`/materials/${materialId}/${action}/`, data);
}

// Get active job information
async function getActiveJob() {
    return getData('/api/active-job/');
}

// Export API utilities for use in other modules
window.WMSAPI = {
    getCSRFToken,
    apiRequest,
    getData,
    postData,
    processMaterialTransaction,
    getActiveJob
};
