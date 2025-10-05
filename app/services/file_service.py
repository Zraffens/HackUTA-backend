import os
import uuid
from werkzeug.utils import secure_filename
from pathlib import Path
from flask import current_app
from PIL import Image
import logging

logger = logging.getLogger(__name__)

# Use absolute path to ensure consistency regardless of working directory
def get_upload_folder():
    """Get absolute path to upload folder"""
    if current_app:
        # Get the project root directory (where run.py is located)
        project_root = os.path.dirname(current_app.root_path)
        return os.path.join(project_root, 'uploads', 'notes')
    else:
        # Fallback for when not in app context
        return os.path.join(os.getcwd(), 'uploads', 'notes')

def get_markdown_folder():
    """Get absolute path to markdown upload folder"""
    if current_app:
        # Get the project root directory (where run.py is located)
        project_root = os.path.dirname(current_app.root_path)
        return os.path.join(project_root, 'uploads', 'markdown')
    else:
        # Fallback for when not in app context
        return os.path.join(os.getcwd(), 'uploads', 'markdown')

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}  # Added image formats for MonkeyOCR

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    """
    Save uploaded file (PDF or image) to the uploads directory.
    If the file is an image, convert it to PDF first.
    
    Args:
        file: FileStorage object from Flask request
        
    Returns:
        str: Path to saved file (always PDF), or None if invalid
    """
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Get absolute upload folder path
        upload_folder = get_upload_folder()
        
        # Ensure upload directory exists
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        # Use proper path joining and normalization
        file_path = os.path.join(upload_folder, unique_filename)
        file_path = os.path.normpath(file_path)  # Normalize path separators
        
        # Save the file
        file.save(file_path)
        
        # Check if it's an image and convert to PDF
        file_extension = get_file_extension(filename)
        if file_extension in ['jpg', 'jpeg', 'png']:
            logger.info(f"Converting image to PDF: {file_path}")
            pdf_path = convert_image_to_pdf(file_path)
            if pdf_path:
                logger.info(f"Image converted to PDF successfully: {pdf_path}")
                return pdf_path
            else:
                logger.error(f"Failed to convert image to PDF: {file_path}")
                # Clean up the original file if conversion failed
                if os.path.exists(file_path):
                    os.remove(file_path)
                return None
        
        # If it's already a PDF, return as-is
        return file_path
    return None

def get_file_extension(filename):
    """Get file extension from filename."""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else None


def convert_image_to_pdf(image_path):
    """
    Convert an image file to PDF format.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        str: Path to the converted PDF file, or None if conversion failed
    """
    try:
        logger.info(f"Starting image to PDF conversion: {image_path}")
        
        # Generate PDF filename
        base_name = os.path.splitext(image_path)[0]
        pdf_path = f"{base_name}.pdf"
        
        # Open image and convert to PDF
        with Image.open(image_path) as img:
            logger.info(f"Image opened successfully. Mode: {img.mode}, Size: {img.size}")
            
            # Convert to RGB if necessary (PNG with transparency, CMYK, etc.)
            if img.mode not in ['RGB', 'L']:  # L is for grayscale
                logger.info(f"Converting image mode from {img.mode} to RGB")
                img = img.convert('RGB')
            
            # Save as PDF with good quality
            img.save(pdf_path, 'PDF', quality=95, optimize=True, resolution=150.0)
            
        logger.info(f"Successfully converted image to PDF: {pdf_path}")
        
        # Verify the PDF was created and has content
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            # Remove the original image file
            os.remove(image_path)
            logger.info(f"Removed original image file: {image_path}")
            return pdf_path
        else:
            logger.error(f"PDF file was not created properly: {pdf_path}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to convert image to PDF: {str(e)}")
        # Clean up partial files
        try:
            pdf_path = f"{os.path.splitext(image_path)[0]}.pdf"
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                logger.info(f"Cleaned up partial PDF file: {pdf_path}")
        except:
            pass
        return None


def fix_file_path(stored_path):
    """
    Fix file paths that might have incorrect directory structure.
    This handles legacy paths that might include 'app' incorrectly and normalizes separators.
    
    Args:
        stored_path: Path stored in database
        
    Returns:
        str: Corrected absolute path to the file with normalized separators
    """
    if not stored_path:
        return None
    
    # Normalize path separators first
    normalized_stored_path = os.path.normpath(stored_path)
    
    # If already absolute and exists, return normalized version
    if os.path.isabs(normalized_stored_path) and os.path.exists(normalized_stored_path):
        return normalized_stored_path
    
    # Extract just the filename from the stored path
    filename = os.path.basename(stored_path)
    
    # Determine if this is a markdown file or regular upload
    if 'markdown' in stored_path or filename.endswith('.md'):
        # This is a markdown file
        correct_path = os.path.join(get_markdown_folder(), filename)
    else:
        # This is a regular upload file
        correct_path = os.path.join(get_upload_folder(), filename)
    
    # Normalize the correct path
    correct_path = os.path.normpath(correct_path)
    
    # If the correct path exists, return it
    if os.path.exists(correct_path):
        return correct_path
    
    # If stored path is relative, try making it absolute from project root
    if not os.path.isabs(stored_path):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        absolute_path = os.path.join(project_root, stored_path)
        absolute_path = os.path.normpath(absolute_path)  # Normalize separators
        if os.path.exists(absolute_path):
            return absolute_path
    
    # Return the normalized stored path (will fail later with proper error)
    return normalized_stored_path
