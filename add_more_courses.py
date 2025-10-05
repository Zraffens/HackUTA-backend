#!/usr/bin/env python3
"""
Add more UTA courses to the database
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models import Course
from app.extensions import db

def add_more_courses():
    """Add more realistic UTA courses across different departments"""
    
    # Additional Computer Science courses
    cs_courses = [
        ("CSE 1105", "Introduction to Computer Science and Engineering"),
        ("CSE 2440", "Introduction to Computer Systems"),
        ("CSE 3302", "Advanced Programming Languages"),
        ("CSE 3313", "Introduction to Signal Processing"),
        ("CSE 3323", "Human Computer Interactions"),
        ("CSE 3380", "Linear Algebra for CSE"),
        ("CSE 4334", "Introduction to Multimedia Systems"),
        ("CSE 4342", "Embedded Systems"),
        ("CSE 4351", "Parallel Processing"),
        ("CSE 4352", "Computer Architecture"),
        ("CSE 4353", "Computer Networks"),
        ("CSE 4354", "Computer and Network Security"),
        ("CSE 4355", "Advanced Computer Graphics"),
        ("CSE 4356", "Intelligent Systems Design"),
        ("CSE 4357", "Markup Languages"),
        ("CSE 4358", "Autonomous Robot Design"),
        ("CSE 4360", "Introduction to Data Mining"),
        ("CSE 4361", "Software Design Patterns"),
        ("CSE 4392", "Machine Learning"),
    ]
    
    # Mathematics courses
    math_courses = [
        ("MATH 1421", "College Algebra and Trigonometry"),
        ("MATH 2330", "Calculus III"),
        ("MATH 3319", "Introduction to Mathematical Proof"),
        ("MATH 3321", "Abstract Algebra I"),
        ("MATH 3330", "Introduction to Real Analysis"),
        ("MATH 3334", "Advanced Discrete Mathematics"),
        ("MATH 4315", "Linear Algebra"),
        ("MATH 4318", "Probability and Statistics for Engineers"),
        ("MATH 4334", "Applied Statistics"),
        ("MATH 4350", "Numerical Analysis"),
    ]
    
    # Engineering courses
    engineering_courses = [
        ("EE 1202", "Electric Circuit Analysis I"),
        ("EE 2302", "Electric Circuit Analysis II"),
        ("EE 3302", "Electronic Devices"),
        ("EE 3317", "Applied Electromagnetic Theory"),
        ("EE 3318", "Digital Logic Design"),
        ("EE 4314", "Digital Signal Processing"),
        ("EE 4325", "Introduction to VLSI Design"),
        ("EE 4330", "Integrated Circuit Design"),
        ("ME 1331", "Introduction to Mechanical Engineering"),
        ("ME 2315", "Statics"),
        ("ME 2330", "Dynamics"),
        ("ME 3315", "Thermodynamics"),
        ("ME 3318", "Fluid Mechanics"),
        ("ME 4310", "Machine Design"),
    ]
    
    # Business courses
    business_courses = [
        ("ACCT 2301", "Fundamentals of Financial Accounting"),
        ("ACCT 2302", "Fundamentals of Managerial Accounting"),
        ("BCOM 3310", "Business Communication"),
        ("FINA 3313", "Financial Management"),
        ("MARK 3321", "Principles of Marketing"),
        ("MGMT 3310", "Organization Theory and Behavior"),
        ("MGMT 4322", "Strategic Management"),
        ("OPMA 3306", "Operations Management"),
        ("BLAW 3311", "Legal Environment of Business"),
    ]
    
    # Science courses
    science_courses = [
        ("BIOL 1441", "General Biology I"),
        ("BIOL 1442", "General Biology II"),
        ("CHEM 1441", "General Chemistry I"),
        ("CHEM 1442", "General Chemistry II"),
        ("CHEM 2321", "Organic Chemistry I"),
        ("CHEM 2322", "Organic Chemistry II"),
        ("GEOL 1301", "Earth Sciences"),
        ("GEOL 1302", "Historical Geology"),
    ]
    
    # Liberal Arts courses
    liberal_arts_courses = [
        ("ENGL 1301", "Rhetoric and Composition"),
        ("ENGL 1302", "Rhetoric and Composition"),
        ("HIST 1311", "United States History to 1865"),
        ("HIST 1312", "United States History from 1865"),
        ("PHIL 1301", "Introduction to Philosophy"),
        ("PHIL 2311", "Introduction to Logic"),
        ("PSYC 1315", "Introduction to Psychology"),
        ("SOCI 1301", "Principles of Sociology"),
        ("POLS 2311", "Government of the United States"),
        ("POLS 2312", "State and Local Government"),
        ("ECON 2305", "Principles of Microeconomics"),
        ("ECON 2306", "Principles of Macroeconomics"),
    ]
    
    # Foreign Languages
    language_courses = [
        ("SPAN 1441", "Beginning Spanish I"),
        ("SPAN 1442", "Beginning Spanish II"),
        ("FREN 1441", "Beginning French I"),
        ("FREN 1442", "Beginning French II"),
        ("GERM 1441", "Beginning German I"),
        ("CHIN 1441", "Beginning Chinese I"),
    ]
    
    # Combine all courses
    all_new_courses = (cs_courses + math_courses + engineering_courses + 
                      business_courses + science_courses + liberal_arts_courses + 
                      language_courses)
    
    print(f"Adding {len(all_new_courses)} new courses to the database...")
    
    courses_added = 0
    courses_skipped = 0
    
    for code, name in all_new_courses:
        # Check if course already exists by code or name
        existing_course_by_code = Course.query.filter_by(code=code).first()
        existing_course_by_name = Course.query.filter_by(name=name).first()
        
        if existing_course_by_code:
            print(f"⏭️  Skipping {code} - course code already exists")
            courses_skipped += 1
            continue
            
        if existing_course_by_name:
            print(f"⏭️  Skipping {code}: {name} - course name already exists")
            courses_skipped += 1
            continue
        
        # Create new course
        course = Course(code=code, name=name)
        db.session.add(course)
        courses_added += 1
        print(f"✅ Added {code}: {name}")
    
    # Commit all changes
    db.session.commit()
    
    print(f"\n📊 Summary:")
    print(f"   ✅ New courses added: {courses_added}")
    print(f"   ⏭️  Courses skipped (already exist): {courses_skipped}")
    print(f"   📚 Total courses in database: {Course.query.count()}")

def main():
    """Main function"""
    app = create_app()
    
    with app.app_context():
        print("🎓 Adding more UTA courses to the database...")
        add_more_courses()
        print("\n🎉 Course addition completed!")

if __name__ == "__main__":
    main()
