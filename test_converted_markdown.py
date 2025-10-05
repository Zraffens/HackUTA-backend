#!/usr/bin/env python3

import requests

def test_converted_file_markdown():
    # Test the converted image's markdown endpoint
    note_id = '1143c747-d983-4262-9800-2ca6c77866bb'

    # Login
    login_data = {'email': 'admin@hackuta.com', 'password': 'AdminPass123!'}
    login_response = requests.post('http://localhost:5000/api/auth/login', json=login_data)
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Test markdown endpoint
    response = requests.get(f'http://localhost:5000/api/notes/{note_id}/markdown', headers=headers)
    print(f'Markdown endpoint status: {response.status_code}')

    if response.status_code == 200:
        data = response.json()
        markdown_content = data.get('markdown', '')
        status = data.get('status', 'unknown')
        print(f'Markdown status: {status}')
        print(f'Markdown length: {len(markdown_content)} chars')
        print(f'Markdown content: {repr(markdown_content)}')
        print('SUCCESS: Converted image processed successfully!')
    else:
        print(f'Error: {response.text}')

if __name__ == '__main__':
    test_converted_file_markdown()
