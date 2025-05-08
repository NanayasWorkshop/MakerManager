/**
 * Machine Detail Page JavaScript
 * Uses the utility modules for common functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle Start Using Machine button
    setupStartUsageForm();
    
    // Handle Stop Using Machine button
    setupStopUsageForm();
});

// Setup the start usage form
function setupStartUsageForm() {
    const startUsageForm = document.getElementById('startUsageForm');
    if (!startUsageForm) return;
    
    const startButton = startUsageForm.closest('.modal-content')?.querySelector('.modal-footer .btn-primary');
    if (!startButton) return;
    
    startButton.addEventListener('click', function(event) {
        event.preventDefault();
        
        // Get form data
        const machineId = document.querySelector('[data-machine-id]')?.getAttribute('data-machine-id');
        const setupTime = document.getElementById('setupTime').value;
        const estimatedUsage = document.getElementById('estimatedUsage').value;
        const notes = document.getElementById('usageNotes').value;
        
        // Validate inputs
        if (!setupTime || !estimatedUsage) {
            alert('Please fill in all required fields');
            return;
        }
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Send AJAX request using API utility
        const formData = {
            setup_time: setupTime,
            estimated_usage: estimatedUsage,
            notes: notes
        };
        
        WMSAPI.apiRequest(`/machines/${machineId}/start-usage/`, 'POST', formData)
            .then(data => {
                if (data.success) {
                    // Close the modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('startUsageModal'));
                    modal.hide();
                    
                    // Show success message
                    WMSUtils.showAlert(
                        document.querySelector('.container'),
                        'success',
                        data.message
                    );
                    
                    // Update machine status display
                    updateMachineStatus('in_use', 'warning');
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error starting machine usage:', error);
                alert('An error occurred while starting machine usage.');
            });
    });
}

// Setup the stop usage form
function setupStopUsageForm() {
    const stopUsageForm = document.getElementById('stopUsageForm');
    if (!stopUsageForm) return;
    
    const stopButton = stopUsageForm.closest('.modal-content')?.querySelector('.modal-footer .btn-danger');
    if (!stopButton) return;
    
    stopButton.addEventListener('click', function(event) {
        event.preventDefault();
        
        // Get form data
        const machineId = document.querySelector('[data-machine-id]')?.getAttribute('data-machine-id');
        const cleanupTime = document.getElementById('cleanupTime').value;
        const notes = document.getElementById('stopUsageNotes').value;
        
        // Validate inputs
        if (!cleanupTime) {
            alert('Please fill in all required fields');
            return;
        }
        
        // Send AJAX request using API utility
        const formData = {
            cleanup_time: cleanupTime,
            notes: notes
        };
        
        WMSAPI.apiRequest(`/machines/${machineId}/stop-usage/`, 'POST', formData)
            .then(data => {
                if (data.success) {
                    // Close the modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('stopUsageModal'));
                    modal.hide();
                    
                    // Show success message
                    WMSUtils.showAlert(
                        document.querySelector('.container'),
                        'success',
                        data.message
                    );
                    
                    // Update machine status display
                    updateMachineStatus('available', 'success');
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error stopping machine usage:', error);
                alert('An error occurred while stopping machine usage.');
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
            actionButton.textContent = 'Start Using Machine';
            actionButton.setAttribute('data-bs-target', '#startUsageModal');
        }
    } else if (newStatus === 'in_use') {
        const actionButton = document.querySelector('.machine-actions .btn-success');
        if (actionButton) {
            actionButton.className = 'btn btn-danger';
            actionButton.textContent = 'Stop Using Machine';
            actionButton.setAttribute('data-bs-target', '#stopUsageModal');
        }
    }
}
