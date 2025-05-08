# workshop_app/utils/price_utils.py

from decimal import Decimal

def calculate_weighted_average_price(current_stock, current_price, new_stock, new_price):
    """
    Calculate weighted average price based on current stock and new restock.
    
    Args:
        current_stock (Decimal): Current quantity in stock
        current_price (Decimal): Current price per unit
        new_stock (Decimal): Quantity being added
        new_price (Decimal): Price per unit of new stock
        
    Returns:
        Decimal: New weighted average price per unit
    """
    # Handle case where there's no current price
    if current_price is None or current_price == 0:
        return new_price
    
    # Calculate total value of current stock
    current_value = current_stock * current_price
    
    # Calculate value of new stock
    new_value = new_stock * new_price
    
    # Calculate total stock after restock
    total_stock = current_stock + new_stock
    
    # Calculate weighted average price
    if total_stock > 0:
        weighted_avg = (current_value + new_value) / total_stock
        # Round to 2 decimal places
        return Decimal(str(weighted_avg)).quantize(Decimal('0.01'))
    
    return Decimal('0.00')
