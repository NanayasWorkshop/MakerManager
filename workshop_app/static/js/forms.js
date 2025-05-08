/**
 * Workshop Management System - Form Handling Utilities
 * Functions for form validation, submission, and data handling
 */

// Validate required fields in a form
function validateRequiredFields(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Validate a numeric input
function validateNumericInput(input, min = null, max = null) {
    const value = parseFloat(input.value);
    
    if (isNaN(value)) {
        return false;
    }
    
    if (min !== null && value < min) {
        return false;
    }
    
    if (max !== null && value > max) {
        return false;
    }
    
    return true;
}

// Toggle disabled state of a form field based on checkbox
function toggleFieldByCheckbox(checkboxId, fieldId, inverse = false) {
    const checkbox = document.getElementById(checkboxId);
    const field = document.getElementById(fieldId);
    const container = field.closest('.container') || field.parentElement;
    
    if (!checkbox || !field) return;
    
    checkbox.addEventListener('change', function() {
        const enableField = inverse ? !this.checked : this.checked;
        
        field.disabled = !enableField;
        
        if (container) {
            container.style.display = enableField ? 'block' : 'none';
        }
        
        if (enableField) {
            field.setAttribute('required', 'required');
        } else {
            field.removeAttribute('required');
        }
    });
    
    // Initial state
    checkbox.dispatchEvent(new Event('change'));
}

// Serialize form data to object
function serializeForm(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    return data;
}

// Collect form data for AJAX submission
function getFormData(form) {
    return new FormData(form);
}

// Export form utilities for use in other modules
window.WMSForms = {
    validateRequiredFields,
    validateNumericInput,
    toggleFieldByCheckbox,
    serializeForm,
    getFormData
};
