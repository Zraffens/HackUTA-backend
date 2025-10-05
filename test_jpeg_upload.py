#!/usr/bin/env python3

import requests
from PIL import Image
from PIL import ImageDraw
import io

def test_jpeg_upload():
    """Test uploading a JPEG image"""
    
    # Create a test JPEG image
    img = Image.new('RGB', (600, 400), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Add some content
    draw.rectangle([30, 30, 570, 80], fill='darkblue')
    draw.rectangle([30, 100, 450, 150], fill='darkblue')
    draw.rectangle([30, 170, 500, 220], fill='darkblue')
    
    # Save as JPEG
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=90)
    img_bytes.seek(0)
    
    # Login
    login_data = {'email': 'admin@hackuta.com', 'password': 'AdminPass123!'}
    login_response = requests.post('http://localhost:5000/api/auth/login', json=login_data)
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Upload JPEG
    files = {'file': ('test_jpeg.jpg', img_bytes, 'image/jpeg')}
    data = {
        'title': 'Test JPEG Upload',
        'description': 'Testing JPEG to PDF conversion',
        'is_public': True
    }
    
    print("Uploading JPEG file...")
    response = requests.post('http://localhost:5000/api/notes', 
                           headers=headers, 
                           files=files, 
                           data=data)
    
    print(f"Upload response: {response.status_code}")
    
    if response.status_code == 201:
        note_data = response.json()
        note_id = note_data['public_id']
        print(f"SUCCESS: JPEG uploaded and converted! Note ID: {note_id}")
        print(f"Has markdown: {note_data.get('has_markdown')}")
        print(f"Markdown URL: {note_data.get('markdown_url')}")
        return note_id
    else:
        print(f"FAILED: {response.text}")
        return None

if __name__ == '__main__':
    test_jpeg_upload()
