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
    Determine the type of code scanned
    
    Args:
        code (str): Scanned code
        
    Returns:
        str: 'job', 'material', 'machine', or 'unknown'
    """
    if validate_job_id(code):
        return 'job'
    elif validate_material_id(code):
        return 'material'
    elif validate_machine_id(code):
        return 'machine'
    else:
        # Try to recognize other formats like EAN, supplier codes, etc.
        # This would require more sophisticated logic for production
        return 'unknown'

def parse_code(code):
    """
    Parse the scanned code to extract ID
    
    Args:
        code (str): Scanned code which might contain additional data
        
    Returns:
        str: Extracted ID from the code
    """
    # For QR codes that might contain URLs or additional data
    # Example: https://workshop.example.com/material/M-12345
    # Should extract M-12345
    
    if not code:
        return None
        
    # URL pattern
    url_pattern = r'(?:.*/)?((?:J|JOB|M|MAT|MC|MACH)-\d{1,6})(?:/.*)?$'
    url_match = re.search(url_pattern, code, re.IGNORECASE)
    
    if url_match:
        return url_match.group(1)
    
    # Direct ID pattern
    id_pattern = r'((?:J|JOB|M|MAT|MC|MACH)-\d{1,6})'
    id_match = re.search(id_pattern, code, re.IGNORECASE)
    
    if id_match:
        return id_match.group(1)
    
    # Just return the original code if we can't parse it
    return code
