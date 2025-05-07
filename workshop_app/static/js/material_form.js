// Material Form JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Filter material types based on selected category
    const categorySelect = document.getElementById('category');
    const typeSelect = document.getElementById('type');
    
    if (categorySelect && typeSelect) {
        // Hide all type options initially except the placeholder
        function updateTypeOptions() {
            const selectedCategoryId = categorySelect.value;
            
            // Disable all options first
            Array.from(typeSelect.options).forEach(option => {
                if (option.value === '') {
                    // Keep placeholder visible
                    option.hidden = false;
                } else {
                    const optionCategoryId = option.getAttribute('data-category');
                    option.hidden = optionCategoryId !== selectedCategoryId;
                }
            });
            
            // Set default selection
            typeSelect.value = '';
        }
        
        // Update options on page load
        updateTypeOptions();
        
        // Update options when category changes
        categorySelect.addEventListener('change', updateTypeOptions);
    }
    
    // Form validation
    const addMaterialForm = document.getElementById('addMaterialForm');
    if (addMaterialForm) {
        addMaterialForm.addEventListener('submit', function(event) {
            let isValid = true;
            
            // Validate required fields
            const requiredFields = addMaterialForm.querySelectorAll('[required]');
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            // Validate stock number inputs
            const numberInputs = [
                document.getElementById('current_stock'),
                document.getElementById('minimum_stock_level'),
                document.getElementById('price_per_unit')
            ];
            
            numberInputs.forEach(input => {
                if (input && input.value && parseFloat(input.value) < 0) {
                    isValid = false;
                    input.classList.add('is-invalid');
                }
            });
            
            // Validate date inputs
            const purchaseDate = document.getElementById('purchase_date');
            const expirationDate = document.getElementById('expiration_date');
            
            if (purchaseDate && expirationDate && 
                purchaseDate.value && expirationDate.value &&
                new Date(purchaseDate.value) > new Date(expirationDate.value)) {
                isValid = false;
                expirationDate.classList.add('is-invalid');
                alert('Expiration date cannot be earlier than purchase date');
            }
            
            if (!isValid) {
                event.preventDefault();
                alert('Please correct the errors in the form before submitting.');
            }
        });
    }
});
