# Admin System Troubleshooting Guide

## Common Issues and Solutions

### 1. "Admin access required" Error During Login

**Problem:** Admin dashboard shows "Admin access required" even with correct credentials.

**Causes & Solutions:**

#### A) Missing `/api/users/profile` endpoint

- **Fixed in latest commit** - The endpoint now exists
- Endpoint returns user profile including `is_admin` field

#### B) User doesn't have admin privileges

```bash
# Check if user is admin in database
python -c "
from app import create_app
from app.models import User
app = create_app()
with app.app_context():
    user = User.query.filter_by(email='admin@hackuta.com').first()
    print(f'User: {user.username if user else None}')
    print(f'Is Admin: {user.is_admin if user else None}')
"
```

#### C) Promote existing user to admin

```bash
# If user exists but isn't admin, promote them
python -c "
from app import create_app
from app.models import User
from app.extensions import db
app = create_app()
with app.app_context():
    user = User.query.filter_by(email='admin@hackuta.com').first()
    if user:
        user.is_admin = True
        db.session.commit()
        print('User promoted to admin')
    else:
        print('User not found')
"
```

### 2. Database Migration Issues

**Problem:** Migration fails with "Cannot add NOT NULL column"

**Solution:** Already fixed in migration file with `server_default='0'`

### 3. TypeError: NoneType and int Issues

**Problem:** `TypeError: unsupported operand type(s) for +=: 'NoneType' and 'int'`

**Fixed in latest commit:**

- Added null checks before incrementing counters
- Updated existing database records with default values

### 4. Admin User Creation

**Create first admin user:**

```bash
python create_admin.py
```

**Default credentials:**

- Email: `admin@hackuta.com`
- Password: `AdminPass123!`
- **Change password after first login!**

### 5. SQLAlchemy Relationship Conflicts

**Problem:** Backref conflicts between User and Note models

**Fixed:** Removed duplicate `bookmarked_notes` relationship from User model

### 6. API Endpoint Issues

**Test admin endpoints:**

```bash
# Login and get token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@hackuta.com","password":"AdminPass123!"}'

# Test profile endpoint
curl -X GET http://localhost:5000/api/users/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Test admin stats
curl -X GET http://localhost:5000/api/admin/dashboard/stats \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 7. Frontend Issues

**Admin dashboard not loading:**

- Ensure Flask app is running on port 5000
- Check browser console for JavaScript errors
- Verify API endpoints are accessible

**Login form issues:**

- Check network tab for failed requests
- Verify CORS settings allow requests
- Ensure JWT tokens are being stored correctly

### 8. Database Integrity

**Check admin field exists:**

```sql
-- Direct database query
sqlite3 instance/note_sharing.db "PRAGMA table_info(user);"
```

**Update counters for existing notes:**

```bash
python -c "
from app import create_app
from app.models import Note
from app.extensions import db
app = create_app()
with app.app_context():
    Note.query.filter(Note.view_count.is_(None)).update({'view_count': 0})
    Note.query.filter(Note.download_count.is_(None)).update({'download_count': 0})
    db.session.commit()
    print('Updated null counters')
"
```

## Quick Fixes Applied

1. ✅ Added `/api/users/profile` endpoint with `is_admin` field
2. ✅ Fixed null value errors in notes controller
3. ✅ Updated database records with proper defaults
4. ✅ Fixed migration with proper server defaults
5. ✅ Resolved SQLAlchemy relationship conflicts

## Admin Dashboard Access

1. **URL:** `http://localhost:5000/admin`
2. **Login:** `admin@hackuta.com` / `AdminPass123!`
3. **Features:** User management, note management, analytics
4. **API Base:** `/api/admin/*` endpoints

## Production Checklist

- [ ] Change default admin password
- [ ] Enable HTTPS for admin routes
- [ ] Set up proper logging for admin actions
- [ ] Configure backup strategy for admin data
- [ ] Implement rate limiting for admin endpoints
- [ ] Add audit trail for admin operations

## Support

If issues persist:

1. Check Flask application logs
2. Verify database migrations are applied
3. Test API endpoints directly with curl/Postman
4. Check browser developer console for errors
5. Ensure all dependencies are installed in virtual environment
