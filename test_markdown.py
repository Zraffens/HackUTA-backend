#!/usr/bin/env python3

import requests

def test_markdown_endpoint():
    # Test the working note
    note_id = '8849d7aa-52a6-453c-8475-e3554deae87b'

    # Login as admin
    login_data = {'email': 'admin@hackuta.com', 'password': 'AdminPass123!'}
    login_response = requests.post('http://localhost:5000/api/auth/login', json=login_data)

    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        print(f'Testing note: {note_id}')
        
        # Test the markdown endpoint
        response = requests.get(f'http://localhost:5000/api/notes/{note_id}/markdown', headers=headers)
        print(f'Markdown endpoint: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            markdown_content = data.get('markdown', '')
            status = data.get('status', 'unknown')
            file_path = data.get('file_path', 'unknown')
            
            print(f'SUCCESS: Got markdown content ({len(markdown_content)} chars)')
            print(f'Status: {status}')
            print(f'File path: {file_path}')
            print(f'First 100 chars: {repr(markdown_content[:100])}')
            
            # Test that it's proper markdown with math
            if 'lim_' in markdown_content and 'frac' in markdown_content:
                print('VERIFIED: Contains LaTeX math expressions')
            else:
                print('WARNING: No LaTeX math found')
                
            # Show the full content for debugging
            print('\n--- FULL MARKDOWN CONTENT ---')
            print(markdown_content)
            print('--- END CONTENT ---')
            
        else:
            print(f'ERROR: {response.text}')
            
        # Also test if note is publicly accessible (no auth)
        print('\n--- Testing public access ---')
        public_response = requests.get(f'http://localhost:5000/api/notes/{note_id}/markdown')
        print(f'Public access: {public_response.status_code}')
        if public_response.status_code != 200:
            print('NOTE: Markdown requires authentication')
            
    else:
        print(f'Login failed: {login_response.status_code}')

if __name__ == '__main__':
    test_markdown_endpoint()
