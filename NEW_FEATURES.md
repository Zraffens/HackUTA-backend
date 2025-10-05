# New Features - API Documentation

## 1. Tags System

### Endpoints

- **GET /api/tags/** - List all tags with note counts (paginated)
- **POST /api/tags/** - Create a new tag (requires auth)
- **GET /api/tags/{id}** - Get a specific tag
- **DELETE /api/tags/{id}** - Delete a tag (requires auth)
- **GET /api/tags/{id}/notes** - Get all notes with this tag (respects visibility)
- **GET /api/tags/popular** - Get most popular tags by note count

## 2. Search & Filtering

### Endpoint

- **GET /api/notes/search** - Search and filter notes

### Query Parameters

- `q` - Search query (searches in title and description)
- `tags` - Comma-separated tag names
- `course_id` - Filter by course public ID
- `is_public` - Filter by visibility (true/false)
- `owner` - Filter by owner username
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 10, max: 100)

## 3. Pagination

All list endpoints now support pagination:

- **GET /api/notes/** - List public notes (paginated)
- **GET /api/notes/search** - Search results (paginated)
- **GET /api/notes/recommended** - Recommendations (paginated)
- **GET /api/users/me/bookmarks** - User bookmarks (paginated)

### Response Format

```json
{
  "items": [...],
  "total": 100,
  "pages": 10,
  "current_page": 1,
  "has_next": true,
  "has_prev": false
}
```

## 4. Bookmarks/Favorites

### Endpoints

- **POST /api/notes/{public_id}/bookmark** - Bookmark a note (requires auth)
- **DELETE /api/notes/{public_id}/bookmark** - Remove bookmark (requires auth)
- **GET /api/users/me/bookmarks** - Get current user's bookmarked notes (requires auth, paginated)

## 5. Statistics Tracking

### Automatic Tracking

- **View Count** - Incremented on GET /api/notes/{public_id}
- **Download Count** - Incremented on:
  - GET /api/notes/{public_id}/download/original
  - GET /api/notes/{public_id}/download/markdown

### Statistics Endpoints

- **GET /api/notes/{public_id}/stats** - Get note statistics

  - view_count, download_count, comment_count, collaborator_count, bookmark_count
  - reaction_counts (concise, detailed, readable)

- **GET /api/users/me/stats** - Get current user's statistics (requires auth)
  - total_notes, public_notes, private_notes
  - total_views, total_downloads
  - followers_count, following_count, bookmarks_count, comments_count

## 6. Recommendation System

### Endpoint

- **GET /api/notes/recommended** - Get personalized recommendations (requires auth, paginated)

### Recommendation Algorithm (Multi-Strategy)

1. **Tag-based** (weight: 3) - Notes with tags from user's bookmarked notes
2. **Social** (weight: 5) - Notes from users you follow
3. **Course-based** (weight: 4) - Notes from courses you're enrolled in
4. **Popularity** (weight: 1) - Popular notes by view count

Notes are scored and ranked. If no personalized recommendations exist, falls back to popular public notes.

## Database Changes

### New Tables

- `tag` - Tag entity (id, name, created_at)
- `note_tags` - Many-to-many association between notes and tags
- `user_bookmarks` - Many-to-many association for bookmarked notes (user_id, note_id, bookmarked_at)

### Updated Tables

- `note` - Added fields:

  - `view_count` (Integer, default: 0)
  - `download_count` (Integer, default: 0)
  - Relationships: `tags`, `bookmarked_by`

- `user` - Added relationship:
  - `bookmarked_notes` - Notes bookmarked by user

## Usage Examples

### Search for notes with tags

```
GET /api/notes/search?q=calculus&tags=math,physics&is_public=true&page=1&per_page=20
```

### Get recommendations

```
GET /api/notes/recommended?page=1&per_page=10
Authorization: Bearer <token>
```

### Bookmark a note

```
POST /api/notes/abc123/bookmark
Authorization: Bearer <token>
```

### Get your bookmarks

```
GET /api/users/me/bookmarks?page=1&per_page=20
Authorization: Bearer <token>
```

### Create a tag

```
POST /api/tags/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "calculus"
}
```

### Get note statistics

```
GET /api/notes/abc123/stats
```
