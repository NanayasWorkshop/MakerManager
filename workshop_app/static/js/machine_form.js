/**
 * Machine Form JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    setupFormValidation();
});

// Setup form validation
function setupFormValidation() {
    const machineForm = document.getElementById('addMachineForm') || 
                       document.getElementById('editMachineForm');
    
    if (machineForm) {
        machineForm.addEventListener('submit', function(event) {
            let isValid = true;
            
            // Validate required fields
            const requiredFields = machineForm.querySelectorAll('[required]');
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            // Validate number inputs
            const numberInputs = [
                document.getElementById('hourly_rate'),
                document.getElementById('setup_rate'),
                document.getElementById('cleanup_rate'),
                document.getElementById('purchase_price')
            ];
            
            numberInputs.forEach(input => {
                if (input && input.value && parseFloat(input.value) < 0) {
                    isValid = false;
                    input.classList.add('is-invalid');
                }
            });
            
            // Validate date inputs
            const purchaseDate = document.getElementById('purchase_date');
            const warrantyEndDate = document.getElementById('warranty_end_date');
            
            if (purchaseDate && warrantyEndDate && 
                purchaseDate.value && warrantyEndDate.value &&
                new Date(purchaseDate.value) > new Date(warrantyEndDate.value)) {
                isValid = false;
                warrantyEndDate.classList.add('is-invalid');
                alert('Warranty end date cannot be earlier than purchase date');
            }
            
            if (!isValid) {
                event.preventDefault();
                alert('Please correct the errors in the form before submitting.');
            }
        });
        
        // Remove invalid class on input
        const formInputs = machineForm.querySelectorAll('input, select, textarea');
        formInputs.forEach(input => {
            input.addEventListener('input', function() {
                this.classList.remove('is-invalid');
            });
        });
    }
}
