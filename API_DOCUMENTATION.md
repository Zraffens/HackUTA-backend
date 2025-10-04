# Note-Sharing Platform API

## Overview

This is a comprehensive REST API for a student note-sharing platform built with Flask.

## Base URL

```
http://localhost:5000/api
```

## Interactive Documentation

Visit `http://localhost:5000/api/` for the Swagger UI documentation.

---

## Authentication Endpoints

### Register

- **POST** `/api/auth/register`
- **Body**: `{ "email": "user@email.com", "username": "username", "password": "password" }`
- **Response**: `{ "message": "User registered successfully" }`

### Login

- **POST** `/api/auth/login`
- **Body**: `{ "email": "user@email.com", "password": "password" }`
- **Response**: `{ "access_token": "...", "refresh_token": "..." }`

### Refresh Token

- **POST** `/api/auth/refresh`
- **Headers**: `Authorization: Bearer <refresh_token>`
- **Response**: `{ "access_token": "..." }`

### Logout

- **POST** `/api/auth/logout`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: `{ "message": "Successfully logged out" }`

---

## Notes Endpoints

### List All Public Notes

- **GET** `/api/notes`
- **Response**: Array of notes

### Create Note

- **POST** `/api/notes`
- **Headers**: `Authorization: Bearer <access_token>`
- **Content-Type**: `multipart/form-data`
- **Body**:
  - `title` (required): Note title
  - `description` (optional): Note description
  - `is_public` (optional, default=true): Public visibility
  - `file` (required): PDF file

### Get Note Details

- **GET** `/api/notes/<public_id>`
- **Response**: Note details

### Update Note

- **PUT** `/api/notes/<public_id>`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: `{ "title": "...", "description": "...", "is_public": true }`

### Delete Note

- **DELETE** `/api/notes/<public_id>`
- **Headers**: `Authorization: Bearer <access_token>`

---

## Comments Endpoints

### Get Comments for Note

- **GET** `/api/notes/<public_id>/comments`
- **Response**: Array of comments with author info

### Add Comment

- **POST** `/api/notes/<public_id>/comments`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: `{ "content": "Your comment here" }`

---

## Reactions Endpoints

### React to Note (Toggle)

- **POST** `/api/notes/<public_id>/react`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: `{ "reaction_type": "concise" }` (or "detailed", "readable")
- **Response**:

```json
{
  "message": "Reaction added/removed",
  "reactions": {
    "concise": 5,
    "detailed": 3,
    "readable": 8
  }
}
```

### Get Reaction Counts

- **GET** `/api/notes/<public_id>/react`
- **Response**:

```json
{
  "concise": 5,
  "detailed": 3,
  "readable": 8
}
```

---

## Collaborators Endpoints

### Get Note Collaborators

- **GET** `/api/notes/<public_id>/collaborators`
- **Response**: Array of collaborator users

### Add Collaborator

- **POST** `/api/notes/<public_id>/collaborators`
- **Headers**: `Authorization: Bearer <access_token>` (must be note owner)
- **Body**: `{ "username": "collaborator_username" }`

---

## Users Endpoints

### List All Users

- **GET** `/api/users`
- **Response**: Array of users

### Get User Profile

- **GET** `/api/users/<username>`
- **Response**:

```json
{
  "public_id": "...",
  "username": "...",
  "profile_bio": "...",
  "created_at": "...",
  "followers_count": 10,
  "following_count": 15,
  "notes_count": 5
}
```

### Follow User

- **POST** `/api/users/<username>/follow`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: `{ "message": "You are now following <username>" }`

### Unfollow User

- **POST** `/api/users/<username>/unfollow`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: `{ "message": "You have unfollowed <username>" }`

---

## Courses Endpoints

### List All Courses

- **GET** `/api/courses`
- **Response**: Array of courses

### Create Course

- **POST** `/api/courses`
- **Body**: `{ "name": "Computer Science 101", "code": "CS101" }`

### Get Course Details

- **GET** `/api/courses/<course_id>`
- **Response**: Course details

### Enroll in Courses

- **POST** `/api/courses/enroll`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: `{ "course_codes": ["CS101", "MATH203", "ENG101"] }`
- **Response**:

```json
{
  "message": "Enrolled in 3 course(s)",
  "courses": ["CS101", "MATH203", "ENG101"]
}
```

### Get My Courses

- **GET** `/api/courses/my-courses`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: Array of user's enrolled courses

---

## Database Setup

1. Run migrations:

```bash
flask db migrate -m "Initial migration"
flask db upgrade
```

2. Start the server:

```bash
python run.py
```

---

## Features Implemented

✅ **Authentication**: Register, login, logout, token refresh  
✅ **Notes CRUD**: Create, read, update, delete notes with PDF uploads  
✅ **Comments**: Add and view comments on notes  
✅ **Reactions**: Three types of reactions (concise, detailed, readable) with toggle functionality  
✅ **Collaborators**: Add collaborators to notes (owner only)  
✅ **User Following**: Follow/unfollow users  
✅ **User Profiles**: View user profiles with stats  
✅ **Courses**: Create courses, enroll in courses, view enrolled courses

---

## Next Steps / Future Features

- [ ] AI-powered note enhancement (placeholder endpoint ready)
- [ ] Recommendation system based on courses and following
- [ ] Note search and filtering by course/owner
- [ ] File download endpoints
- [ ] Notification system
- [ ] Rate limiting
- [ ] Pagination for large lists
