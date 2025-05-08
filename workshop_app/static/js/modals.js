/**
 * Workshop Management System - Modal Dialog Utilities
 * Functions for handling modal dialogs and their data
 */

// Setup a modal with data from trigger element
function setupModal(modalId, triggerSelector, dataMap) {
    const triggers = document.querySelectorAll(triggerSelector);
    
    if (!triggers.length) return;
    
    triggers.forEach(trigger => {
        trigger.addEventListener('click', function(event) {
            const modal = document.getElementById(modalId);
            if (!modal) return;
            
            // Set data from trigger to modal fields
            for (const [attribute, targetId] of Object.entries(dataMap)) {
                const value = this.getAttribute(`data-${attribute}`);
                const target = modal.querySelector(`#${targetId}`);
                
                if (target && value) {
                    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
                        target.value = value;
                    } else {
                        target.textContent = value;
                    }
                }
            }
            
            // If there's a form in the modal, trigger a custom event
            const form = modal.querySelector('form');
            if (form) {
                form.dispatchEvent(new CustomEvent('modalopened', {
                    detail: { trigger: this }
                }));
            }
        });
    });
}

// Handle modal form submission
function setupModalForm(modalId, formId, submitHandler, successCallback = null) {
    const modal = document.getElementById(modalId);
    const form = document.getElementById(formId);
    
    if (!modal || !form) return;
    
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        try {
            const result = await submitHandler(form);
            
            if (result.success) {
                // Close the modal
                const modalInstance = bootstrap.Modal.getInstance(modal);
                modalInstance.hide();
                
                // Call success callback if provided
                if (successCallback && typeof successCallback === 'function') {
                    successCallback(result);
                }
            } else {
                // Show error message within the modal
                const errorEl = modal.querySelector('.alert-danger') || document.createElement('div');
                errorEl.className = 'alert alert-danger';
                errorEl.textContent = result.error || 'An error occurred';
                
                if (!modal.querySelector('.alert-danger')) {
                    form.prepend(errorEl);
                }
            }
        } catch (error) {
            console.error('Error submitting modal form:', error);
            alert('An error occurred while processing your request.');
        }
    });
}

// Export modal utilities for use in other modules
window.WMSModals = {
    setupModal,
    setupModalForm
};
