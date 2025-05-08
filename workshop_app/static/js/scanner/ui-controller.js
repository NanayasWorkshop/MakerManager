/**
 * UI Controller Module
 * Handles UI updates and user interactions
 */

/**
 * Update the loading element to show current status
 * @param {HTMLElement} loadingElement - The loading indicator element
 * @param {string} status - Status message to display
 * @param {boolean} isError - Whether this is an error message
 */
function updateLoadingStatus(loadingElement, status, isError = false) {
    if (isError) {
        loadingElement.innerHTML = `
            <div class="alert alert-danger">
                <p><strong>Error</strong></p>
                <p>${status}</p>
                <button class="btn btn-primary mt-2" id="tryScanAgainButton">Try Again</button>
                <a href="#" class="btn btn-outline-secondary mt-2" id="showManualEntryButton">Enter Manually</a>
            </div>
        `;
    } else {
        loadingElement.innerHTML = `
            <div class="${isError ? 'alert alert-danger' : ''}">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">${status}</p>
            </div>
        `;
    }
}

/**
 * Update the scanner status display
 * @param {HTMLElement} statusElement - The status element to update
 * @param {string} message - Message to display
 */
function updateScannerStatus(statusElement, message) {
    if (!statusElement) return;
    statusElement.textContent = message;
}

/**
 * Show a scan result in the modal
 * @param {Object} data - The scan result data
 * @param {bootstrap.Modal} resultModal - Bootstrap modal instance
 */
function showScanResultModal(data, resultModal) {
    // Get type-specific details
    let typeText, badgeClass;
    
    if (data.type === 'job') {
        typeText = 'Job';
        badgeClass = 'bg-primary';
    } else if (data.type === 'material') {
        typeText = 'Material';
        badgeClass = 'bg-success';
    } else if (data.type === 'machine') {
        typeText = 'Machine';
        badgeClass = 'bg-warning text-dark';
    } else {
        typeText = 'Item';
        badgeClass = 'bg-secondary';
    }
    
    // Update modal content
    document.getElementById('scanResultTitle').textContent = `${typeText} Detected`;
    
    document.getElementById('scanResultBody').innerHTML = `
        <div class="text-center mb-3">
            <span class="badge ${badgeClass} fs-6 mb-2">${typeText}</span>
            <h4>${data.name}</h4>
            <p class="text-muted">${data.id}</p>
        </div>
        
        <div class="d-flex justify-content-center">
            <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <span>Loading details...</span>
        </div>
    `;
    
    // Set action button link
    const actionButton = document.getElementById('scanResultAction');
    actionButton.href = data.redirect_url;
    actionButton.textContent = `View ${typeText} Details`;
    
    // Show the modal
    resultModal.show();
}

/**
 * Show an error message when scan processing fails
 * @param {string} errorMessage - The error message to display
 * @param {HTMLElement} loadingElement - Element to display the error in
 * @param {Function} onTryAgain - Callback for try again button
 * @param {HTMLElement} manualEntryForm - Form for manual entry
 */
function showScanError(errorMessage, loadingElement, onTryAgain, manualEntryForm) {
    loadingElement.innerHTML = `
        <div class="alert alert-danger">
            <p><strong>Scan Error</strong></p>
            <p>${errorMessage}</p>
            <button class="btn btn-primary mt-2" id="tryScanAgainButton">Try Again</button>
            <a href="#" class="btn btn-outline-secondary mt-2" id="showManualEntryButton">Enter Manually</a>
        </div>
    `;
    
    document.getElementById('tryScanAgainButton').addEventListener('click', onTryAgain);
    document.getElementById('showManualEntryButton').addEventListener('click', function(e) {
        e.preventDefault();
        manualEntryForm.classList.remove('d-none');
        document.getElementById('item_id').focus();
    });
}

/**
 * Reset the UI for scanning
 * @param {HTMLElement} videoElement - Video element
 * @param {HTMLElement} overlayElement - Scanner overlay element
 * @param {HTMLElement} loadingElement - Loading indicator element
 * @param {HTMLButtonElement} startButton - Start scanning button
 * @param {HTMLButtonElement} stopButton - Stop scanning button
 */
function resetScannerUI(videoElement, overlayElement, loadingElement, startButton, stopButton) {
    videoElement.classList.add('d-none');
    overlayElement.classList.add('d-none');
    loadingElement.classList.remove('d-none');
    startButton.disabled = false;
    stopButton.disabled = true;
    
    loadingElement.innerHTML = `
        <p class="mt-2">Scanner stopped</p>
        <button class="btn btn-primary" id="restartScanButton">Restart Scanner</button>
    `;
}

export {
    updateLoadingStatus,
    updateScannerStatus,
    showScanResultModal,
    showScanError,
    resetScannerUI
};
