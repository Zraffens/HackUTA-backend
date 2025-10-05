#!/usr/bin/env python3

import os
from PIL import Image
import tempfile

def test_image_to_pdf_conversion():
    """Test the image to PDF conversion functionality"""
    
    # Create a simple test image
    test_image_path = "test_image.png"
    
    # Create a simple colored image
    img = Image.new('RGB', (800, 600), color='white')
    
    # Add some text-like content (simple colored rectangles to simulate text)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    
    # Draw some rectangles to simulate text/content
    draw.rectangle([50, 50, 750, 100], fill='black')
    draw.rectangle([50, 150, 600, 200], fill='black')
    draw.rectangle([50, 250, 700, 300], fill='black')
    draw.rectangle([50, 350, 500, 400], fill='black')
    
    # Save the test image
    img.save(test_image_path, 'PNG')
    print(f"Created test image: {test_image_path}")
    
    # Test the conversion function
    try:
        from app.services.file_service import convert_image_to_pdf
        from app import create_app
        
        app = create_app()
        with app.app_context():
            pdf_path = convert_image_to_pdf(test_image_path)
            
            if pdf_path and os.path.exists(pdf_path):
                print(f"SUCCESS: Image converted to PDF: {pdf_path}")
                print(f"PDF file size: {os.path.getsize(pdf_path)} bytes")
                
                # Clean up
                os.remove(pdf_path)
                print("Cleaned up test PDF file")
            else:
                print("FAILED: PDF conversion failed")
                
    except Exception as e:
        print(f"ERROR: {str(e)}")
        # Clean up test image if it still exists
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

if __name__ == '__main__':
    test_image_to_pdf_conversion()
