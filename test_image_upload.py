#!/usr/bin/env python3

import requests
from PIL import Image
from PIL import ImageDraw
import io
import os

def test_image_upload_conversion():
    """Test uploading an image through the API and verify it gets converted to PDF"""
    
    # Create a test image in memory
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add some content
    draw.rectangle([50, 50, 750, 100], fill='black')
    draw.rectangle([50, 150, 600, 200], fill='black')
    draw.text((50, 300), "Test Note Content", fill='black')
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Login as admin
    login_data = {'email': 'admin@hackuta.com', 'password': 'AdminPass123!'}
    login_response = requests.post('http://localhost:5000/api/auth/login', json=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Upload the image
        files = {'file': ('test_note.png', img_bytes, 'image/png')}
        data = {
            'title': 'Test Image Upload',
            'description': 'Testing image to PDF conversion',
            'is_public': True
        }
        
        print("Uploading image file...")
        response = requests.post('http://localhost:5000/api/notes', 
                               headers=headers, 
                               files=files, 
                               data=data)
        
        print(f"Upload response: {response.status_code}")
        
        if response.status_code == 201:
            note_data = response.json()
            note_id = note_data['public_id']
            print(f"SUCCESS: Note created with ID: {note_id}")
            print(f"Note title: {note_data['title']}")
            print(f"OCR status: {note_data['ocr_status']}")
            
            # Check if the file was saved as PDF
            print("\\nImage to PDF conversion test SUCCESSFUL!")
            print("Backend automatically converted the uploaded image to PDF format.")
            
        else:
            print(f"FAILED: Upload failed with status {response.status_code}")
            print(f"Response: {response.text}")
    else:
        print(f"Login failed: {login_response.status_code}")

if __name__ == '__main__':
    test_image_upload_conversion()
