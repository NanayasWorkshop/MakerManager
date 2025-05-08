/**
 * Machine Detail JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Setup QR code button
    setupQRCodeButton();
    
    // Handle Start Using Machine button
    setupStartUsageForm();
    
    // Handle Stop Using Machine button
    setupStopUsageForm();
});

// Initialize tooltips
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Setup the QR code button functionality
function setupQRCodeButton() {
    const qrCodeButton = document.getElementById('qrCodeButton');
    if (!qrCodeButton) return;
    
    qrCodeButton.addEventListener('click', function(event) {
        event.preventDefault();
        
        // Get machine ID from data attribute
        const machineId = document.querySelector('[data-machine-id]').getAttribute('data-machine-id');
        
        // Fetch QR code using API utility
        fetch(`/machines/${machineId}/qr-code/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Create modal to display QR code
                    const modalHtml = `
                        <div class="modal fade" id="qrCodeModal" tabindex="-1" aria-hidden="true">
                            <div class="modal-dialog">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h5 class="modal-title">QR Code for ${data.machine_name}</h5>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                    </div>
                                    <div class="modal-body text-center">
                                        <img src="${data.qr_code_url}" alt="QR Code" class="img-fluid">
                                        <p class="mt-2">Machine ID: ${machineId}</p>
                                        <p class="mt-2">Scan this code to quickly access this machine.</p>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                        <a href="${data.qr_code_url}" download="qrcode-${machineId}.png" class="btn btn-primary">Download</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    // Add modal to body
                    document.body.insertAdjacentHTML('beforeend', modalHtml);
                    
                    // Show modal
                    const modal = new bootstrap.Modal(document.getElementById('qrCodeModal'));
                    modal.show();
                    
                    // Remove modal from DOM when hidden
                    document.getElementById('qrCodeModal').addEventListener('hidden.bs.modal', function() {
                        this.remove();
                    });
                } else {
                    alert('Error: ' + (data.error || 'Failed to get QR code'));
                }
            })
            .catch(error => {
                console.error('Error getting QR code:', error);
                alert('An error occurred while getting the QR code.');
            });
    });
}

// Setup the start usage form
function setupStartUsageForm() {
    const startUsageForm = document.getElementById('startUsageForm');
    if (!startUsageForm) return;
    
    startUsageForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Get form data
        const formData = new FormData(startUsageForm);
        
        // Submit form via AJAX
        fetch(startUsageForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Close the modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('startUsageModal'));
                modal.hide();
                
                // Show success message
                showAlert('success', data.message);
                
                // Update machine status display
                updateMachineStatus('in_use', 'warning');
                
                // Reload page after a delay
                setTimeout(function() {
                    window.location.reload();
                }, 2000);
            } else {
                // Show error message
                showAlert('danger', data.error);
            }
        })
        .catch(error => {
            console.error('Error starting machine usage:', error);
            showAlert('danger', 'An error occurred while starting machine usage.');
        });
    });
}

// Setup the stop usage form
function setupStopUsageForm() {
    const stopUsageForm = document.getElementById('stopUsageForm');
    if (!stopUsageForm) return;
    
    stopUsageForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Get form data
        const formData = new FormData(stopUsageForm);
        
        // Submit form via AJAX
        fetch(stopUsageForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Close the modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('stopUsageModal'));
                modal.hide();
                
                // Show success message
                showAlert('success', data.message);
                
                // Update machine status display
                updateMachineStatus('available', 'success');
                
                // Reload page after a delay
                setTimeout(function() {
                    window.location.reload();
                }, 2000);
            } else {
                // Show error message
                showAlert('danger', data.error);
            }
        })
        .catch(error => {
            console.error('Error stopping machine usage:', error);
            showAlert('danger', 'An error occurred while stopping machine usage.');
        });
    });
}

// Update machine status display after status change
function updateMachineStatus(newStatus, newColorClass) {
    // Update status badge
    const statusBadge = document.querySelector('.card-header .badge');
    if (statusBadge) {
        statusBadge.className = `badge bg-light text-${newColorClass}`;
        statusBadge.textContent = newStatus === 'available' ? 'Available' : 
                                 newStatus === 'in_use' ? 'In Use' : 
                                 newStatus === 'maintenance' ? 'Maintenance' : 'Out of Order';
    }
    
    // Update machine card
    const machineCard = document.querySelector('.card.mb-4');
    if (machineCard) {
        machineCard.className = machineCard.className.replace(/border-\w+/, `border-${newColorClass}`);
        document.querySelector('.card-header').className = 
            document.querySelector('.card-header').className.replace(/bg-\w+/, `bg-${newColorClass}`);
    }
    
    // Update action button
    if (newStatus === 'available') {
        const actionButton = document.querySelector('.machine-actions .btn-danger');
        if (actionButton) {
            actionButton.className = 'btn btn-success';
            actionButton.innerHTML = '<i class="bi bi-play-circle"></i> Start Using Machine';
            actionButton.setAttribute('data-bs-target', '#startUsageModal');
        }
    } else if (newStatus === 'in_use') {
        const actionButton = document.querySelector('.machine-actions .btn-success');
        if (actionButton) {
            actionButton.className = 'btn btn-danger';
            actionButton.innerHTML = '<i class="bi bi-stop-circle"></i> Stop Using Machine';
            actionButton.setAttribute('data-bs-target', '#stopUsageModal');
        }
    }
}

// Show alert message
function showAlert(type, message) {
    // Create alert element
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add alert to page
    const container = document.querySelector('.container');
    container.insertBefore(alertElement, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        const alert = bootstrap.Alert.getInstance(alertElement);
        if (alert) {
            alert.close();
        } else {
            alertElement.remove();
        }
    }, 5000);
}
