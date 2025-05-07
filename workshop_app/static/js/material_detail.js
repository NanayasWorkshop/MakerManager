// Material Detail JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Set up minimum stock indicator position based on minimum stock level
    const minStockIndicator = document.querySelector('.min-stock-indicator');
    const minStockLevel = parseFloat('{{ material.minimum_stock_level }}');
    const maxStockLevel = parseFloat('{{ material.minimum_stock_level|mul:2 }}') || parseFloat('{{ material.current_stock|mul:2 }}');
    
    if (minStockIndicator && minStockLevel) {
        const percent = (minStockLevel / maxStockLevel) * 100;
        minStockIndicator.querySelector('.line').style.left = `${percent}%`;
        minStockIndicator.querySelector('.label').style.left = `${percent}%`;
    }
    
    // Form validation for withdraw
    const withdrawForm = document.querySelector('form[action*="withdraw"]');
    if (withdrawForm) {
        withdrawForm.addEventListener('submit', function(event) {
            const quantity = parseFloat(document.getElementById('quantity').value);
            const maxQuantity = parseFloat(document.getElementById('quantity').getAttribute('max'));
            
            if (isNaN(quantity) || quantity <= 0) {
                event.preventDefault();
                alert('Please enter a valid quantity greater than zero.');
            } else if (quantity > maxQuantity) {
                event.preventDefault();
                alert(`Cannot withdraw more than current stock (${maxQuantity}).`);
            }
        });
    }
    
    // Form validation for return
    const returnForm = document.querySelector('form[action*="return"]');
    if (returnForm) {
        returnForm.addEventListener('submit', function(event) {
            const quantity = parseFloat(document.getElementById('return_quantity').value);
            
            if (isNaN(quantity) || quantity <= 0) {
                event.preventDefault();
                alert('Please enter a valid quantity greater than zero.');
            }
        });
    }
    
    // QR code popup could be implemented here
});
