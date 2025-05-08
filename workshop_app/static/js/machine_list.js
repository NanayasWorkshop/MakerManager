/**
 * Machine List JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Handle filter form submission
    setupFilterForm();
    
    // Handle type selection based on category
    setupOperatorCheckbox();
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
    const filterForm = document.getElementById('machineFilterForm');
    if (!filterForm) return;
    
    // Auto-submit on select change
    const selectElements = filterForm.querySelectorAll('select');
    selectElements.forEach(select => {
        select.addEventListener('change', function() {
            filterForm.submit();
        });
    });
}

// Setup operator checkbox
function setupOperatorCheckbox() {
    const operatorCheckbox = document.getElementById('operator');
    if (!operatorCheckbox) return;
    
    operatorCheckbox.addEventListener('change', function() {
        document.getElementById('machineFilterForm').submit();
    });
}
