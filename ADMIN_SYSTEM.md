# Admin System Documentation

## Overview

The Note-Sharing Platform now includes a comprehensive admin system that allows administrators to manage users, notes, and view analytics. The system includes both API endpoints and a web-based dashboard interface.

## Admin User Setup

### Creating the First Admin User

1. Run the admin creation script:

   ```bash
   python create_admin.py
   ```

   This creates an admin user with:

   - **Username:** admin
   - **Email:** admin@hackuta.com
   - **Password:** AdminPass123!

   **⚠️ Important:** Change the password after first login!

### Making Existing Users Admin

You can promote existing users to admin through the admin dashboard or by updating the database directly.

## Admin Dashboard

### Accessing the Dashboard

- **URL:** `http://localhost:5000/admin`
- **Login:** Use admin credentials to access the dashboard

### Dashboard Features

#### 1. Dashboard Overview

- **User Statistics:** Total users, admin users, new registrations
- **Note Statistics:** Total notes, public/private counts, views, downloads
- **System Statistics:** Comments, bookmarks, tags, courses

#### 2. User Management

- **View all users** with pagination and search
- **Promote/Demote** users to/from admin
- **User details:** Registration date, note count, admin status
- **Search functionality** by username, email, or full name

#### 3. Note Management

- **View all notes** with filtering and search
- **Hide/Unhide** notes from public view
- **Filter by status:** Public, Private, OCR status
- **Note details:** Owner, views, downloads, OCR status

#### 4. Analytics

- **Popular notes** by views and downloads
- **User growth** statistics
- **System usage** metrics

## API Endpoints

### Authentication

All admin endpoints require:

1. Valid JWT token (obtained through `/api/auth/login`)
2. User must have `is_admin = True`

### Admin API Endpoints

#### Dashboard Statistics

```http
GET /api/admin/dashboard/stats
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "user_stats": {
    "total_users": 150,
    "admin_users": 3,
    "new_users_today": 5,
    "new_users_this_week": 23,
    "new_users_this_month": 78
  },
  "note_stats": {
    "total_notes": 1247,
    "public_notes": 1098,
    "private_notes": 149,
    "notes_today": 15,
    "notes_this_week": 89,
    "notes_this_month": 234,
    "total_views": 15678,
    "total_downloads": 4567
  },
  "system_stats": {
    "total_comments": 892,
    "total_bookmarks": 3456,
    "total_tags": 67,
    "total_courses": 23
  }
}
```

#### User Management

```http
GET /api/admin/users?page=1&per_page=20&search=john
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "users": [
    {
      "id": 1,
      "public_id": "user-uuid",
      "username": "john_doe",
      "email": "john@example.com",
      "full_name": "John Doe",
      "is_admin": false,
      "created_at": "2024-01-15T10:30:00Z",
      "notes_count": 15,
      "last_login": null
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8,
    "has_prev": false,
    "has_next": true
  }
}
```

#### User Actions

```http
POST /api/admin/users/{user_id}/action
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "action": "promote"  // promote, demote, suspend, activate
}
```

#### Note Management

```http
GET /api/admin/notes?page=1&per_page=20&search=calculus&status=public
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "notes": [
    {
      "id": 1,
      "public_id": "note-uuid",
      "title": "Calculus Notes Chapter 1",
      "owner_username": "student123",
      "is_public": true,
      "view_count": 245,
      "download_count": 67,
      "created_at": "2024-01-15T10:30:00Z",
      "ocr_status": "completed"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 1247,
    "pages": 63,
    "has_prev": false,
    "has_next": true
  }
}
```

#### Note Actions

```http
POST /api/admin/notes/{note_id}/action
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "action": "hide"  // hide, unhide, delete
}
```

#### Analytics

```http
GET /api/admin/analytics/popular-notes?limit=10
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "most_viewed": [
    {
      "id": "note-uuid",
      "title": "Physics Notes",
      "owner": "student123",
      "view_count": 245,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "most_downloaded": [
    {
      "id": "note-uuid",
      "title": "Math Solutions",
      "owner": "student456",
      "download_count": 89,
      "created_at": "2024-01-10T15:20:00Z"
    }
  ]
}
```

## Security Features

### Admin Authentication Decorator

The `@admin_required` decorator ensures:

- User is authenticated with valid JWT
- User has admin privileges (`is_admin = True`)
- Proper error responses for unauthorized access

### Protection Against Self-Demotion

Admins cannot demote themselves, preventing accidental loss of admin access.

### Role-Based Access Control

- Regular users: Cannot access admin endpoints
- Admin users: Full access to admin functionality
- System validates admin status on every request

## Database Changes

### User Model Updates

Added `is_admin` field to the User model:

```python
is_admin = db.Column(db.Boolean, default=False, nullable=False)
```

### Migration Applied

The database has been updated to include the admin field with proper defaults.

## Frontend Integration

### Admin Dashboard Features

1. **Single Page Application** - All admin functionality in one interface
2. **Responsive Design** - Works on desktop and mobile devices
3. **Real-time Updates** - Statistics and data refresh dynamically
4. **Search and Filtering** - Easy navigation through large datasets
5. **Pagination** - Efficient handling of large data sets

### Technology Stack

- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **Charts:** Chart.js for analytics visualization
- **Authentication:** JWT token-based
- **Responsive:** CSS Grid and Flexbox

## Usage Examples

### Login as Admin

1. Go to `http://localhost:5000/admin`
2. Enter admin credentials:
   - Email: `admin@hackuta.com`
   - Password: `AdminPass123!`
3. Access the dashboard

### Promote a User to Admin

1. Navigate to "User Management"
2. Search for the user
3. Click "Promote" button
4. User gains admin access immediately

### Hide Inappropriate Notes

1. Navigate to "Note Management"
2. Find the problematic note
3. Click "Hide" to remove from public view
4. Note becomes private instantly

### View System Statistics

1. Dashboard shows real-time statistics
2. Analytics section provides detailed insights
3. Popular notes help identify trending content

## Future Enhancements

### Planned Features

1. **User Suspension System** - Temporarily disable user accounts
2. **File Management** - Clean up orphaned files
3. **Audit Logs** - Track admin actions
4. **Email Notifications** - Alert users of admin actions
5. **Advanced Analytics** - More detailed usage insights
6. **Bulk Operations** - Select multiple items for batch actions

### Configuration Options

Future versions will include:

- Configurable admin permissions
- Custom admin roles
- Admin activity logging
- System maintenance tools

## Troubleshooting

### Common Issues

#### Cannot Access Admin Dashboard

- Verify user has `is_admin = True` in database
- Check JWT token is valid and not expired
- Ensure Flask application is running

#### 403 Access Denied

- User is not admin - check `is_admin` field
- Token may be expired - re-login required
- Admin decorator protection is working correctly

#### Statistics Not Loading

- Check database connections
- Verify all models are properly imported
- Check for database migration issues

### Admin User Recovery

If admin access is lost:

1. Run `python create_admin.py` to create new admin
2. Or manually update database: `UPDATE user SET is_admin = 1 WHERE email = 'user@email.com'`

## Security Considerations

### Production Deployment

1. **Change default admin password**
2. **Use HTTPS** for all admin traffic
3. **Implement rate limiting** for admin endpoints
4. **Enable audit logging** for admin actions
5. **Regular security updates** for dependencies

### Access Control

- Admin endpoints are protected by JWT + admin role check
- No bypassing of authentication mechanisms
- Proper error handling prevents information disclosure

## Conclusion

The admin system provides comprehensive platform management capabilities while maintaining security and usability. The web-based dashboard offers an intuitive interface for non-technical administrators, while the API endpoints support custom integrations and automation.

For technical support or feature requests, refer to the main project documentation or contact the development team.
