/**
 * Dashboard JavaScript
 * Uses the utility modules for common functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Handle active job clear button
    setupClearJobButton();
    
    // Handle activate personal job button
    setupActivatePersonalJobButton();
    
    // Start Timer button handler
    setupStartTimerButton();
});

// Initialize tooltips
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Setup the clear job button
function setupClearJobButton() {
    const clearJobButton = document.querySelector('.card-header .btn-outline-light');
    if (!clearJobButton) return;
    
    clearJobButton.addEventListener('click', function(event) {
        event.preventDefault();
        if (confirm('Are you sure you want to clear the active job?')) {
            // Send AJAX request to clear active job using API utility
            fetch('/api/clear-active-job/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show different message based on whether a personal job was set
                    if (data.no_personal_job) {
                        alert('Active job cleared successfully.');
                    } else {
                        alert('Active job set to your personal job: ' + data.job_name);
                    }
                    window.location.reload();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error clearing active job:', error);
                alert('An error occurred while clearing the active job.');
            });
        }
    });
}

// Setup the activate personal job button
function setupActivatePersonalJobButton() {
    const activatePersonalJobBtn = document.getElementById('activatePersonalJobBtn');
    if (!activatePersonalJobBtn) return;
    
    activatePersonalJobBtn.addEventListener('click', function(event) {
        // Send AJAX request to clear active job (which sets personal job as active)
        fetch('/api/clear-active-job/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Personal job set as active: ' + data.job_name);
                window.location.reload();
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error activating personal job:', error);
            alert('An error occurred while activating personal job.');
        });
    });
}

// Setup the start timer button
function setupStartTimerButton() {
    const startTimerButton = document.querySelector('.quick-actions .btn-success');
    if (!startTimerButton) return;
    
    startTimerButton.addEventListener('click', function(event) {
        // Check if there's an active job
        fetch('/api/active-job/')
            .then(response => response.json())
            .then(data => {
                if (data.has_active_job) {
                    // Start timer for active job
                    fetch('/api/start-timer/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                        }
                    })
                    .then(timerData => timerData.json())
                    .then(timerData => {
                        if (timerData.success) {
                            alert('Timer started for job: ' + timerData.job_name);
                            window.location.reload();
                        } else {
                            alert('Error: ' + timerData.error);
                        }
                    })
                    .catch(error => {
                        console.error('Error starting timer:', error);
                        alert('An error occurred while starting the timer.');
                    });
                } else {
                    alert('No active job. Please activate a job first.');
                    window.location.href = '/scan/';
                }
            })
            .catch(error => {
                console.error('Error checking active job:', error);
                alert('An error occurred while checking active job.');
            });
    });
}
