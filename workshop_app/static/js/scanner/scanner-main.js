/**
 * Scanner Main Module
 * Core functionality integrating all scanner modules
 */

import { 
    initializeCamera, 
    stopCamera, 
    getVideoDimensions, 
    isCameraActive 
} from './camera-manager.js';

import { 
    detectCodeInFrame,
    highlightDetectedCode 
} from './code-detector.js';

import { 
    updateLoadingStatus, 
    updateScannerStatus, 
    showScanResultModal, 
    showScanError,
    resetScannerUI
} from './ui-controller.js';

import { 
    processScannedCode,
    withdrawMaterial,
    returnMaterial 
} from './api-client.js';

// Scanner state variables
let scanning = false;
let scanInterval = null;

/**
 * Initialize the scanner
 * @param {Object} elements - DOM elements
 * @param {string} csrfToken - CSRF token for API requests
 */
function initScanner(elements, csrfToken) {
    const { 
        video, 
        canvas, 
        loadingElement, 
        overlayElement, 
        startButton, 
        stopButton, 
        manualEntryLink,
        manualEntryForm
    } = elements;
    
    // Set up canvas
    const context = canvas.getContext('2d');
    
    // Event Listeners
    startButton.addEventListener('click', () => startScanning(elements, csrfToken));
    stopButton.addEventListener('click', () => stopScanning(elements));
    
    manualEntryLink.addEventListener('click', function(e) {
        e.preventDefault();
        manualEntryForm.classList.toggle('d-none');
        if (!manualEntryForm.classList.contains('d-none')) {
            document.getElementById('item_id').focus();
        }
    });
    
    // Set up material transaction forms if they exist
    setupMaterialForms(csrfToken);
}

/**
 * Start the scanning process
 * @param {Object} elements - DOM elements
 * @param {string} csrfToken - CSRF token for API requests
 */
async function startScanning(elements, csrfToken) {
    if (scanning) return;
    
    const { 
        video, 
        canvas, 
        loadingElement, 
        overlayElement, 
        startButton, 
        stopButton 
    } = elements;
    
    const cameraInitialized = await initializeCamera(video, loadingElement, overlayElement);
    if (!cameraInitialized) return;
    
    // Set canvas dimensions to match video
    const dimensions = getVideoDimensions(video);
    if (dimensions.width && dimensions.height) {
        canvas.width = dimensions.width;
        canvas.height = dimensions.height;
    }
    
    scanning = true;
    startButton.disabled = true;
    stopButton.disabled = false;
    
    // Start processing frames for QR codes
    scanInterval = setInterval(() => {
        processFrame(elements, csrfToken);
    }, 200);
}

/**
 * Stop scanning
 * @param {Object} elements - DOM elements
 */
function stopScanning(elements) {
    if (!scanning) return;
    
    const { 
        video, 
        overlayElement, 
        loadingElement, 
        startButton, 
        stopButton 
    } = elements;
    
    // Clear interval
    if (scanInterval) {
        clearInterval(scanInterval);
        scanInterval = null;
    }
    
    // Stop video stream
    stopCamera();
    
    // Reset UI
    resetScannerUI(video, overlayElement, loadingElement, startButton, stopButton);
    
    // Add restart button event listener
    document.getElementById('restartScanButton').addEventListener('click', () => {
        startScanning(elements, csrfToken);
    });
    
    scanning = false;
}

/**
 * Process a video frame to look for QR codes
 * @param {Object} elements - DOM elements
 * @param {string} csrfToken - CSRF token for API requests
 */
function processFrame(elements, csrfToken) {
    if (!scanning || !isCameraActive()) return;
    
    const { video, canvas } = elements;
    
    const code = detectCodeInFrame(video, canvas);
    
    if (code) {
        console.log("Code detected:", code.data);
        
        // Stop scanning
        stopScanning(elements);
        
        // Process the code
        handleDetectedCode(code.data, elements, csrfToken);
    }
}

/**
 * Process the detected code
 * @param {string} codeData - The detected code data
 * @param {Object} elements - DOM elements
 * @param {string} csrfToken - CSRF token for API requests
 */
async function handleDetectedCode(codeData, elements, csrfToken) {
    const { loadingElement, manualEntryForm } = elements;
    
    // Show loading indicator
    updateLoadingStatus(loadingElement, 'Processing code...');
    
    try {
        // Send to server for processing
        const data = await processScannedCode(codeData, csrfToken);
        
        if (data.success) {
            // Handle successful scan
            handleSuccessfulScan(data, elements);
        } else {
            // Handle scan error
            showScanError(
                data.error, 
                loadingElement, 
                () => startScanning(elements, csrfToken),
                manualEntryForm
            );
        }
    } catch (error) {
        showScanError(
            'An error occurred while processing the scan.', 
            loadingElement, 
            () => startScanning(elements, csrfToken),
            manualEntryForm
        );
    }
}

/**
 * Handle a successful scan
 * @param {Object} data - The scan result data
 * @param {Object} elements - DOM elements
 */
function handleSuccessfulScan(data, elements) {
    const resultModal = new bootstrap.Modal(document.getElementById('scanResultModal'));
    
    // Show result modal
    showScanResultModal(data, resultModal);
    
    // Automatically navigate after a short delay for a smoother experience
    setTimeout(() => {
        window.location.href = data.redirect_url;
    }, 1500);
}

/**
 * Set up material transaction forms
 * @param {string} csrfToken - CSRF token for API requests
 */
function setupMaterialForms(csrfToken) {
    // Handle withdraw form
    const withdrawForm = document.getElementById('withdrawForm');
    if (withdrawForm) {
        const withdrawButton = withdrawForm.closest('.modal-content').querySelector('.modal-footer .btn-primary');
        if (withdrawButton) {
            withdrawButton.addEventListener('click', async function(event) {
                event.preventDefault();
                
                const materialId = document.querySelector('[data-material-id]').getAttribute('data-material-id');
                const quantity = document.getElementById('withdrawQuantity').value;
                const notes = document.getElementById('withdrawNotes').value;
                
                // Validate inputs
                if (!quantity || parseFloat(quantity) <= 0) {
                    alert('Please enter a valid quantity greater than zero');
                    return;
                }
                
                try {
                    const data = await withdrawMaterial(materialId, quantity, notes, csrfToken);
                    
                    if (data.success) {
                        // Close the modal
                        const modal = bootstrap.Modal.getInstance(document.getElementById('withdrawModal'));
                        modal.hide();
                        
                        showSuccessMessage(data.message);
                    } else {
                        alert('Error: ' + data.error);
                    }
                } catch (error) {
                    alert('An error occurred while withdrawing the material.');
                }
            });
        }
    }
    
    // Handle return form
    const returnForm = document.getElementById('returnForm');
    if (returnForm) {
        const returnButton = returnForm.closest('.modal-content').querySelector('.modal-footer .btn-primary');
        if (returnButton) {
            returnButton.addEventListener('click', async function(event) {
                event.preventDefault();
                
                const materialId = document.querySelector('[data-material-id]').getAttribute('data-material-id');
                const quantity = document.getElementById('returnQuantity').value;
                const notes = document.getElementById('returnNotes').value;
                
                // Validate inputs
                if (!quantity || parseFloat(quantity) <= 0) {
                    alert('Please enter a valid quantity greater than zero');
                    return;
                }
                
                try {
                    const data = await returnMaterial(materialId, quantity, notes, csrfToken);
                    
                    if (data.success) {
                        // Close the modal
                        const modal = bootstrap.Modal.getInstance(document.getElementById('returnModal'));
                        modal.hide();
                        
                        showSuccessMessage(data.message);
                    } else {
                        alert('Error: ' + data.error);
                    }
                } catch (error) {
                    alert('An error occurred while returning the material.');
                }
            });
        }
    }
}

/**
 * Show a success message
 * @param {string} message - The message to display
 */
function showSuccessMessage(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show';
    alertDiv.innerHTML = `
        <strong>Success!</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
    
    // Auto dismiss alert after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

export { initScanner };
