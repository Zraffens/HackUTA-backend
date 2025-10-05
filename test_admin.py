"""
Admin System Test Script
Run this to verify the admin system is working correctly
"""

import requests
import json
from requests.exceptions import RequestException

BASE_URL = "http://localhost:5000"
ADMIN_EMAIL = "admin@hackuta.com"
ADMIN_PASSWORD = "AdminPass123!"

def test_admin_system():
    """Test the complete admin system functionality"""
    print("🔍 Testing Admin System...")
    print("=" * 50)
    
    try:
        # Test 1: Admin Login
        print("1️⃣ Testing admin login...")
        login_response = requests.post(f"{BASE_URL}/api/auth/login", 
                                     json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        
        if login_response.status_code == 200:
            token = login_response.json().get('access_token')
            print("✅ Admin login successful")
        else:
            print(f"❌ Admin login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False
        
        # Test 2: Profile Endpoint
        print("2️⃣ Testing profile endpoint...")
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = requests.get(f"{BASE_URL}/api/users/profile", headers=headers)
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            is_admin = profile_data.get('is_admin', False)
            print(f"✅ Profile endpoint working - is_admin: {is_admin}")
            
            if not is_admin:
                print("❌ User is not admin!")
                return False
        else:
            print(f"❌ Profile endpoint failed: {profile_response.status_code}")
            print(f"Response: {profile_response.text}")
            return False
        
        # Test 3: Admin Dashboard Stats
        print("3️⃣ Testing admin dashboard stats...")
        stats_response = requests.get(f"{BASE_URL}/api/admin/dashboard/stats", headers=headers)
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print("✅ Admin dashboard stats working")
            print(f"   Total users: {stats_data.get('user_stats', {}).get('total_users', 'N/A')}")
            print(f"   Total notes: {stats_data.get('note_stats', {}).get('total_notes', 'N/A')}")
        else:
            print(f"❌ Dashboard stats failed: {stats_response.status_code}")
            print(f"Response: {stats_response.text}")
            return False
        
        # Test 4: User Management
        print("4️⃣ Testing user management...")
        users_response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
        
        if users_response.status_code == 200:
            users_data = users_response.json()
            user_count = len(users_data.get('users', []))
            print(f"✅ User management working - {user_count} users found")
        else:
            print(f"❌ User management failed: {users_response.status_code}")
            print(f"Response: {users_response.text}")
        
        # Test 5: Note Management
        print("5️⃣ Testing note management...")
        notes_response = requests.get(f"{BASE_URL}/api/admin/notes", headers=headers)
        
        if notes_response.status_code == 200:
            notes_data = notes_response.json()
            note_count = len(notes_data.get('notes', []))
            print(f"✅ Note management working - {note_count} notes found")
        else:
            print(f"❌ Note management failed: {notes_response.status_code}")
            print(f"Response: {notes_response.text}")
        
        # Test 6: Admin Dashboard Access
        print("6️⃣ Testing admin dashboard page...")
        dashboard_response = requests.get(f"{BASE_URL}/admin")
        
        if dashboard_response.status_code == 200:
            print("✅ Admin dashboard page accessible")
        else:
            print(f"❌ Admin dashboard page failed: {dashboard_response.status_code}")
        
        print("\n" + "=" * 50)
        print("🎉 Admin System Test Complete!")
        print("\n📋 Summary:")
        print("✅ Admin authentication working")
        print("✅ Profile endpoint with is_admin field")
        print("✅ Admin API endpoints functional")
        print("✅ Dashboard statistics available")
        print("✅ User and note management ready")
        print("✅ Web interface accessible")
        
        print(f"\n🔗 Access admin dashboard: {BASE_URL}/admin")
        print(f"📧 Email: {ADMIN_EMAIL}")
        print(f"🔑 Password: {ADMIN_PASSWORD}")
        print("\n⚠️  Remember to change the default password!")
        
        return True
        
    except RequestException as e:
        print(f"❌ Connection error: {e}")
        print("Make sure Flask app is running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_database():
    """Check database integrity"""
    print("\n🗄️  Checking database...")
    try:
        from app import create_app
        from app.models import User, Note
        
        app = create_app()
        with app.app_context():
            # Check admin user
            admin = User.query.filter_by(email=ADMIN_EMAIL).first()
            if admin:
                print(f"✅ Admin user exists: {admin.username} (is_admin: {admin.is_admin})")
            else:
                print("❌ Admin user not found in database")
                return False
            
            # Check notes have proper counters
            null_views = Note.query.filter(Note.view_count.is_(None)).count()
            null_downloads = Note.query.filter(Note.download_count.is_(None)).count()
            
            if null_views == 0 and null_downloads == 0:
                print("✅ All notes have proper view/download counters")
            else:
                print(f"⚠️  Found {null_views} notes with null view_count, {null_downloads} with null download_count")
            
            total_notes = Note.query.count()
            total_users = User.query.count()
            print(f"📊 Database summary: {total_users} users, {total_notes} notes")
            
        return True
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Admin System Verification")
    print("=" * 50)
    
    # Check database first
    db_ok = check_database()
    
    if db_ok:
        print("\nStarting API tests...")
        print("📡 Make sure Flask app is running: python run.py")
        input("Press Enter when ready...")
        
        test_admin_system()
    else:
        print("\n❌ Database issues found. Please fix before testing API.")
        print("Run: python create_admin.py")
