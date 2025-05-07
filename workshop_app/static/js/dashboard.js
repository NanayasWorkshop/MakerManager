// Dashboard JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Handle active job clear button
    const clearJobButton = document.querySelector('.card-header .btn-outline-light');
    if (clearJobButton) {
        clearJobButton.addEventListener('click', function(event) {
            if (confirm('Are you sure you want to clear the active job?')) {
                // Send AJAX request to clear active job
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
                        // If there's a personal job, it will be set as active
                        // Otherwise, the active job will be cleared
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
    
    // Start Timer button handler
    const startTimerButton = document.querySelector('.quick-actions .btn-success');
    if (startTimerButton) {
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
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                alert('Timer started for job: ' + data.job_name);
                                window.location.reload();
                            } else {
                                alert('Error: ' + data.error);
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
});
