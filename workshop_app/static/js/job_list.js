/**
 * Job List JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Handle filter form submission
    setupFilterForm();
});

// Initialize tooltips
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Setup the filter form
function setupFilterForm() {
    const filterForm = document.getElementById('jobFilterForm');
    if (!filterForm) return;
    
    // Auto-submit on select change
    const selectElements = filterForm.querySelectorAll('select');
    selectElements.forEach(select => {
        select.addEventListener('change', function() {
            filterForm.submit();
        });
    });
}

// Function to set active job
function setActiveJob(jobId) {
    if (confirm('Set this job as your active job?')) {
        document.getElementById('activeJobId').value = jobId;
        document.getElementById('setActiveJobForm').submit();
    }
}
