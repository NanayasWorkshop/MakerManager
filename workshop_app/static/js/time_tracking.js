/**
 * Time Tracking JavaScript
 * Handles starting and stopping time tracking for jobs
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize time tracking buttons
    initTimeTrackingButtons();
    
    // If there's an active timer, update it periodically
    if (document.getElementById('stopTimerBtn')) {
        startElapsedTimeCounter();
    }
});

// Initialize time tracking buttons
function initTimeTrackingButtons() {
    const startTimerBtn = document.getElementById('startTimerBtn');
    const stopTimerBtn = document.getElementById('stopTimerBtn');
    
    if (startTimerBtn) {
        startTimerBtn.addEventListener('click', startTimer);
    }
    
    if (stopTimerBtn) {
        stopTimerBtn.addEventListener('click', stopTimer);
    }
}

// Start timer for active job
function startTimer() {
    // Get CSRF token
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    
    // Send request to start timer
    fetch('/api/start-timer/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: 'notes=Started from dashboard'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Swap buttons
            const startTimerBtn = document.getElementById('startTimerBtn');
            if (startTimerBtn) {
                // Replace the button with stop button
                const btnGroup = startTimerBtn.parentNode;
                startTimerBtn.remove();
                
                const newButton = document.createElement('button');
                newButton.className = 'btn btn-danger';
                newButton.id = 'stopTimerBtn';
                newButton.dataset.jobId = data.job_name;
                newButton.innerHTML = `<i class="bi bi-stop-circle"></i> Stop Time (0m 0s)`;
                newButton.addEventListener('click', stopTimer);
                
                btnGroup.prepend(newButton);
                
                // Start counter
                startElapsedTimeCounter();
            }
            
            // Show success message
            showAlert('success', data.message);
        } else {
            // Show error message
            showAlert('danger', data.error || 'Failed to start timer');
        }
    })
    .catch(error => {
        console.error('Error starting timer:', error);
        showAlert('danger', 'An error occurred while starting the timer');
    });
}

// Stop timer for active job
function stopTimer() {
    // Get CSRF token
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    
    // Send request to stop timer
    fetch('/api/stop-timer/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: 'notes=Stopped from dashboard'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Swap buttons
            const stopTimerBtn = document.getElementById('stopTimerBtn');
            if (stopTimerBtn) {
                // Replace the button with start button
                const btnGroup = stopTimerBtn.parentNode;
                stopTimerBtn.remove();
                
                const newButton = document.createElement('button');
                newButton.className = 'btn btn-primary';
                newButton.id = 'startTimerBtn';
                newButton.dataset.jobId = data.job_name;
                newButton.innerHTML = `<i class="bi bi-play-circle"></i> Start Time`;
                newButton.addEventListener('click', startTimer);
                
                btnGroup.prepend(newButton);
            }
            
            // Show success message and time tracked
            showAlert('success', `${data.message} Time tracked: ${data.duration}`);
        } else {
            // Show error message
            showAlert('danger', data.error || 'Failed to stop timer');
        }
    })
    .catch(error => {
        console.error('Error stopping timer:', error);
        showAlert('danger', 'An error occurred while stopping the timer');
    });
}

// Start elapsed time counter for active timer
function startElapsedTimeCounter() {
    // Get timer start time and elapsed time elements
    const stopTimerBtn = document.getElementById('stopTimerBtn');
    if (!stopTimerBtn) return;
    
    // Start time is stored in data attribute or needs to be retrieved from API
    let seconds = 0;
    
    // Update timer every second
    const intervalId = setInterval(() => {
        seconds++;
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        let displayTime = '';
        if (hours > 0) {
            displayTime = `${hours}h ${minutes}m`;
        } else {
            displayTime = `${minutes}m ${secs}s`;
        }
        
        // Update button text
        stopTimerBtn.innerHTML = `<i class="bi bi-stop-circle"></i> Stop Time (${displayTime})`;
        
        // If button no longer exists, clear interval
        if (!document.getElementById('stopTimerBtn')) {
            clearInterval(intervalId);
        }
    }, 1000);
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
    
    // Add alert to container
    const container = document.querySelector('main > .container');
    container.insertBefore(alertElement, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertElement.classList.remove('show');
        setTimeout(() => {
            alertElement.remove();
        }, 150);
    }, 5000);
}
