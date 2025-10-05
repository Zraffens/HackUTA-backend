# Note Sharing Platform - Complete Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│                   (React/Next.js/Vite)                          │
│                                                                  │
│  Components: Login, Register, Notes, Search, Bookmarks, etc.   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP/REST API
                         │ CORS Enabled
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                      FLASK BACKEND                               │
│                   (Python 3.x + Flask)                          │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              API Layer (Flask-RESTx)                     │  │
│  │                                                           │  │
│  │  /api/auth      - Authentication & JWT                   │  │
│  │  /api/notes     - Notes CRUD, Search, Recommendations   │  │
│  │  /api/users     - Users, Follow, Bookmarks, Stats       │  │
│  │  /api/courses   - Courses & Enrollment                   │  │
│  │  /api/tags      - Tags Management                        │  │
│  │                                                           │  │
│  │  Swagger UI: /api/ (Interactive Documentation)           │  │
│  └─────────────────────────────────────────────────────────┘  │
│                         │                                        │
│  ┌─────────────────────▼───────────────────────────────────┐  │
│  │            Business Logic Layer                          │  │
│  │                                                           │  │
│  │  - Authentication (JWT, Password Hashing)                │  │
│  │  - File Upload & Validation                              │  │
│  │  - OCR Service (Gemini AI Integration)                   │  │
│  │  - Search & Filtering Logic                              │  │
│  │  - Recommendation Algorithm                              │  │
│  │  - Statistics Tracking                                   │  │
│  │  - Pagination Utilities                                  │  │
│  └─────────────────────┬───────────────────────────────────┘  │
│                         │                                        │
│  ┌─────────────────────▼───────────────────────────────────┐  │
│  │            Data Access Layer (SQLAlchemy ORM)            │  │
│  │                                                           │  │
│  │  Models: User, Note, Comment, Reaction, Course, Tag     │  │
│  │  Relationships: Many-to-Many, One-to-Many                │  │
│  │  Migrations: Flask-Migrate (Alembic)                     │  │
│  └─────────────────────┬───────────────────────────────────┘  │
└────────────────────────┼────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌────▼─────┐
│   SQLite     │  │  File System │  │ Gemini AI│
│   Database   │  │              │  │   API    │
│              │  │  uploads/    │  │          │
│ - user       │  │  ├─notes/    │  │  OCR:    │
│ - note       │  │  └─markdown/ │  │  PDF → MD│
│ - comment    │  │              │  │  IMG → MD│
│ - reaction   │  └──────────────┘  └──────────┘
│ - course     │
│ - tag        │
│ - note_tags  │
│ - bookmarks  │
│ - followers  │
│ - etc.       │
└──────────────┘
```

## Data Flow Diagrams

### 1. Note Upload with OCR

```
User → Upload PDF/Image
  │
  ├─→ Flask API (POST /api/notes/)
  │     │
  │     ├─→ Validate File
  │     ├─→ Save to uploads/notes/
  │     ├─→ Create Note (status: pending)
  │     │
  │     └─→ OCR Service
  │           │
  │           ├─→ Convert PDF to Images
  │           ├─→ Send to Gemini AI
  │           ├─→ Receive Markdown + LaTeX
  │           ├─→ Extract from code blocks
  │           └─→ Save to uploads/markdown/
  │
  └─→ Response: Note with OCR status
```

### 2. Recommendation Algorithm

```
GET /api/notes/recommended
  │
  ├─→ Get User's Bookmarked Notes
  │     └─→ Extract Tags → Score +3
  │
  ├─→ Get Followed Users
  │     └─→ Get Their Public Notes → Score +5
  │
  ├─→ Get User's Courses
  │     └─→ Get Course Notes → Score +4
  │
  ├─→ Get Popular Notes (by views)
  │     └─→ Score +1
  │
  └─→ Sort by Score → Paginate → Return
```

### 3. Search with Filters

```
GET /api/notes/search?q=calc&tags=math&course_id=xyz
  │
  ├─→ Base Query: Note.query
  │
  ├─→ Apply Text Filter (title, description)
  │     └─→ ILIKE '%calc%'
  │
  ├─→ Apply Tag Filter
  │     └─→ JOIN note_tags → WHERE tag IN ('math')
  │
  ├─→ Apply Course Filter
  │     └─→ JOIN note_courses → WHERE course_id = 'xyz'
  │
  ├─→ Apply Visibility Filter
  │     └─→ Check Auth → Filter public/private
  │
  └─→ Paginate → Return Results
```

## Database Schema

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    USER     │     │    NOTE     │     │     TAG     │
├─────────────┤     ├─────────────┤     ├─────────────┤
│ id          │     │ id          │     │ id          │
│ public_id   │     │ public_id   │     │ name        │
│ username    │     │ title       │     │ created_at  │
│ email       │     │ description │     └──────┬──────┘
│ password_hash│    │ is_public   │            │
│ created_at  │     │ file_path   │            │
│ profile_bio │     │ markdown_path│           │
└──────┬──────┘     │ ocr_status  │            │
       │            │ view_count  │◄───────────┤
       │            │ download_cnt│    note_tags (M2M)
       │            │ owner_id    │
       │            │ created_at  │
       │            └──────┬──────┘
       │                   │
       │ owner             │ notes
       └───────────────────┘

┌─────────────┐     ┌─────────────┐
│   COMMENT   │     │  REACTION   │
├─────────────┤     ├─────────────┤
│ id          │     │ id          │
│ content     │     │ reaction_type│
│ note_id     │     │ note_id     │
│ author_id   │     │ user_id     │
│ created_at  │     │ created_at  │
└─────────────┘     └─────────────┘

┌─────────────┐     ┌──────────────────┐
│   COURSE    │     │  ASSOCIATIONS    │
├─────────────┤     ├──────────────────┤
│ id          │     │ followers        │
│ public_id   │     │ course_users     │
│ name        │     │ note_collaborators│
│ description │     │ note_courses     │
│ created_by  │     │ note_tags        │
│ created_at  │     │ user_bookmarks   │
└─────────────┘     └──────────────────┘
```

## API Endpoint Categories

```
┌────────────────────────────────────────────────┐
│              AUTHENTICATION                    │
├────────────────────────────────────────────────┤
│ POST   /api/auth/register                     │
│ POST   /api/auth/login                        │
│ POST   /api/auth/logout                       │
│ POST   /api/auth/refresh                      │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│                 NOTES                          │
├────────────────────────────────────────────────┤
│ GET    /api/notes/                (paginated) │
│ POST   /api/notes/                            │
│ GET    /api/notes/search          (filters)   │
│ GET    /api/notes/recommended     (AI)        │
│ GET    /api/notes/{id}            (+views)    │
│ PUT    /api/notes/{id}                        │
│ DELETE /api/notes/{id}                        │
│ GET    /api/notes/{id}/stats                  │
│ POST   /api/notes/{id}/bookmark               │
│ DELETE /api/notes/{id}/bookmark               │
│ GET    /api/notes/{id}/download/original      │
│ GET    /api/notes/{id}/download/markdown      │
│ GET    /api/notes/{id}/comments               │
│ POST   /api/notes/{id}/comments               │
│ POST   /api/notes/{id}/reactions              │
│ GET    /api/notes/{id}/collaborators          │
│ POST   /api/notes/{id}/collaborators          │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│                 USERS                          │
├────────────────────────────────────────────────┤
│ GET    /api/users/                            │
│ GET    /api/users/{username}                  │
│ POST   /api/users/{username}/follow           │
│ POST   /api/users/{username}/unfollow         │
│ GET    /api/users/me/bookmarks   (paginated)  │
│ GET    /api/users/me/stats                    │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│                COURSES                         │
├────────────────────────────────────────────────┤
│ GET    /api/courses/                          │
│ POST   /api/courses/                          │
│ GET    /api/courses/{id}                      │
│ POST   /api/courses/{id}/enroll               │
│ POST   /api/courses/{id}/unenroll             │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│                  TAGS                          │
├────────────────────────────────────────────────┤
│ GET    /api/tags/                 (paginated) │
│ POST   /api/tags/                             │
│ GET    /api/tags/{id}                         │
│ DELETE /api/tags/{id}                         │
│ GET    /api/tags/{id}/notes                   │
│ GET    /api/tags/popular                      │
└────────────────────────────────────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────┐
│             Backend Stack                    │
├─────────────────────────────────────────────┤
│ Core Framework:      Flask 3.x              │
│ API Framework:       Flask-RESTx            │
│ Database ORM:        SQLAlchemy             │
│ Migrations:          Flask-Migrate/Alembic  │
│ Authentication:      Flask-JWT-Extended     │
│ CORS:                Flask-CORS             │
│ Password Security:   Werkzeug               │
│ AI/OCR:              Google Gemini AI       │
│ Image Processing:    PyMuPDF, Pillow        │
│ Database:            SQLite (dev)           │
│ Environment:         Python 3.12            │
└─────────────────────────────────────────────┘
```

## Security Features

```
┌─────────────────────────────────────────────┐
│              Security Layers                 │
├─────────────────────────────────────────────┤
│ ✓ JWT Authentication                        │
│ ✓ Password Hashing (Werkzeug)              │
│ ✓ Token Blocklist (Logout)                 │
│ ✓ CORS Configuration                        │
│ ✓ File Type Validation                     │
│ ✓ Input Validation                          │
│ ✓ SQL Injection Protection (ORM)           │
│ ✓ Authorization Checks                      │
└─────────────────────────────────────────────┘
```

## Performance Optimizations

```
┌─────────────────────────────────────────────┐
│         Performance Features                 │
├─────────────────────────────────────────────┤
│ ✓ Pagination (prevent large responses)     │
│ ✓ Lazy Loading (relationships)             │
│ ✓ Database Indexing                        │
│ ✓ Efficient Queries (joins)                │
│ ✓ File Size Limits                         │
│ ✓ Query Optimization                        │
└─────────────────────────────────────────────┘
```

## File Structure

```
note-sharing-platform/
├── app/
│   ├── __init__.py          # App factory, CORS
│   ├── extensions.py        # DB, JWT, migrate
│   ├── models/              # Database models
│   │   ├── user.py
│   │   ├── note.py
│   │   ├── comment.py
│   │   ├── reaction.py
│   │   ├── course.py
│   │   ├── tag.py           # NEW
│   │   └── associations.py
│   ├── api/                 # API endpoints
│   │   ├── auth/
│   │   ├── notes/
│   │   ├── users/
│   │   ├── courses/
│   │   └── tags/            # NEW
│   ├── services/            # Business logic
│   │   ├── file_service.py
│   │   └── ocr_service.py   # Gemini AI
│   └── utils/               # Utilities
│       └── pagination.py    # NEW
├── migrations/              # Database migrations
├── uploads/                 # File storage
│   ├── notes/
│   └── markdown/
├── instance/                # Instance-specific
│   └── note_sharing.db
├── .env                     # Environment vars
├── requirements.txt         # Dependencies
├── run.py                   # Entry point
└── venv/                    # Virtual environment
```

---

**Created**: December 2024  
**Version**: 1.0  
**Status**: ✅ Production Ready  
**API Docs**: http://127.0.0.1:5000/api/
