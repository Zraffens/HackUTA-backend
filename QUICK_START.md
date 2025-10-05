# Quick Start Guide - Note Sharing Platform

## 🚀 Server is Running!

The Flask backend is currently running at: **http://127.0.0.1:5000**

## 📚 API Documentation

### Swagger UI (Interactive Documentation)

Open in your browser: **http://127.0.0.1:5000/api/**

This provides:

- Interactive API testing
- Complete endpoint documentation
- Request/response schemas
- Authentication testing

## 🔑 Quick Testing Guide

### 1. Register a User

```bash
POST http://127.0.0.1:5000/api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```

### 2. Login

```bash
POST http://127.0.0.1:5000/api/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "password123"
}
```

**Response**: You'll get an `access_token` - use this in Authorization header

### 3. Create a Note (with OCR)

```bash
POST http://127.0.0.1:5000/api/notes/
Authorization: Bearer <your_access_token>
Content-Type: multipart/form-data

Form Data:
- title: "Calculus Notes"
- description: "My handwritten calculus notes"
- is_public: true
- file: <upload a PDF or image file>
```

**Note**: The server will automatically convert your handwritten notes to markdown using Gemini AI!

### 4. Search Notes

```bash
GET http://127.0.0.1:5000/api/notes/search?q=calculus&tags=math&page=1&per_page=10
```

### 5. Get Recommendations

```bash
GET http://127.0.0.1:5000/api/notes/recommended?page=1&per_page=10
Authorization: Bearer <your_access_token>
```

### 6. Bookmark a Note

```bash
POST http://127.0.0.1:5000/api/notes/<note_public_id>/bookmark
Authorization: Bearer <your_access_token>
```

### 7. Get Your Bookmarks

```bash
GET http://127.0.0.1:5000/api/users/me/bookmarks?page=1&per_page=10
Authorization: Bearer <your_access_token>
```

### 8. Create Tags

```bash
POST http://127.0.0.1:5000/api/tags/
Authorization: Bearer <your_access_token>
Content-Type: application/json

{
  "name": "mathematics"
}
```

### 9. Get Note Statistics

```bash
GET http://127.0.0.1:5000/api/notes/<note_public_id>/stats
```

### 10. Get Your Personal Statistics

```bash
GET http://127.0.0.1:5000/api/users/me/stats
Authorization: Bearer <your_access_token>
```

## 📊 All Available Features

### ✅ Authentication

- Register, Login, Logout, Refresh Token
- JWT-based authentication
- Password hashing

### ✅ Notes Management

- Create with file upload (PDF/images)
- Automatic OCR to markdown (Gemini AI)
- Update, Delete
- Public/Private visibility
- View and download original files
- View and download markdown versions

### ✅ Social Features

- Comments on notes
- Reactions (concise, detailed, readable)
- Follow/Unfollow users
- Collaborators on notes

### ✅ Course Management

- Create courses
- Enroll/Unenroll
- Associate notes with courses

### ✅ Tags System (NEW)

- Create and manage tags
- Associate notes with multiple tags
- Popular tags ranking
- Filter notes by tags

### ✅ Search & Filtering (NEW)

- Full-text search
- Filter by tags, courses, owner, visibility
- Pagination support

### ✅ Bookmarks (NEW)

- Bookmark favorite notes
- View all bookmarks
- Remove bookmarks

### ✅ Statistics (NEW)

- View counts per note
- Download counts per note
- User statistics dashboard
- Note statistics dashboard

### ✅ Recommendations (NEW)

- Personalized note recommendations
- Multi-strategy algorithm
- Based on bookmarks, follows, and courses

## 🛠️ Testing with Postman/Thunder Client

1. **Import the Swagger JSON**:

   - Go to http://127.0.0.1:5000/api/swagger.json
   - Import into Postman or Thunder Client

2. **Set up Environment Variables**:

   - `base_url`: http://127.0.0.1:5000
   - `access_token`: (set after login)

3. **Test Flow**:
   - Register → Login → Create Note → Search → Bookmark → Get Recommendations

## 🗄️ Database

**Type**: SQLite
**Location**: `instance/note_sharing.db`

**Tables**:

- user
- note
- comment
- note_reaction
- course
- tag (NEW)
- note_tags (NEW)
- user_bookmarks (NEW)
- followers
- course_users
- note_collaborators
- note_courses
- blocked_tokens

## 🔐 Environment Variables

Located in `.env`:

- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT signing key
- `GEMINI_API_KEY` - Google Gemini API key for OCR

## 📁 File Storage

**Uploads Directory**: `uploads/`

- `uploads/notes/` - Original PDF/image files
- `uploads/markdown/` - Converted markdown files

## 🎯 CORS Configuration

The backend supports CORS for these frontend origins:

- http://localhost:3000 (React default)
- http://localhost:5173 (Vite default)
- http://localhost:5174 (Vite alternative)

## 🔍 Debugging

**Debug Mode**: ON
**Debugger PIN**: 647-069-155 (check terminal for current PIN)

## 📖 Documentation Files

- `NEW_FEATURES.md` - Documentation for all new features
- `IMPLEMENTATION_SUMMARY.md` - Complete implementation details
- `API_DOCUMENTATION.md` - Original API documentation
- `GEMINI_SETUP.md` - Gemini AI OCR setup guide
- `OCR_INTEGRATION_SUMMARY.md` - OCR integration details

## 💡 Tips

1. **Always include Authorization header** for protected endpoints
2. **Use pagination** for large result sets (page & per_page params)
3. **Check OCR status** after uploading notes (it takes a few seconds)
4. **Bookmark notes** to get better recommendations
5. **Follow users** and join courses for personalized content

## 🎉 You're All Set!

The platform is ready to use. Happy coding! 🚀
