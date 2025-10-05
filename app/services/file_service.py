import os
import uuid
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads/notes'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}  # Added image formats for MonkeyOCR

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    """
    Save uploaded file (PDF or image) to the uploads directory.
    
    Args:
        file: FileStorage object from Flask request
        
    Returns:
        str: Path to saved file, or None if invalid
    """
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
            
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        return file_path
    return None

def get_file_extension(filename):
    """Get file extension from filename."""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else None
