"""
OCR Service using Google Gemini AI for converting handwritten notes to markdown.
This service handles the conversion of PDF/image files to markdown format using Gemini Vision API.
"""
import os
import logging
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def get_markdown_output_dir():
    """Get absolute path to markdown output directory"""
    # Get project root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    return os.path.join(project_root, 'uploads', 'markdown')

class GeminiOCRService:
    """Service for handling OCR conversion using Google Gemini AI"""
    
    def __init__(self):
        self.markdown_dir = get_markdown_output_dir()
        self.api_key = GEMINI_API_KEY
        self.client = None
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set in environment variables")
        else:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Gemini OCR Service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {str(e)}")
        
        # Create markdown directory if it doesn't exist
        if not os.path.exists(self.markdown_dir):
            os.makedirs(self.markdown_dir)
    
    def convert_to_markdown(self, input_file_path, output_filename=None):
        """
        Convert a PDF or image file to markdown using Gemini AI.
        
        Args:
            input_file_path (str): Path to the input PDF or image file
            output_filename (str): Optional custom output filename (without extension)
            
        Returns:
            str: Path to the generated markdown file, or None if conversion failed
        """
        try:
            # Validate input file exists
            if not os.path.exists(input_file_path):
                logger.error(f"Input file not found: {input_file_path}")
                return None
            
            if not self.client:
                logger.error("GEMINI_API_KEY not configured or client initialization failed")
                return None
            
            # Generate output filename if not provided
            if output_filename is None:
                input_basename = os.path.basename(input_file_path)
                output_filename = os.path.splitext(input_basename)[0]
            
            logger.info(f"Converting {input_file_path} to markdown using Gemini AI")
            
            # Check file type
            file_ext = os.path.splitext(input_file_path)[1].lower()
            
            if file_ext == '.pdf':
                # Convert PDF to images
                images = self._pdf_to_images(input_file_path)
            elif file_ext in ['.jpg', '.jpeg', '.png']:
                # Load single image
                images = [Image.open(input_file_path)]
            else:
                logger.error(f"Unsupported file type: {file_ext}")
                return None
            
            # Process all images with Gemini
            markdown_content = self._process_images_with_gemini(images)
            
            if not markdown_content:
                logger.error("No markdown content generated")
                return None
            
            # Save markdown to file
            final_path = os.path.join(self.markdown_dir, f"{output_filename}.md")
            final_path = os.path.normpath(final_path)  # Normalize path separators
            with open(final_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Markdown file created: {final_path}")
            return final_path
                
        except Exception as e:
            logger.error(f"Error during OCR conversion: {str(e)}", exc_info=True)
            return None
    
    def _pdf_to_images(self, pdf_path):
        """Convert PDF pages to PIL Images"""
        images = []
        try:
            pdf_document = fitz.open(pdf_path)
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                # Render page to pixmap (image)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                # Convert to PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(img)
            pdf_document.close()
            logger.info(f"Converted PDF to {len(images)} images")
        except Exception as e:
            logger.error(f"Error converting PDF to images: {str(e)}")
        return images
    
    def _process_images_with_gemini(self, images):
        """Process images with Gemini and return markdown"""
        try:
            all_markdown = []
            
            for idx, img in enumerate(images):
                logger.info(f"Processing image {idx + 1}/{len(images)}")
                
                prompt = """Convert this handwritten note/document to markdown format. 
                
Instructions:
- Extract ALL text accurately, including handwritten notes
- Preserve mathematical equations in LaTeX format (use $...$ for inline and $$...$$ for block equations) and make them such that they follow the markdown rules. they should be seen properly in markdown. don't add them as code. add them as actual 
- Maintain proper heading hierarchy with #, ##, ###
- Use lists (- or 1.) where appropriate
- Preserve tables in markdown table format
- Keep the formatting clean and readable
- If there are diagrams, describe them in [Image: description] format

Return ONLY the markdown content, no explanations."""
                
                # Convert PIL Image to bytes
                import io
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
                
                # Use the client to generate content with the new SDK
                response = self.client.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents=[
                        prompt, 
                        types.Part.from_bytes(data=img_bytes, mime_type='image/png')
                    ]
                )
                
                if response.text:
                    # Extract markdown content from code blocks
                    content = response.text
                    
                    # Check if content is wrapped in ```markdown ... ```
                    if '```markdown' in content:
                        # Extract content between ```markdown and ```
                        start = content.find('```markdown') + len('```markdown')
                        end = content.find('```', start)
                        if end != -1:
                            content = content[start:end].strip()
                    elif '```' in content:
                        # Handle generic code blocks
                        start = content.find('```') + 3
                        # Skip language identifier if present
                        newline = content.find('\n', start)
                        if newline != -1:
                            start = newline + 1
                        end = content.find('```', start)
                        if end != -1:
                            content = content[start:end].strip()
                    
                    all_markdown.append(f"\n\n---\n**Page {idx + 1}**\n---\n\n")
                    all_markdown.append(content)
            
            return "\n".join(all_markdown)
            
        except Exception as e:
            logger.error(f"Error processing with Gemini: {str(e)}", exc_info=True)
            return None
    
    def convert_async(self, input_file_path, note_id, callback=None):
        """
        Asynchronously convert a file to markdown (for background processing).
        This is a placeholder for future async implementation.
        
        Args:
            input_file_path (str): Path to input file
            note_id (str): Note public ID
            callback (callable): Optional callback function after completion
            
        Returns:
            bool: True if conversion was queued successfully
        """
        # TODO: Implement with Celery or similar task queue
        # For now, just do synchronous conversion
        output_filename = f"note_{note_id}"
        result = self.convert_to_markdown(input_file_path, output_filename)
        
        if callback and result:
            callback(note_id, result)
        
        return result is not None


# Singleton instance
ocr_service = GeminiOCRService()
