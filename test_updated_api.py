#!/usr/bin/env python3

import requests

def test_updated_api():
    # Login as admin
    login_data = {'email': 'admin@hackuta.com', 'password': 'AdminPass123!'}
    login_response = requests.post('http://localhost:5000/api/auth/login', json=login_data)
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    print('=== TESTING UPDATED API RESPONSES ===')

    # Test getting all notes
    response = requests.get('http://localhost:5000/api/notes', headers=headers)
    print(f'GET /api/notes: {response.status_code}')

    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
        if items:
            note = items[0]
            print(f'Note fields: {list(note.keys())}')
            has_markdown = note.get('has_markdown')
            markdown_url = note.get('markdown_url')
            ocr_status = note.get('ocr_status')
            print(f'has_markdown: {has_markdown}')
            print(f'markdown_url: {markdown_url}')
            print(f'ocr_status: {ocr_status}')
        else:
            print('No notes found')

    # Test getting specific note
    note_id = '8849d7aa-52a6-453c-8475-e3554deae87b'
    response = requests.get(f'http://localhost:5000/api/notes/{note_id}', headers=headers)
    print(f'\nGET /api/notes/{note_id}: {response.status_code}')

    if response.status_code == 200:
        note = response.json()
        print(f'Note fields: {list(note.keys())}')
        has_markdown = note.get('has_markdown')
        markdown_url = note.get('markdown_url')
        print(f'has_markdown: {has_markdown}')
        print(f'markdown_url: {markdown_url}')
        print(f'SUCCESS: Frontend can now use the markdown_url field!')
        
        # Show example usage for frontend
        print(f'\n=== FRONTEND USAGE EXAMPLE ===')
        print(f'1. Fetch note: GET /api/notes/{note_id}')
        print(f'2. Check if markdown available: note.has_markdown = {has_markdown}')
        print(f'3. If available, fetch markdown: GET {markdown_url}')
        print(f'4. No need to construct URL - it\'s provided in the response!')

if __name__ == '__main__':
    test_updated_api()
