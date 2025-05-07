// Material Detail JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Set up minimum stock indicator position based on minimum stock level
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
    
    // Form validation for withdraw
    const withdrawForm = document.querySelector('form[action*="withdraw"]');
    if (withdrawForm) {
        withdrawForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const quantity = parseFloat(document.getElementById('quantity').value);
            const maxQuantity = parseFloat(document.getElementById('quantity').getAttribute('max'));
            const notes = document.getElementById('notes').value;
            const materialId = window.location.pathname.split('/').filter(Boolean).pop();
            
            if (isNaN(quantity) || quantity <= 0) {
                alert('Please enter a valid quantity greater than zero.');
                return;
            } else if (quantity > maxQuantity) {
                alert(`Cannot withdraw more than current stock (${maxQuantity}).`);
                return;
            }
            
            // Submit form via AJAX
            const formData = new FormData(withdrawForm);
            
            fetch(withdrawForm.action, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Close the modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('withdrawModal'));
                    modal.hide();
                    
                    // Update the UI without page reload
                    document.getElementById('quantity').value = '';
                    document.getElementById('notes').value = '';
                    
                    // Update current stock display
                    const newStock = (currentStock - quantity).toFixed(2);
                    currentStockElement.textContent = newStock;
                    currentStockElement.setAttribute('data-current-stock', newStock);
                    
                    // Update progress bar
                    const progressBar = document.querySelector('.progress-bar');
                    if (progressBar) {
                        const percent = minStockLevel ? ((newStock / minStockLevel) * 100) : 100;
                        progressBar.style.width = `${percent}%`;
                        progressBar.textContent = `${newStock} ${document.querySelector('[data-unit]').getAttribute('data-unit')}`;
                        
                        // Update progress bar color based on stock level
                        if (minStockLevel && newStock <= minStockLevel) {
                            progressBar.className = progressBar.className.replace(/bg-\w+/, 'bg-warning');
                        } else if (newStock <= 0) {
                            progressBar.className = progressBar.className.replace(/bg-\w+/, 'bg-danger');
                        }
                    }
                    
                    // Add new transaction to history
                    const transactionsList = document.querySelector('.list-group-flush');
                    if (transactionsList) {
                        const now = new Date();
                        const dateStr = now.toISOString().split('T')[0] + ' ' + 
                                       now.toTimeString().split(' ')[0].substring(0, 5);
                        
                        const newTransaction = document.createElement('div');
                        newTransaction.className = 'list-group-item';
                        newTransaction.innerHTML = `
                            <div class="d-flex w-100 justify-content-between">
                                <h6 class="mb-1">
                                    <span class="badge bg-warning text-dark">Withdrawal</span>
                                    ${quantity} ${document.querySelector('[data-unit]').getAttribute('data-unit')}
                                </h6>
                                <small class="text-muted">${dateStr}</small>
                            </div>
                            <p class="mb-1"><small>Job: ${data.job_reference}</small></p>
                            <p class="mb-1"><small>Operator: ${data.operator_name}</small></p>
                            ${notes ? `<small class="text-muted">Notes: ${notes}</small>` : ''}
                        `;
                        
                        transactionsList.insertBefore(newTransaction, transactionsList.firstChild);
                    }
                    
                    // Show success message
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-success alert-dismissible fade show';
                    alertDiv.innerHTML = `
                        <strong>Success!</strong> ${data.message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    `;
                    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
                    
                    // Auto dismiss alert after 5 seconds
                    setTimeout(() => {
                        alertDiv.remove();
                    }, 5000);
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error processing withdrawal:', error);
                alert('An error occurred while processing the withdrawal.');
            });
        });
    }
    
    // Form validation for return
    const returnForm = document.querySelector('form[action*="return"]');
    if (returnForm) {
        returnForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const quantity = parseFloat(document.getElementById('return_quantity').value);
            const notes = document.getElementById('return_notes').value;
            const materialId = window.location.pathname.split('/').filter(Boolean).pop();
            
            if (isNaN(quantity) || quantity <= 0) {
                alert('Please enter a valid quantity greater than zero.');
                return;
            }
            
            // Submit form via AJAX
            const formData = new FormData(returnForm);
            
            fetch(returnForm.action, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Close the modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('returnModal'));
                    modal.hide();
                    
                    // Update the UI without page reload
                    document.getElementById('return_quantity').value = '';
                    document.getElementById('return_notes').value = '';
                    
                    // Update current stock display
                    const currentStock = parseFloat(currentStockElement.getAttribute('data-current-stock'));
                    const newStock = (currentStock + quantity).toFixed(2);
                    currentStockElement.textContent = newStock;
                    currentStockElement.setAttribute('data-current-stock', newStock);
                    
                    // Update progress bar
                    const progressBar = document.querySelector('.progress-bar');
                    if (progressBar) {
                        const percent = minStockLevel ? ((newStock / minStockLevel) * 100) : 100;
                        progressBar.style.width = `${percent}%`;
                        progressBar.textContent = `${newStock} ${document.querySelector('[data-unit]').getAttribute('data-unit')}`;
                        
                        // Update progress bar color based on stock level
                        if (minStockLevel && newStock > minStockLevel) {
                            progressBar.className = progressBar.className.replace(/bg-\w+/, 'bg-success');
                        } else if (newStock > 0) {
                            progressBar.className = progressBar.className.replace(/bg-\w+/, newStock <= minStockLevel ? 'bg-warning' : 'bg-success');
                        }
                    }
                    
                    // Add new transaction to history
                    const transactionsList = document.querySelector('.list-group-flush');
                    if (transactionsList) {
                        const now = new Date();
                        const dateStr = now.toISOString().split('T')[0] + ' ' + 
                                       now.toTimeString().split(' ')[0].substring(0, 5);
                        
                        const newTransaction = document.createElement('div');
                        newTransaction.className = 'list-group-item';
                        newTransaction.innerHTML = `
                            <div class="d-flex w-100 justify-content-between">
                                <h6 class="mb-1">
                                    <span class="badge bg-success">Return</span>
                                    ${quantity} ${document.querySelector('[data-unit]').getAttribute('data-unit')}
                                </h6>
                                <small class="text-muted">${dateStr}</small>
                            </div>
                            <p class="mb-1"><small>Job: ${data.job_reference}</small></p>
                            <p class="mb-1"><small>Operator: ${data.operator_name}</small></p>
                            ${notes ? `<small class="text-muted">Notes: ${notes}</small>` : ''}
                        `;
                        
                        transactionsList.insertBefore(newTransaction, transactionsList.firstChild);
                    }
                    
                    // Show success message
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-success alert-dismissible fade show';
                    alertDiv.innerHTML = `
                        <strong>Success!</strong> ${data.message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    `;
                    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
                    
                    // Auto dismiss alert after 5 seconds
                    setTimeout(() => {
                        alertDiv.remove();
                    }, 5000);
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error processing return:', error);
                alert('An error occurred while processing the return.');
            });
        });
    }
    
    // QR code popup
    const qrCodeButton = document.querySelector('a.btn-outline-info');
    if (qrCodeButton) {
        qrCodeButton.addEventListener('click', function(event) {
            event.preventDefault();
            
            // Get material ID from URL
            const materialId = window.location.pathname.split('/').filter(Boolean).pop();
            
            // Fetch QR code
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
                        alert('Error: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error getting QR code:', error);
                    alert('An error occurred while getting the QR code.');
                });
        });
    }
    
    // Handle View Full History link
    const viewHistoryLink = document.querySelector('.card-footer .btn-outline-secondary');
    if (viewHistoryLink) {
        viewHistoryLink.addEventListener('click', function(event) {
            event.preventDefault();
            
            // Get material ID from URL
            const materialId = window.location.pathname.split('/').filter(Boolean).pop();
            
            // Redirect to full history page
            window.location.href = `/materials/${materialId}/history/`;
        });
    }
});
