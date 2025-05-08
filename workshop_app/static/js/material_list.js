/**
 * Material List Page JavaScript
 * Uses the utility modules for common functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle category selection to dynamically update types
    setupCategoryFilter();
    
    // Initialize modal data for withdraw and return
    setupWithdrawModal();
    setupReturnModal();
    
    // Form validation for withdraw and return
    setupFormValidation();
});

// Setup the category filter to update types
function setupCategoryFilter() {
    const categorySelect = document.getElementById('category');
    const typeSelect = document.getElementById('type');
    
    if (categorySelect && typeSelect) {
        categorySelect.addEventListener('change', function() {
            // We'd implement AJAX here to get types for the selected category
            // For now, we'll just submit the form to refresh
            document.getElementById('materialFilterForm').submit();
        });
    }
}

// Setup the withdraw modal
function setupWithdrawModal() {
    const withdrawModal = document.getElementById('withdrawModal');
    if (!withdrawModal) return;
    
    withdrawModal.addEventListener('show.bs.modal', function(event) {
        const button = event.relatedTarget;
        const materialId = button.getAttribute('data-material-id');
        const materialName = button.getAttribute('data-material-name');
        const materialUnit = button.getAttribute('data-material-unit');
        
        // Set modal title and form values
        withdrawModal.querySelector('.modal-title').textContent = `Withdraw ${materialName}`;
        document.getElementById('withdrawMaterialId').value = materialId;
        document.getElementById('withdrawUnitLabel').textContent = materialUnit;
        document.getElementById('withdrawForm').action = `/materials/${materialId}/withdraw/`;
        
        // Check if there's an active job and show in the info box
        checkActiveJob();
    });
}

// Setup the return modal
function setupReturnModal() {
    const returnModal = document.getElementById('returnModal');
    if (!returnModal) return;
    
    returnModal.addEventListener('show.bs.modal', function(event) {
        const button = event.relatedTarget;
        const materialId = button.getAttribute('data-material-id');
        const materialName = button.getAttribute('data-material-name');
        const materialUnit = button.getAttribute('data-material-unit');
        
        // Set modal title and form values
        returnModal.querySelector('.modal-title').textContent = `Return ${materialName}`;
        document.getElementById('returnMaterialId').value = materialId;
        document.getElementById('returnUnitLabel').textContent = materialUnit;
        document.getElementById('returnForm').action = `/materials/${materialId}/return/`;
    });
}

// Setup form validation for withdraw and return forms
function setupFormValidation() {
    const withdrawForm = document.getElementById('withdrawForm');
    if (withdrawForm) {
        withdrawForm.addEventListener('submit', function(event) {
            const quantity = parseFloat(document.getElementById('withdrawQuantity').value);
            if (isNaN(quantity) || quantity <= 0) {
                event.preventDefault();
                alert('Please enter a valid quantity greater than zero.');
            }
        });
    }
    
    const returnForm = document.getElementById('returnForm');
    if (returnForm) {
        returnForm.addEventListener('submit', function(event) {
            const quantity = parseFloat(document.getElementById('returnQuantity').value);
            if (isNaN(quantity) || quantity <= 0) {
                event.preventDefault();
                alert('Please enter a valid quantity greater than zero.');
            }
        });
    }
}

// Check for active job and update the info box
function checkActiveJob() {
    WMSAPI.getData('/api/active-job/')
        .then(data => {
            const infoBox = document.getElementById('jobAssociationInfo');
            if (data.has_active_job) {
                infoBox.innerHTML = `Material will be associated with your active job: <strong>${data.job_name}</strong>`;
                infoBox.style.display = 'block';
            } else {
                infoBox.innerHTML = 'You have no active job. Please activate a job before withdrawing material.';
                infoBox.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error checking active job:', error);
        });
}
