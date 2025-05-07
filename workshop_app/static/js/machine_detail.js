// Machine Detail JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Handle Start Using Machine button
    const startUsingForm = document.getElementById('startUsageForm');
    if (startUsingForm) {
        const startButton = startUsingForm.closest('.modal-content').querySelector('.modal-footer .btn-primary');
        if (startButton) {
            startButton.addEventListener('click', function(event) {
                event.preventDefault();
                
                // Get machine ID from URL or data attribute
                const machineId = document.querySelector('[data-machine-id]').getAttribute('data-machine-id');
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
                
                // Send AJAX request
                fetch(`/machines/${machineId}/start-usage/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken
                    },
                    body: `setup_time=${encodeURIComponent(setupTime)}&estimated_usage=${encodeURIComponent(estimatedUsage)}&notes=${encodeURIComponent(notes)}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Close the modal
                        const modal = bootstrap.Modal.getInstance(document.getElementById('startUsageModal'));
                        modal.hide();
                        
                        // Show success message
                        const alertDiv = document.createElement('div');
                        alertDiv.className = 'alert alert-success alert-dismissible fade show';
                        alertDiv.innerHTML = `
                            <strong>Success!</strong> ${data.message}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        `;
                        document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
                        
                        // Update machine status display
                        const statusBadge = document.querySelector('.card-header .badge');
                        if (statusBadge) {
                            statusBadge.className = 'badge bg-light text-warning';
                            statusBadge.textContent = 'In Use';
                        }
                        
                        // Update machine card
                        const machineCard = document.querySelector('.card.mb-4');
                        if (machineCard) {
                            machineCard.className = machineCard.className.replace(/border-\w+/, 'border-warning');
                            document.querySelector('.card-header').className = 
                                document.querySelector('.card-header').className.replace(/bg-\w+/, 'bg-warning');
                        }
                        
                        // Update button
                        const actionButton = document.querySelector('.machine-actions .btn-success');
                        if (actionButton) {
                            actionButton.className = 'btn btn-danger';
                            actionButton.textContent = 'Stop Using Machine';
                            actionButton.setAttribute('data-bs-target', '#stopUsageModal');
                        }
                        
                        // Auto dismiss alert after 5 seconds
                        setTimeout(() => {
                            alertDiv.remove();
                        }, 5000);
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
    }
    
    // Handle Stop Using Machine button
    const stopUsingForm = document.getElementById('stopUsageForm');
    if (stopUsingForm) {
        const stopButton = stopUsingForm.closest('.modal-content').querySelector('.modal-footer .btn-danger');
        if (stopButton) {
            stopButton.addEventListener('click', function(event) {
                event.preventDefault();
                
                // Get machine ID from URL or data attribute
                const machineId = document.querySelector('[data-machine-id]').getAttribute('data-machine-id');
                const cleanupTime = document.getElementById('cleanupTime').value;
                const notes = document.getElementById('stopUsageNotes').value;
                
                // Validate inputs
                if (!cleanupTime) {
                    alert('Please fill in all required fields');
                    return;
                }
                
                // Get CSRF token
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                // Send AJAX request
                fetch(`/machines/${machineId}/stop-usage/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken
                    },
                    body: `cleanup_time=${encodeURIComponent(cleanupTime)}&notes=${encodeURIComponent(notes)}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Close the modal
                        const modal = bootstrap.Modal.getInstance(document.getElementById('stopUsageModal'));
                        modal.hide();
                        
                        // Show success message
                        const alertDiv = document.createElement('div');
                        alertDiv.className = 'alert alert-success alert-dismissible fade show';
                        alertDiv.innerHTML = `
                            <strong>Success!</strong> ${data.message}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        `;
                        document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
                        
                        // Update machine status display
                        const statusBadge = document.querySelector('.card-header .badge');
                        if (statusBadge) {
                            statusBadge.className = 'badge bg-light text-success';
                            statusBadge.textContent = 'Available';
                        }
                        
                        // Update machine card
                        const machineCard = document.querySelector('.card.mb-4');
                        if (machineCard) {
                            machineCard.className = machineCard.className.replace(/border-\w+/, 'border-success');
                            document.querySelector('.card-header').className = 
                                document.querySelector('.card-header').className.replace(/bg-\w+/, 'bg-success text-white');
                        }
                        
                        // Update button
                        const actionButton = document.querySelector('.machine-actions .btn-danger');
                        if (actionButton) {
                            actionButton.className = 'btn btn-success';
                            actionButton.textContent = 'Start Using Machine';
                            actionButton.setAttribute('data-bs-target', '#startUsageModal');
                        }
                        
                        // Auto dismiss alert after 5 seconds
                        setTimeout(() => {
                            alertDiv.remove();
                        }, 5000);
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
    }
});
