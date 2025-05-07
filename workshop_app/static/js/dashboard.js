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
                // TODO: Implement AJAX call to clear active job
                window.location.reload();
            }
        });
    }
    
    // Quick action button handlers could be added here
});
