#!/usr/bin/env python3
"""
Script to fix incorrect file paths in the database.
This will update any file paths that include 'app\' incorrectly.
"""

import os
from app import create_app, db
from app.models import Note
from app.services.file_service import fix_file_path

def fix_database_file_paths():
    """Fix incorrect file paths stored in database"""
    app = create_app()
    
    with app.app_context():
        print("Checking for notes with incorrect file paths...")
        
        notes = Note.query.all()
        fixed_count = 0
        
        for note in notes:
            update_needed = False
            
            # Fix file_path if needed
            if note.file_path:
                corrected_path = fix_file_path(note.file_path)
                if corrected_path != note.file_path:
                    print(f"Fixing file_path for note {note.public_id}:")
                    print(f"  Old: {note.file_path}")
                    print(f"  New: {corrected_path}")
                    note.file_path = corrected_path
                    update_needed = True
            
            # Fix markdown_path if needed
            if note.markdown_path:
                corrected_path = fix_file_path(note.markdown_path)
                if corrected_path != note.markdown_path:
                    print(f"Fixing markdown_path for note {note.public_id}:")
                    print(f"  Old: {note.markdown_path}")
                    print(f"  New: {corrected_path}")
                    note.markdown_path = corrected_path
                    update_needed = True
            
            if update_needed:
                fixed_count += 1
        
        if fixed_count > 0:
            db.session.commit()
            print(f"\nFixed {fixed_count} notes with incorrect file paths.")
        else:
            print("No file paths needed fixing.")
        
        # Additional verification - check for mixed separators
        print("\nChecking for mixed path separators...")
        mixed_separators_count = 0
        
        for note in notes:
            if note.file_path and ('/' in note.file_path and '\\' in note.file_path):
                print(f"Mixed separators in file_path for note {note.public_id}: {note.file_path}")
                mixed_separators_count += 1
            if note.markdown_path and ('/' in note.markdown_path and '\\' in note.markdown_path):
                print(f"Mixed separators in markdown_path for note {note.public_id}: {note.markdown_path}")
                mixed_separators_count += 1
        
        if mixed_separators_count > 0:
            print(f"Found {mixed_separators_count} paths with mixed separators (these should be fixed by normalization)")
        else:
            print("No mixed separators found in paths")
        
        print("File path fix complete!")

if __name__ == "__main__":
    fix_database_file_paths()
