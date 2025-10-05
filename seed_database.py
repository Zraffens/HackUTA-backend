#!/usr/bin/env python3
"""
Database Seeding Script for Note Sharing Platform
This script clears the database and populates it with realistic sample data.
"""

import os
import sys
import random
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Add the app to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.note import Note
from app.models.course import Course
from app.models.tag import Tag
from app.models.comment import Comment
from app.models.reaction import NoteReaction
from app.services.file_service import save_file, get_upload_folder
from app.services.ocr_service import ocr_service
from werkzeug.datastructures import FileStorage
import uuid

def clear_database():
    """Clear all data from the database"""
    print("🗑️  Clearing database...")
    
    # Drop all tables and recreate them
    db.drop_all()
    db.create_all()
    
    print("✅ Database cleared and recreated")

def clear_upload_folders():
    """Clear upload directories"""
    print("🗑️  Clearing upload folders...")
    
    folders_to_clear = [
        'uploads/notes',
        'uploads/markdown'
    ]
    
    for folder in folders_to_clear:
        folder_path = Path(folder)
        if folder_path.exists():
            shutil.rmtree(folder_path)
        folder_path.mkdir(parents=True, exist_ok=True)
    
    print("✅ Upload folders cleared")

def create_users():
    """Create sample users"""
    print("👥 Creating users...")
    
    users_data = [
        # Admin users
        {'username': 'admin', 'email': 'admin@hackuta.com', 'password': 'AdminPass123!', 'bio': 'Platform Administrator', 'is_admin': True},
        {'username': 'prof_johnson', 'email': 'johnson@uta.edu', 'password': 'ProfPass123!', 'bio': 'Computer Science Professor at UTA', 'is_admin': True},
        
        # Regular students
        {'username': 'alice_chen', 'email': 'alice.chen@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'CS Senior, love algorithms and data structures'},
        {'username': 'bob_wilson', 'email': 'bob.wilson@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'Software Engineering student, interested in web development'},
        {'username': 'carol_garcia', 'email': 'carol.garcia@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'AI enthusiast, working on machine learning projects'},
        {'username': 'david_kim', 'email': 'david.kim@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'Database systems specialist, SQL expert'},
        {'username': 'emma_brown', 'email': 'emma.brown@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'Computer graphics and game development lover'},
        {'username': 'frank_davis', 'email': 'frank.davis@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'Cybersecurity focus, ethical hacking enthusiast'},
        {'username': 'grace_lee', 'email': 'grace.lee@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'Operating systems and parallel computing'},
        {'username': 'henry_taylor', 'email': 'henry.taylor@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'Mobile app developer, iOS and Android'},
        {'username': 'ivy_martinez', 'email': 'ivy.martinez@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'Data science and analytics student'},
        {'username': 'jack_anderson', 'email': 'jack.anderson@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'Network administrator, cloud computing'},
        {'username': 'kelly_moore', 'email': 'kelly.moore@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'UX/UI designer with programming skills'},
        {'username': 'liam_clark', 'email': 'liam.clark@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'DevOps engineer, CI/CD pipeline expert'},
        {'username': 'mia_rodriguez', 'email': 'mia.rodriguez@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'Bioinformatics, computational biology'},
        {'username': 'noah_lewis', 'email': 'noah.lewis@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'Computer vision and image processing'},
        {'username': 'olivia_walker', 'email': 'olivia.walker@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'Full-stack developer, MEAN stack'},
        {'username': 'peter_hall', 'email': 'peter.hall@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'Embedded systems and IoT development'},
        {'username': 'quinn_allen', 'email': 'quinn.allen@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'Quantum computing research student'},
        {'username': 'ruby_young', 'email': 'ruby.young@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'Software testing and quality assurance'},
        {'username': 'sam_king', 'email': 'sam.king@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'Blockchain and cryptocurrency enthusiast'},
        {'username': 'tina_wright', 'email': 'tina.wright@mavs.uta.edu', 'password': 'StudentPass123!', 'bio': 'Human-computer interaction researcher'},
    ]
    
    users = []
    for user_data in users_data:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            profile_bio=user_data['bio'],
            is_admin=user_data.get('is_admin', False)
        )
        user.set_password(user_data['password'])
        users.append(user)
        db.session.add(user)
    
    db.session.commit()
    print(f"✅ Created {len(users)} users")
    return users

def create_courses():
    """Create sample courses"""
    print("📚 Creating courses...")
    
    courses_data = [
        {'code': 'CSE 1310', 'name': 'Introduction to Computers and Programming'},
        {'code': 'CSE 1320', 'name': 'Intermediate Programming'},
        {'code': 'CSE 2312', 'name': 'Computer Organization and Assembly Language Programming'},
        {'code': 'CSE 2315', 'name': 'Discrete Structures'},
        {'code': 'CSE 3318', 'name': 'Algorithms and Data Structures'},
        {'code': 'CSE 3320', 'name': 'Operating Systems'},
        {'code': 'CSE 3330', 'name': 'Database Systems and File Structures'},
        {'code': 'CSE 4305', 'name': 'Compilers for Algorithmic Languages'},
        {'code': 'CSE 4308', 'name': 'Artificial Intelligence'},
        {'code': 'CSE 4314', 'name': 'Operating Systems Concepts'},
        {'code': 'CSE 4315', 'name': 'Programming Languages'},
        {'code': 'CSE 4316', 'name': 'Algorithm Analysis and Design'},
        {'code': 'CSE 4317', 'name': 'Computer Graphics'},
        {'code': 'CSE 4321', 'name': 'Software Engineering'},
        {'code': 'CSE 4322', 'name': 'Software Testing'},
        {'code': 'MATH 1426', 'name': 'Calculus I'},
        {'code': 'MATH 2425', 'name': 'Calculus II'},
        {'code': 'MATH 2326', 'name': 'Discrete Mathematics'},
        {'code': 'PHYS 1443', 'name': 'General Technical Physics I'},
        {'code': 'PHYS 1444', 'name': 'General Technical Physics II'},
    ]
    
    courses = []
    for course_data in courses_data:
        course = Course(
            code=course_data['code'],
            name=course_data['name']
        )
        courses.append(course)
        db.session.add(course)
    
    db.session.commit()
    print(f"✅ Created {len(courses)} courses")
    return courses

def create_tags():
    """Create sample tags"""
    print("🏷️  Creating tags...")
    
    tags_data = [
        'algorithms', 'data-structures', 'programming', 'java', 'python', 'c++', 
        'javascript', 'web-development', 'database', 'sql', 'machine-learning', 
        'artificial-intelligence', 'computer-graphics', 'operating-systems', 
        'networking', 'cybersecurity', 'software-engineering', 'testing', 
        'calculus', 'linear-algebra', 'discrete-math', 'statistics', 'physics',
        'homework', 'midterm', 'final-exam', 'study-guide', 'lecture-notes',
        'project', 'assignment', 'quiz', 'review', 'cheat-sheet', 'formula',
        'examples', 'practice-problems', 'solutions', 'theory', 'practical',
        'beginner', 'intermediate', 'advanced', 'tutorial', 'reference'
    ]
    
    tags = []
    for tag_name in tags_data:
        tag = Tag(name=tag_name)
        tags.append(tag)
        db.session.add(tag)
    
    db.session.commit()
    print(f"✅ Created {len(tags)} tags")
    return tags

def copy_sample_file(source_file, note_id):
    """Copy a sample file to the uploads directory with a unique name"""
    source_path = Path('sample_files') / source_file
    if not source_path.exists():
        print(f"⚠️  Sample file not found: {source_path}")
        return None
    
    # Create unique filename
    file_ext = source_path.suffix
    unique_filename = f"{uuid.uuid4().hex}_{source_file}"
    
    # Get upload folder
    upload_folder = get_upload_folder()
    dest_path = Path(upload_folder) / unique_filename
    
    # Copy file
    shutil.copy2(source_path, dest_path)
    return str(dest_path)

def create_notes_with_sample_files(users, courses, tags):
    """Create sample notes using the available sample files"""
    print("📝 Creating notes with sample files...")
    
    sample_files = ['Screenshot 2025-10-04 161119.pdf', 'testing.jpg']
    
    # Note templates with realistic academic content
    note_templates = [
        # Computer Science Notes
        {'title': 'Data Structures - Linked Lists', 'description': 'Comprehensive notes on linked list implementation and operations', 'course_codes': ['CSE 1320', 'CSE 3318'], 'tag_names': ['data-structures', 'programming', 'algorithms', 'lecture-notes']},
        {'title': 'Binary Search Tree Implementation', 'description': 'Step-by-step guide to implementing BST in Java', 'course_codes': ['CSE 3318'], 'tag_names': ['data-structures', 'java', 'algorithms', 'examples']},
        {'title': 'Operating Systems - Process Scheduling', 'description': 'Different CPU scheduling algorithms explained', 'course_codes': ['CSE 3320', 'CSE 4314'], 'tag_names': ['operating-systems', 'algorithms', 'study-guide']},
        {'title': 'Database Normalization Rules', 'description': 'First, second, and third normal forms with examples', 'course_codes': ['CSE 3330'], 'tag_names': ['database', 'sql', 'theory', 'examples']},
        {'title': 'Compiler Design - Lexical Analysis', 'description': 'Token recognition and finite automata', 'course_codes': ['CSE 4305'], 'tag_names': ['compilers', 'theory', 'advanced', 'lecture-notes']},
        {'title': 'AI Search Algorithms', 'description': 'BFS, DFS, A* and heuristic search methods', 'course_codes': ['CSE 4308'], 'tag_names': ['artificial-intelligence', 'algorithms', 'search', 'theory']},
        {'title': 'Software Testing Strategies', 'description': 'Unit testing, integration testing, and test-driven development', 'course_codes': ['CSE 4322'], 'tag_names': ['software-engineering', 'testing', 'practical', 'tutorial']},
        {'title': 'Computer Graphics - 3D Transformations', 'description': 'Matrix operations for 3D object manipulation', 'course_codes': ['CSE 4317'], 'tag_names': ['computer-graphics', 'linear-algebra', 'theory', 'examples']},
        {'title': 'Network Protocol Stack', 'description': 'OSI model and TCP/IP protocol suite', 'course_codes': ['CSE 3320'], 'tag_names': ['networking', 'protocols', 'theory', 'reference']},
        {'title': 'Machine Learning - Linear Regression', 'description': 'Mathematical foundations and implementation', 'course_codes': ['CSE 4308'], 'tag_names': ['machine-learning', 'statistics', 'python', 'algorithms']},
        
        # Math and Physics Notes
        {'title': 'Calculus - Limits and Continuity', 'description': 'Definition and properties of limits', 'course_codes': ['MATH 1426'], 'tag_names': ['calculus', 'theory', 'formula', 'examples']},
        {'title': 'Integration Techniques', 'description': 'Integration by parts, substitution, partial fractions', 'course_codes': ['MATH 2425'], 'tag_names': ['calculus', 'formula', 'practice-problems', 'tutorial']},
        {'title': 'Discrete Math - Graph Theory', 'description': 'Graph algorithms and properties', 'course_codes': ['MATH 2326', 'CSE 2315'], 'tag_names': ['discrete-math', 'algorithms', 'theory', 'examples']},
        {'title': 'Linear Algebra - Eigenvalues', 'description': 'Computing eigenvalues and eigenvectors', 'course_codes': ['MATH 2326'], 'tag_names': ['linear-algebra', 'theory', 'examples', 'formula']},
        {'title': 'Physics - Newton\'s Laws', 'description': 'Fundamental laws of motion with examples', 'course_codes': ['PHYS 1443'], 'tag_names': ['physics', 'mechanics', 'theory', 'examples']},
        {'title': 'Electromagnetic Fields', 'description': 'Electric and magnetic field calculations', 'course_codes': ['PHYS 1444'], 'tag_names': ['physics', 'electromagnetism', 'formula', 'theory']},
        
        # Exam and Study Materials
        {'title': 'Midterm Study Guide - Algorithms', 'description': 'Key concepts for the algorithms midterm exam', 'course_codes': ['CSE 3318'], 'tag_names': ['study-guide', 'midterm', 'algorithms', 'review']},
        {'title': 'Final Exam Practice - Database Systems', 'description': 'Practice problems for database final exam', 'course_codes': ['CSE 3330'], 'tag_names': ['final-exam', 'database', 'practice-problems', 'sql']},
        {'title': 'Calculus Cheat Sheet', 'description': 'Essential formulas and derivatives', 'course_codes': ['MATH 1426', 'MATH 2425'], 'tag_names': ['cheat-sheet', 'calculus', 'formula', 'reference']},
        {'title': 'Programming Assignment - Sorting', 'description': 'Implementation of various sorting algorithms', 'course_codes': ['CSE 1320', 'CSE 3318'], 'tag_names': ['assignment', 'programming', 'algorithms', 'java']},
        
        # Project and Assignment Notes
        {'title': 'Web Development Project Planning', 'description': 'Full-stack web application architecture', 'course_codes': ['CSE 4321'], 'tag_names': ['web-development', 'project', 'javascript', 'software-engineering']},
        {'title': 'Database Project - Library System', 'description': 'ER diagram and SQL implementation', 'course_codes': ['CSE 3330'], 'tag_names': ['database', 'project', 'sql', 'practical']},
        {'title': 'AI Project - Game Playing Agent', 'description': 'Minimax algorithm implementation', 'course_codes': ['CSE 4308'], 'tag_names': ['artificial-intelligence', 'project', 'algorithms', 'programming']},
        {'title': 'Operating Systems Lab - Process Management', 'description': 'Hands-on process creation and synchronization', 'course_codes': ['CSE 3320'], 'tag_names': ['operating-systems', 'practical', 'programming', 'c++']},
        
        # Advanced Topics
        {'title': 'Cybersecurity - Cryptographic Protocols', 'description': 'RSA, AES, and digital signatures', 'course_codes': ['CSE 4314'], 'tag_names': ['cybersecurity', 'cryptography', 'advanced', 'theory']},
        {'title': 'Parallel Programming Concepts', 'description': 'Multi-threading and parallel algorithms', 'course_codes': ['CSE 4314'], 'tag_names': ['programming', 'parallel-processing', 'advanced', 'c++']},
        {'title': 'Computer Vision Fundamentals', 'description': 'Image processing and pattern recognition', 'course_codes': ['CSE 4308'], 'tag_names': ['computer-vision', 'machine-learning', 'advanced', 'python']},
        {'title': 'Distributed Systems Architecture', 'description': 'Microservices and distributed computing', 'course_codes': ['CSE 4321'], 'tag_names': ['distributed-systems', 'software-engineering', 'advanced', 'networking']},
    ]
    
    notes = []
    for i, template in enumerate(note_templates):
        # Cycle through sample files
        sample_file = sample_files[i % len(sample_files)]
        
        # Create note
        owner = random.choice(users)
        note = Note(
            title=template['title'],
            description=template['description'],
            is_public=random.choice([True, True, True, False]),  # 75% public
            owner_id=owner.id,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90))
        )
        
        # Copy sample file
        file_path = copy_sample_file(sample_file, note.public_id)
        if file_path:
            note.file_path = file_path
            note.ocr_status = 'pending'  # Will be processed later
        
        notes.append(note)
        db.session.add(note)
        db.session.flush()  # Get the note ID
        
        # Add course associations
        for course_code in template['course_codes']:
            course = next((c for c in courses if c.code == course_code), None)
            if course:
                note.courses.append(course)
        
        # Add tag associations
        for tag_name in template['tag_names']:
            tag = next((t for t in tags if t.name == tag_name), None)
            if tag:
                note.tags.append(tag)
    
    db.session.commit()
    print(f"✅ Created {len(notes)} notes")
    return notes

def process_notes_with_ocr(notes):
    """Process notes with OCR to generate markdown"""
    print("🔄 Processing notes with OCR...")
    
    processed_count = 0
    for note in notes:
        if note.file_path and os.path.exists(note.file_path):
            print(f"Processing: {note.title}")
            
            # Generate output filename
            output_filename = f"note_{note.public_id}"
            
            # Process with OCR
            markdown_path = ocr_service.convert_to_markdown(note.file_path, output_filename)
            
            if markdown_path:
                note.markdown_path = markdown_path
                note.ocr_status = 'completed'
                processed_count += 1
            else:
                note.ocr_status = 'failed'
            
            db.session.add(note)
    
    db.session.commit()
    print(f"✅ Processed {processed_count} notes with OCR")

def create_comments_and_reactions(notes, users):
    """Create comments and reactions for notes"""
    print("💬 Creating comments and reactions...")
    
    comment_templates = [
        "Great notes! Very helpful for understanding the concept.",
        "Thanks for sharing this. The examples are really clear.",
        "Could you add more details about the implementation?",
        "This helped me with my assignment. Much appreciated!",
        "Excellent explanation of the algorithm.",
        "The diagrams make this so much easier to understand.",
        "Perfect timing! I have an exam tomorrow.",
        "I was struggling with this topic. This really helped!",
        "Can you share more notes from this course?",
        "The step-by-step approach is fantastic.",
        "This is exactly what I was looking for.",
        "Very well organized and easy to follow.",
        "Thanks for the detailed examples!",
        "This saved me so much time studying.",
        "The mathematical notation is perfect.",
    ]
    
    reaction_types = ['concise', 'detailed', 'readable']
    
    comments_created = 0
    reactions_created = 0
    
    for note in notes:
        # Add random comments (0-5 per note)
        num_comments = random.randint(0, 5)
        for _ in range(num_comments):
            comment = Comment(
                content=random.choice(comment_templates),
                note_id=note.id,
                user_id=random.choice(users).id,
                created_at=note.created_at + timedelta(days=random.randint(1, 10))
            )
            db.session.add(comment)
            comments_created += 1
        
        # Add random reactions (0-10 per note)
        num_reactions = random.randint(0, 10)
        reacting_users = random.sample(users, min(num_reactions, len(users)))
        
        for user in reacting_users:
            reaction = NoteReaction(
                note_id=note.id,
                user_id=user.id,
                reaction_type=random.choice(reaction_types)
            )
            db.session.add(reaction)
            reactions_created += 1
    
    db.session.commit()
    print(f"✅ Created {comments_created} comments and {reactions_created} reactions")

def create_bookmarks(notes, users):
    """Create bookmark relationships"""
    print("🔖 Creating bookmarks...")
    
    bookmarks_created = 0
    for user in users:
        # Each user bookmarks 0-8 random notes
        num_bookmarks = random.randint(0, 8)
        bookmarked_notes = random.sample(notes, min(num_bookmarks, len(notes)))
        
        for note in bookmarked_notes:
            if note not in user.bookmarked_notes:
                user.bookmarked_notes.append(note)
                bookmarks_created += 1
    
    db.session.commit()
    print(f"✅ Created {bookmarks_created} bookmarks")

def update_view_and_download_counts(notes):
    """Add realistic view and download counts"""
    print("📊 Adding view and download counts...")
    
    for note in notes:
        # Public notes get more views
        if note.is_public:
            note.view_count = random.randint(5, 150)
            note.download_count = random.randint(1, note.view_count // 3)
        else:
            note.view_count = random.randint(1, 20)
            note.download_count = random.randint(0, note.view_count // 2)
        
        db.session.add(note)
    
    db.session.commit()
    print("✅ Updated view and download counts")

def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        clear_database()
        clear_upload_folders()
        
        # Create base data
        users = create_users()
        courses = create_courses()
        tags = create_tags()
        
        # Create notes with sample files
        notes = create_notes_with_sample_files(users, courses, tags)
        
        # Process notes with OCR (this might take a while)
        process_notes_with_ocr(notes)
        
        # Add social features
        create_comments_and_reactions(notes, users)
        create_bookmarks(notes, users)
        
        # Add metrics
        update_view_and_download_counts(notes)
        
        print("=" * 50)
        print("🎉 Database seeding completed successfully!")
        print(f"📊 Summary:")
        print(f"   👥 Users: {len(users)}")
        print(f"   📚 Courses: {len(courses)}")
        print(f"   🏷️  Tags: {len(tags)}")
        print(f"   📝 Notes: {len(notes)}")
        print(f"   💬 Comments: Added")
        print(f"   ⭐ Reactions: Added")
        print(f"   🔖 Bookmarks: Added")
        print("")
        print("🔑 Admin Login: admin@hackuta.com / AdminPass123!")
        print("👨‍🎓 Student Login: alice.chen@mavs.uta.edu / StudentPass123!")
        print("")
        print("🚀 Your note sharing platform is ready to use!")

if __name__ == '__main__':
    main()
