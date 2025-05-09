/**
 * Material Detail Page JavaScript
 * Uses the utility modules for common functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Set up minimum stock indicator position based on minimum stock level
    setupMinStockIndicator();
    
    // Setup withdraw form
    setupWithdrawForm();
    
    // Setup return form
    setupReturnForm();
    
    // QR code popup
    setupQRCodeButton();
    
    // Handle View Full History link - no special handling needed
});

// Setup the minimum stock level indicator
function setupMinStockIndicator() {
    const minStockIndicator = document.querySelector('.min-stock-indicator');
    const minStockElement = document.querySelector('[data-min-stock]');
    const currentStockElement = document.querySelector('[data-current-stock]');
    
    if (minStockIndicator && minStockElement && currentStockElement) {
        const minStockLevel = parseFloat(minStockElement.getAttribute('data-min-stock'));
        const currentStock = parseFloat(currentStockElement.getAttribute('data-current-stock'));
        const maxStockLevel = minStockLevel ? (minStockLevel * 2) : (currentStock * 2);
        
        if (minStockLevel) {
            const percent = (minStockLevel / maxStockLevel) * 100;
            minStockIndicator.querySelector('.line').style.left = `${percent}%`;
            minStockIndicator.querySelector('.label').style.left = `${percent}%`;
        }
    }
}

// Setup the withdrawal form and handling
function setupWithdrawForm() {
    const withdrawForm = document.querySelector('form[action*="withdraw"]');
    if (!withdrawForm) return;
    
    withdrawForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Get form data
        const quantity = parseFloat(document.getElementById('quantity').value);
        const maxQuantity = parseFloat(document.getElementById('quantity').getAttribute('max'));
        const notes = document.getElementById('notes').value;
        const materialId = window.location.pathname.split('/').filter(Boolean).pop();
        
        // Validate quantity
        if (isNaN(quantity) || quantity <= 0) {
            alert('Please enter a valid quantity greater than zero.');
            return;
        } else if (quantity > maxQuantity) {
            alert(`Cannot withdraw more than current stock (${maxQuantity}).`);
            return;
        }
        
        // Create FormData object
        const formData = new FormData(withdrawForm);
        
        try {
            // Show loading indicator or disable form
            const submitBtn = withdrawForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            }
            
            // Submit using fetch API
            fetch(withdrawForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin' // Include cookies
            })
            .then(response => {
                if (!response.ok) {
                    console.warn(`Server responded with status: ${response.status}`);
                    // Try to parse response anyway, as it might contain useful error info
                }
                // Try to parse as JSON, but don't throw if it's not valid JSON
                return response.text().then(text => {
                    try {
                        return JSON.parse(text);
                    } catch (e) {
                        console.warn("Response was not valid JSON:", text);
                        // If we got a non-JSON response, the transaction might have still succeeded
                        // Let's reload the page to show the updated state
                        window.location.reload();
                        throw new Error("Invalid JSON response");
                    }
                });
            })
            .then(data => {
                // If we get here, we have a valid JSON response
                if (data.success) {
                    // Close the modal if it exists
                    const modal = bootstrap.Modal.getInstance(document.getElementById('withdrawModal'));
                    if (modal) modal.hide();
                    
                    // Update UI
                    updateMaterialUI(quantity, 'withdraw');
                    
                    // Add transaction to history list
                    addTransactionToHistory('withdrawal', quantity, data.job_reference, data.operator_name, notes);
                    
                    // Show success message
                    alert(`Successfully withdrew ${quantity} ${document.querySelector('[data-unit]').getAttribute('data-unit')} of material.`);
                } else {
                    // If there's an error message in the response, show it
                    if (data.error) {
                        alert('Error: ' + data.error);
                    } else {
                        console.warn("Server indicated failure but didn't provide error details");
                        // The transaction might have failed, but let's refresh anyway to be sure
                        window.location.reload();
                    }
                }
            })
            .catch(error => {
                console.error('Error handling response:', error);
                // Don't show another error alert here - we'll just silently reload
                window.location.reload();
            })
            .finally(() => {
                // Re-enable the submit button if we're still on the page
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = 'Withdraw';
                }
            });
        } catch (error) {
            console.error('Error submitting form:', error);
            // Even if there's an error in submitting the form,
            // the transaction might have gone through, so just reload the page
            window.location.reload();
        }
    });
}

// Setup the return form and handling
function setupReturnForm() {
    const returnForm = document.querySelector('form[action*="return"]');
    if (!returnForm) return;
    
    returnForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Get form data
        const quantity = parseFloat(document.getElementById('return_quantity').value);
        const notes = document.getElementById('return_notes').value;
        
        // Validate quantity
        if (isNaN(quantity) || quantity <= 0) {
            alert('Please enter a valid quantity greater than zero.');
            return;
        }
        
        // Create FormData object
        const formData = new FormData(returnForm);
        
        try {
            // Show loading indicator or disable form
            const submitBtn = returnForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            }
            
            // Submit using fetch API
            fetch(returnForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin' // Include cookies
            })
            .then(response => {
                if (!response.ok) {
                    console.warn(`Server responded with status: ${response.status}`);
                    // Try to parse response anyway, as it might contain useful error info
                }
                // Try to parse as JSON, but don't throw if it's not valid JSON
                return response.text().then(text => {
                    try {
                        return JSON.parse(text);
                    } catch (e) {
                        console.warn("Response was not valid JSON:", text);
                        // If we got a non-JSON response, the transaction might have still succeeded
                        // Let's reload the page to show the updated state
                        window.location.reload();
                        throw new Error("Invalid JSON response");
                    }
                });
            })
            .then(data => {
                // If we get here, we have a valid JSON response
                if (data.success) {
                    // Close the modal if it exists
                    const modal = bootstrap.Modal.getInstance(document.getElementById('returnModal'));
                    if (modal) modal.hide();
                    
                    // Update UI
                    updateMaterialUI(quantity, 'return');
                    
                    // Add transaction to history list
                    addTransactionToHistory('return', quantity, data.job_reference, data.operator_name, notes);
                    
                    // Show success message
                    alert(`Successfully returned ${quantity} ${document.querySelector('[data-unit]').getAttribute('data-unit')} of material.`);
                } else {
                    // If there's an error message in the response, show it
                    if (data.error) {
                        alert('Error: ' + data.error);
                    } else {
                        console.warn("Server indicated failure but didn't provide error details");
                        // The transaction might have failed, but let's refresh anyway to be sure
                        window.location.reload();
                    }
                }
            })
            .catch(error => {
                console.error('Error handling response:', error);
                // Don't show another error alert here - we'll just silently reload
                window.location.reload();
            })
            .finally(() => {
                // Re-enable the submit button if we're still on the page
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = 'Return';
                }
            });
        } catch (error) {
            console.error('Error submitting form:', error);
            // Even if there's an error in submitting the form,
            // the transaction might have gone through, so just reload the page
            window.location.reload();
        }
    });
}

// Update the material UI after a transaction
function updateMaterialUI(quantity, action) {
    const currentStockElement = document.getElementById('currentStockDisplay');
    const unitOfMeasurement = currentStockElement.getAttribute('data-unit');
    const currentStock = parseFloat(currentStockElement.getAttribute('data-current-stock'));
    
    // Calculate new stock
    const newStock = action === 'withdraw' ? 
        (currentStock - quantity).toFixed(2) : 
        (currentStock + quantity).toFixed(2);
    
    // Update current stock display
    currentStockElement.textContent = `${newStock} ${unitOfMeasurement}`;
    currentStockElement.setAttribute('data-current-stock', newStock);
    
    // Update progress bar
    const progressBar = document.querySelector('.progress-bar');
    const minStockLevel = parseFloat(document.querySelector('[data-min-stock]')?.getAttribute('data-min-stock') || '0');
    
    if (progressBar) {
        const percent = minStockLevel ? ((newStock / minStockLevel) * 100) : 100;
        progressBar.style.width = `${percent}%`;
        progressBar.textContent = `${newStock} ${unitOfMeasurement}`;
        
        // Update progress bar color based on stock level
        if (newStock <= 0) {
            progressBar.className = progressBar.className.replace(/bg-\w+/, 'bg-danger');
        } else if (minStockLevel && newStock <= minStockLevel) {
            progressBar.className = progressBar.className.replace(/bg-\w+/, 'bg-warning');
        } else {
            progressBar.className = progressBar.className.replace(/bg-\w+/, 'bg-success');
        }
    }
    
    // Reset form fields
    if (action === 'withdraw') {
        document.getElementById('quantity').value = '';
        document.getElementById('notes').value = '';
    } else {
        document.getElementById('return_quantity').value = '';
        document.getElementById('return_notes').value = '';
    }
}

// Add a transaction to the history list
function addTransactionToHistory(transactionType, quantity, jobReference, operatorName, notes) {
    const transactionsList = document.querySelector('.list-group-flush');
    if (!transactionsList) return;
    
    const now = new Date();
    const dateStr = now.toISOString().split('T')[0] + ' ' + 
                   now.toTimeString().split(' ')[0].substring(0, 5);
    
    const unitOfMeasurement = document.querySelector('[data-unit]').getAttribute('data-unit');
    
    const newTransaction = document.createElement('div');
    newTransaction.className = 'list-group-item';
    newTransaction.innerHTML = `
        <div class="d-flex w-100 justify-content-between">
            <h6 class="mb-1">
                <span class="badge ${transactionType === 'withdrawal' ? 'bg-warning text-dark' : 'bg-success'}">
                    ${transactionType === 'withdrawal' ? 'Withdrawal' : 'Return'}
                </span>
                ${quantity} ${unitOfMeasurement}
            </h6>
            <small class="text-muted">${dateStr}</small>
        </div>
        <p class="mb-1"><small>Job: ${jobReference}</small></p>
        <p class="mb-1"><small>Operator: ${operatorName}</small></p>
        ${notes ? `<small class="text-muted">Notes: ${notes}</small>` : ''}
    `;
    
    transactionsList.insertBefore(newTransaction, transactionsList.firstChild);
}

// Setup the QR code button functionality
function setupQRCodeButton() {
    const qrCodeButton = document.querySelector('a.btn-outline-info');
    if (!qrCodeButton) return;
    
    qrCodeButton.addEventListener('click', function(event) {
        event.preventDefault();
        
        // Get material ID from URL
        const materialId = window.location.pathname.split('/').filter(Boolean).pop();
        
        // Fetch QR code using standard fetch
        fetch(`/materials/${materialId}/qr-code/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Create modal to display QR code
                    const modalHtml = `
                        <div class="modal fade" id="qrCodeModal" tabindex="-1" aria-hidden="true">
                            <div class="modal-dialog">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h5 class="modal-title">QR Code for ${data.material_name}</h5>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                    </div>
                                    <div class="modal-body text-center">
                                        <img src="${data.qr_code_url}" alt="QR Code" class="img-fluid">
                                        <p class="mt-2">Material ID: ${materialId}</p>
                                        <p class="mt-2">Scan this code to quickly access this material.</p>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                        <a href="${data.qr_code_url}" download="qrcode-${materialId}.png" class="btn btn-primary">Download</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    // Add modal to body
                    document.body.insertAdjacentHTML('beforeend', modalHtml);
                    
                    // Show modal
                    const modal = new bootstrap.Modal(document.getElementById('qrCodeModal'));
                    modal.show();
                    
                    // Remove modal from DOM when hidden
                    document.getElementById('qrCodeModal').addEventListener('hidden.bs.modal', function() {
                        this.remove();
                    });
                } else {
                    alert('Error: ' + (data.error || 'Failed to get QR code'));
                }
            })
            .catch(error => {
                console.error('Error getting QR code:', error);
                alert('An error occurred while getting the QR code.');
            });
    });
}
