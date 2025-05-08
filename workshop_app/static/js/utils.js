/**
 * Workshop Management System - Utility Functions
 * Contains general purpose utility functions used across the application
 */

// Create and show an alert message
function showAlert(container, type, message, autoDismiss = true, dismissTime = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <strong>${type === 'success' ? 'Success!' : type === 'danger' ? 'Error!' : 'Notice!'}</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    container.insertBefore(alertDiv, container.firstChild);
    
    if (autoDismiss) {
        setTimeout(() => {
            alertDiv.remove();
        }, dismissTime);
    }
    
    return alertDiv;
}

// Update element status styling (card, badge, etc)
function updateStatusStyling(element, oldStatus, newStatus, selector = 'className') {
    if (element) {
        if (selector === 'className') {
            element.className = element.className.replace(oldStatus, newStatus);
        } else {
            element.style[selector] = element.style[selector].replace(oldStatus, newStatus);
        }
    }
}

// Copy text to clipboard
function copyToClipboard(text, button, successClass = 'btn-success', originalClass = 'btn-outline-primary') {
    navigator.clipboard.writeText(text).then(() => {
        // Show temporary success message
        const originalHTML = button.innerHTML;
        button.innerHTML = '<i class="bi bi-check"></i>';
        button.classList.add(successClass);
        button.classList.remove(originalClass);
        
        setTimeout(() => {
            button.innerHTML = originalHTML;
            button.classList.remove(successClass);
            button.classList.add(originalClass);
        }, 1500);
    }).catch(err => {
        console.error('Could not copy text: ', err);
        alert('Failed to copy to clipboard');
    });
}

// Format date for display
function formatDate(date, includeTime = true) {
    if (!date) return '';
    const d = new Date(date);
    const dateStr = d.toISOString().split('T')[0];
    if (!includeTime) return dateStr;
    
    const timeStr = d.toTimeString().split(' ')[0].substring(0, 5);
    return `${dateStr} ${timeStr}`;
}

// Export utilities for use in other modules
window.WMSUtils = {
    showAlert,
    updateStatusStyling,
    copyToClipboard,
    formatDate
};
