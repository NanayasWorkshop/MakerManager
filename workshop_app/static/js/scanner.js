/**
 * Workshop Management System - Scanner Functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const video = document.getElementById('scanner-video');
    const canvas = document.getElementById('scanner-canvas');
    const loadingElement = document.getElementById('scanner-loading');
    const overlayElement = document.getElementById('scanner-overlay');
    const startButton = document.getElementById('startScanButton');
    const stopButton = document.getElementById('stopScanButton');
    const manualEntryLink = document.getElementById('manualEntryLink');
    const manualEntryForm = document.getElementById('manualEntryForm');
    
    // Scanner variables
    let scanning = false;
    let videoStream = null;
    let scanInterval = null;
    
    // Get CSRF token for AJAX requests
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // ---- Event Listeners ----
    
    // Start scanning button
    startButton.addEventListener('click', startScanning);
    
    // Stop scanning button
    stopButton.addEventListener('click', stopScanning);
    
    // Manual entry link
    manualEntryLink.addEventListener('click', function(e) {
        e.preventDefault();
        manualEntryForm.classList.toggle('d-none');
        if (!manualEntryForm.classList.contains('d-none')) {
            document.getElementById('item_id').focus();
        }
    });
    
    // ---- Functions ----
    
    // Initialize camera
    async function initCamera() {
        try {
            // Request camera access
            videoStream = await navigator.mediaDevices.getUserMedia({
                video: { 
                    facingMode: "environment",
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            });
            
            // Set video source
            video.srcObject = videoStream;
            
            // Show video when ready
            video.onloadedmetadata = function() {
                loadingElement.classList.add('d-none');
                video.classList.remove('d-none');
                overlayElement.classList.remove('d-none');
                video.play();
                
                // Setup canvas with same dimensions
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
            };
            
            return true;
        } catch (error) {
            console.error('Camera access error:', error);
            loadingElement.innerHTML = `
                <div class="alert alert-danger">
                    <p><strong>Camera access failed</strong></p>
                    <p>${error.message}</p>
                    <p>Please ensure you've granted camera permission and are using a supported browser.</p>
                </div>
            `;
            return false;
        }
    }
    
    // Start the scanning process
    async function startScanning() {
        if (scanning) return;
        
        const cameraInitialized = await initCamera();
        if (!cameraInitialized) return;
        
        scanning = true;
        startButton.disabled = true;
        stopButton.disabled = false;
        
        // Start processing frames for QR codes
        scanInterval = setInterval(processFrame, 200);
    }
    
    // Stop scanning
    function stopScanning() {
        if (!scanning) return;
        
        // Clear interval
        if (scanInterval) {
            clearInterval(scanInterval);
            scanInterval = null;
        }
        
        // Stop video stream
        if (videoStream) {
            videoStream.getTracks().forEach(track => track.stop());
            videoStream = null;
        }
        
        // Reset UI
        video.classList.add('d-none');
        overlayElement.classList.add('d-none');
        loadingElement.classList.remove('d-none');
        loadingElement.innerHTML = `
            <p class="mt-2">Scanner stopped</p>
            <button class="btn btn-primary" id="restartScanButton">Restart Scanner</button>
        `;
        
        document.getElementById('restartScanButton').addEventListener('click', startScanning);
        
        scanning = false;
        startButton.disabled = false;
        stopButton.disabled = true;
    }
    
    // Process a video frame to look for QR codes
    function processFrame() {
        if (!scanning || !videoStream) return;
        
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        
        // Use jsQR to detect QR codes
        const code = jsQR(imageData.data, imageData.width, imageData.height, {
            inversionAttempts: "dontInvert",
        });
        
        if (code) {
            console.log("Code detected:", code.data);
            
            // Stop scanning
            stopScanning();
            
            // Process the code
            processScannedCode(code.data);
        }
    }
    
    // Process the scanned code
    function processScannedCode(code) {
        // Show loading indicator
        loadingElement.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Processing code...</p>
        `;
        
        // Send to server for processing - always use auto detection
        fetch('/scan/process/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `code=${encodeURIComponent(code)}&scan_type=auto`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Handle successful scan
                handleSuccessfulScan(data);
            } else {
                // Handle scan error
                showScanError(data.error);
            }
        })
        .catch(error => {
            console.error('Error processing scan:', error);
            showScanError('An error occurred while processing the scan.');
        });
    }
    
    // Handle a successful scan
    function handleSuccessfulScan(data) {
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
        
        // Show result modal
        const resultModal = new bootstrap.Modal(document.getElementById('scanResultModal'));
        
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
        
        // Automatically navigate after a short delay for a smoother experience
        setTimeout(() => {
            window.location.href = data.redirect_url;
        }, 1500);
    }
    
    // Show an error message when scan processing fails
    function showScanError(errorMessage) {
        loadingElement.innerHTML = `
            <div class="alert alert-danger">
                <p><strong>Scan Error</strong></p>
                <p>${errorMessage}</p>
                <button class="btn btn-primary mt-2" id="tryScanAgainButton">Try Again</button>
                <a href="#" class="btn btn-outline-secondary mt-2" id="showManualEntryButton">Enter Manually</a>
            </div>
        `;
        
        document.getElementById('tryScanAgainButton').addEventListener('click', startScanning);
        document.getElementById('showManualEntryButton').addEventListener('click', function(e) {
            e.preventDefault();
            manualEntryForm.classList.remove('d-none');
            document.getElementById('item_id').focus();
        });
    }
    
    // Handle withdraw/return forms in scan result page
    const withdrawForm = document.getElementById('withdrawForm');
    if (withdrawForm) {
        const withdrawButton = withdrawForm.closest('.modal-content').querySelector('.modal-footer .btn-primary');
        if (withdrawButton) {
            withdrawButton.addEventListener('click', function(event) {
                event.preventDefault();
                
                const materialId = document.querySelector('[data-material-id]').getAttribute('data-material-id');
                const quantity = document.getElementById('withdrawQuantity').value;
                const notes = document.getElementById('withdrawNotes').value;
                
                // Validate inputs
                if (!quantity || parseFloat(quantity) <= 0) {
                    alert('Please enter a valid quantity greater than zero');
                    return;
                }
                
                // Send AJAX request
                fetch(`/materials/${materialId}/withdraw/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken
                    },
                    body: `quantity=${encodeURIComponent(quantity)}&notes=${encodeURIComponent(notes)}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Close the modal
                        const modal = bootstrap.Modal.getInstance(document.getElementById('withdrawModal'));
                        modal.hide();
                        
                        // Show success message
                        const alertDiv = document.createElement('div');
                        alertDiv.className = 'alert alert-success alert-dismissible fade show';
                        alertDiv.innerHTML = `
                            <strong>Success!</strong> ${data.message}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        `;
                        document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
                        
                        // Auto dismiss alert after 5 seconds
                        setTimeout(() => {
                            alertDiv.remove();
                        }, 5000);
                    } else {
                        alert('Error: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error withdrawing material:', error);
                    alert('An error occurred while withdrawing the material.');
                });
            });
        }
    }
    
    const returnForm = document.getElementById('returnForm');
    if (returnForm) {
        const returnButton = returnForm.closest('.modal-content').querySelector('.modal-footer .btn-primary');
        if (returnButton) {
            returnButton.addEventListener('click', function(event) {
                event.preventDefault();
                
                const materialId = document.querySelector('[data-material-id]').getAttribute('data-material-id');
                const quantity = document.getElementById('returnQuantity').value;
                const notes = document.getElementById('returnNotes').value;
                
                // Validate inputs
                if (!quantity || parseFloat(quantity) <= 0) {
                    alert('Please enter a valid quantity greater than zero');
                    return;
                }
                
                // Send AJAX request
                fetch(`/materials/${materialId}/return/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken
                    },
                    body: `quantity=${encodeURIComponent(quantity)}&notes=${encodeURIComponent(notes)}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Close the modal
                        const modal = bootstrap.Modal.getInstance(document.getElementById('returnModal'));
                        modal.hide();
                        
                        // Show success message
                        const alertDiv = document.createElement('div');
                        alertDiv.className = 'alert alert-success alert-dismissible fade show';
                        alertDiv.innerHTML = `
                            <strong>Success!</strong> ${data.message}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        `;
                        document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
                        
                        // Auto dismiss alert after 5 seconds
                        setTimeout(() => {
                            alertDiv.remove();
                        }, 5000);
                    } else {
                        alert('Error: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error returning material:', error);
                    alert('An error occurred while returning the material.');
                });
            });
        }
    }
});
