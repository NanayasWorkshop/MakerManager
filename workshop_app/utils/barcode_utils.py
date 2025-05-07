"""
Utility functions for barcode and QR code handling
"""
import qrcode
from io import BytesIO
import base64
import re
import logging

logger = logging.getLogger(__name__)

def generate_qr_code(data, size=10):
    """
    Generate a QR code image for the given data
    
    Args:
        data (str): Data to encode in the QR code
        size (int): Size of the QR code (default: 10)
        
    Returns:
        str: Base64 encoded image data for the QR code
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        return None

def validate_job_id(job_id):
    """
    Validate that the string is a valid job ID format
    
    Args:
        job_id (str): Job ID to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Example pattern: J-12345 or JOB-12345
    pattern = r'^(J|JOB)-\d{1,6}$'
    return bool(re.match(pattern, job_id, re.IGNORECASE))

def validate_material_id(material_id):
    """
    Validate that the string is a valid material ID format
    
    Args:
        material_id (str): Material ID to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Example pattern: M-12345 or MAT-12345
    pattern = r'^(M|MAT)-\d{1,6}$'
    return bool(re.match(pattern, material_id, re.IGNORECASE))

def validate_machine_id(machine_id):
    """
    Validate that the string is a valid machine ID format
    
    Args:
        machine_id (str): Machine ID to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Example pattern: MC-12345 or MACH-12345
    pattern = r'^(MC|MACH)-\d{1,6}$'
    return bool(re.match(pattern, machine_id, re.IGNORECASE))

def determine_code_type(code):
    """
    Determine the type of code scanned based on its format
    
    Args:
        code (str): Scanned code
        
    Returns:
        str: 'job', 'material', 'machine', or 'unknown'
    """
    if not code:
        return 'unknown'
        
    # Clean the code (remove spaces, ensure uppercase for pattern matching)
    code = code.strip().upper()
    
    # Try to match our internal code format first
    if validate_job_id(code):
        return 'job'
    elif validate_material_id(code):
        return 'material'
    elif validate_machine_id(code):
        return 'machine'
    
    # Check if it contains any identifiable prefixes
    if code.startswith('J-') or code.startswith('JOB-'):
        return 'job'
    elif code.startswith('M-') or code.startswith('MAT-'):
        return 'material'
    elif code.startswith('MC-') or code.startswith('MACH-'):
        return 'machine'
    
    # If we can't determine the type based on our internal format,
    # we'll assume it's either a material or machine serial number/barcode
    # The actual lookup will happen in the view
    
    # For now, we'll return 'unknown' and the view will attempt to find it in the database
    return 'unknown'

def parse_code(code):
    """
    Parse the scanned code to extract ID
    
    Args:
        code (str): Scanned code which might contain additional data
        
    Returns:
        str: Extracted ID from the code
    """
    if not code:
        return None
    
    # Clean the code
    code = code.strip()
    
    # URL pattern
    url_pattern = r'(?:.*/)?((?:J|JOB|M|MAT|MC|MACH)-\d{1,6})(?:/.*)?$'
    url_match = re.search(url_pattern, code, re.IGNORECASE)
    
    if url_match:
        return url_match.group(1)
    
    # Direct ID pattern for our internal codes
    id_pattern = r'((?:J|JOB|M|MAT|MC|MACH)-\d{1,6})'
    id_match = re.search(id_pattern, code, re.IGNORECASE)
    
    if id_match:
        return id_match.group(1)
    
    # If it doesn't match our internal format, return the whole code
    # as it could be a manufacturer's serial number or barcode
    return code
