"""
Script to create the first admin user
Run this script once to set up the initial admin account
"""

from app import create_app
from app.extensions import db
from app.models import User
import uuid

def create_admin_user():
    """Create the first admin user"""
    app = create_app()
    
    with app.app_context():
        # Check if any admin user already exists
        existing_admin = User.query.filter_by(is_admin=True).first()
        if existing_admin:
            print(f"Admin user already exists: {existing_admin.username} ({existing_admin.email})")
            return
        
        # Create admin user
        admin_data = {
            'username': 'admin',
            'email': 'admin@hackuta.com',
            'password': 'AdminPass123!',  # Change this in production!
            'public_id': str(uuid.uuid4()),
            'is_admin': True
        }
        
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == admin_data['username']) | 
            (User.email == admin_data['email'])
        ).first()
        
        if existing_user:
            # Promote existing user to admin
            existing_user.is_admin = True
            db.session.commit()
            print(f"Promoted existing user to admin: {existing_user.username} ({existing_user.email})")
        else:
            # Create new admin user
            admin_user = User(
                public_id=admin_data['public_id'],
                username=admin_data['username'],
                email=admin_data['email'],
                is_admin=True
            )
            admin_user.set_password(admin_data['password'])
            
            db.session.add(admin_user)
            db.session.commit()
            
            print(f"Admin user created successfully!")
            print(f"Username: {admin_data['username']}")
            print(f"Email: {admin_data['email']}")
            print(f"Password: {admin_data['password']}")
            print("Please change the password after first login!")

if __name__ == '__main__':
    create_admin_user()
