/**
 * Scanning Result Page JavaScript
 * For handling material operations on the scan result page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Setup the withdraw modal form submission
    setupWithdrawModal();
    
    // Setup the return modal form submission
    setupReturnModal();
});

// Setup the withdraw modal form submission
function setupWithdrawModal() {
    const withdrawModal = document.getElementById('withdrawModal');
    if (!withdrawModal) return;
    
    const withdrawForm = withdrawModal.querySelector('form');
    if (!withdrawForm) return;
    
    // Extract the material ID from the URL
    // URL could be like /scan/material/FLMRL-PLA-00018/
    const pathParts = window.location.pathname.split('/').filter(Boolean);
    const materialId = pathParts[pathParts.length - 1];
    
    // Make sure the form action is set correctly
    withdrawForm.setAttribute('action', `/materials/${materialId}/withdraw/`);
    
    // Handle form submission
    withdrawForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Get the form data
        const quantity = document.getElementById('withdrawQuantity').value;
        const notes = document.getElementById('withdrawNotes').value;
        
        // Create form data object
        const formData = new FormData();
        formData.append('quantity', quantity);
        formData.append('notes', notes);
        
        // Properly handle CSRF token
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfToken) {
            formData.append('csrfmiddlewaretoken', csrfToken.value);
        }
        
        // Submit the form via AJAX
        fetch(withdrawForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Close the modal
                const modal = bootstrap.Modal.getInstance(withdrawModal);
                if (modal) modal.hide();
                
                // Show success message
                alert(data.message || 'Material withdrawn successfully');
                
                // Reload the page to show updated stock
                window.location.reload();
            } else {
                alert('Error: ' + (data.error || 'Failed to withdraw material'));
            }
        })
        .catch(error => {
            console.error('Error withdrawing material:', error);
            // Even with error, reload the page as the transaction might have completed
            window.location.reload();
        });
    });
    
    // Get the withdraw button and make sure it submits the form
    const withdrawButton = withdrawModal.querySelector('.btn-primary');
    if (withdrawButton) {
        withdrawButton.addEventListener('click', function() {
            withdrawForm.dispatchEvent(new Event('submit'));
        });
    }
}

// Setup the return modal form submission
function setupReturnModal() {
    const returnModal = document.getElementById('returnModal');
    if (!returnModal) return;
    
    const returnForm = returnModal.querySelector('form');
    if (!returnForm) return;
    
    // Extract the material ID from the URL
    // URL could be like /scan/material/FLMRL-PLA-00018/
    const pathParts = window.location.pathname.split('/').filter(Boolean);
    const materialId = pathParts[pathParts.length - 1];
    
    // Make sure the form action is set correctly
    returnForm.setAttribute('action', `/materials/${materialId}/return/`);
    
    // Handle form submission
    returnForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Get the form data
        const quantity = document.getElementById('returnQuantity').value;
        const notes = document.getElementById('returnNotes').value;
        
        // Create form data object
        const formData = new FormData();
        formData.append('quantity', quantity);
        formData.append('notes', notes);
        
        // Properly handle CSRF token
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfToken) {
            formData.append('csrfmiddlewaretoken', csrfToken.value);
        }
        
        // Submit the form via AJAX
        fetch(returnForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Close the modal
                const modal = bootstrap.Modal.getInstance(returnModal);
                if (modal) modal.hide();
                
                // Show success message
                alert(data.message || 'Material returned successfully');
                
                // Reload the page to show updated stock
                window.location.reload();
            } else {
                alert('Error: ' + (data.error || 'Failed to return material'));
            }
        })
        .catch(error => {
            console.error('Error returning material:', error);
            // Even with error, reload the page as the transaction might have completed
            window.location.reload();
        });
    });
    
    // Get the return button and make sure it submits the form
    const returnButton = returnModal.querySelector('.btn-primary');
    if (returnButton) {
        returnButton.addEventListener('click', function() {
            returnForm.dispatchEvent(new Event('submit'));
        });
    }
}
