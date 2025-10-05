# MonkeyOCR Integration Summary

## What Was Done

### ✅ Database Changes

1. **Updated Note Model** (`app/models/note.py`):
   - Added `markdown_path` field to store the converted markdown file path
   - Added `ocr_status` field to track conversion status (pending, processing, completed, failed)
   - Original `file_path` still stores the handwritten note (PDF/image)

### ✅ New Services Created

2. **OCR Service** (`app/services/ocr_service.py`):

   - `MonkeyOCRService` class for handling OCR conversions
   - `convert_to_markdown()` method that calls MonkeyOCR's `parse.py` script
   - Handles file conversion with proper error handling and logging
   - Saves markdown output to `uploads/markdown/` directory

3. **Updated File Service** (`app/services/file_service.py`):
   - Extended allowed file types to include: PDF, JPG, JPEG, PNG
   - Added helper function `get_file_extension()`

### ✅ API Endpoints Added

4. **New Endpoints in Notes Controller**:

   - **GET** `/api/notes/<public_id>/ocr-status` - Check OCR conversion status
   - **GET** `/api/notes/<public_id>/markdown` - Get markdown content as JSON
   - **GET** `/api/notes/<public_id>/download/original` - Download original handwritten note
   - **GET** `/api/notes/<public_id>/download/markdown` - Download markdown file

5. **Modified Endpoint**:
   - **POST** `/api/notes` - Now triggers OCR conversion after file upload

### ✅ Documentation Created

6. **Setup Guide** (`MONKEYOCR_SETUP.md`):
   - Complete installation instructions for MonkeyOCR
   - Configuration steps for Flask integration
   - Troubleshooting guide
   - Testing examples

## File Structure

```
note-sharing-platform/
├── app/
│   ├── models/
│   │   └── note.py                    # ✨ Updated with OCR fields
│   ├── services/
│   │   ├── file_service.py           # ✨ Updated with image support
│   │   └── ocr_service.py            # ✨ NEW - OCR conversion service
│   └── api/
│       └── notes/
│           ├── controller.py          # ✨ Updated with OCR endpoints
│           └── dto.py                 # ✨ Updated with OCR status fields
├── uploads/
│   ├── notes/                         # Original handwritten files
│   └── markdown/                      # Converted markdown files
├── MONKEYOCR_SETUP.md                 # ✨ NEW - Setup guide
└── requirements.txt
```

## Next Steps (Before Testing)

### 1. Install MonkeyOCR (Outside Flask Environment)

```bash
# Create separate conda environment
conda create -n MonkeyOCR python=3.10
conda activate MonkeyOCR

# Clone and install MonkeyOCR
git clone https://github.com/Yuliang-Liu/MonkeyOCR.git
cd MonkeyOCR

# Follow installation steps from MONKEYOCR_SETUP.md
```

### 2. Configure Environment Variable

Add to `.env` file:

```env
MONKEYOCR_PATH=/full/path/to/MonkeyOCR
```

### 3. Run Database Migration

```bash
flask db migrate -m "Add OCR fields to Note model"
flask db upgrade
```

### 4. Create Upload Directories

```bash
mkdir uploads/markdown
```

### 5. Test the Integration

```bash
# Start the Flask app
python run.py

# Upload a handwritten note
# Check OCR status
# Retrieve markdown content
```

## How It Works

### Upload Flow:

```
1. User uploads PDF/image via POST /api/notes
   ↓
2. File saved to uploads/notes/
   ↓
3. Note created with ocr_status='pending'
   ↓
4. OCR conversion starts (ocr_status='processing')
   ↓
5. MonkeyOCR converts file to markdown
   ↓
6. Markdown saved to uploads/markdown/
   ↓
7. Note updated with markdown_path and ocr_status='completed'
   ↓
8. Users can access both original and markdown versions
```

### Data Storage:

- **Original File**: `uploads/notes/abc123_note.pdf`
- **Markdown File**: `uploads/markdown/note_<public_id>.md`
- **Database**: Both paths stored in Note model

## API Usage Examples

### 1. Upload Note (Triggers OCR)

```bash
POST /api/notes
Content-Type: multipart/form-data

{
  "title": "Calculus Notes",
  "description": "Chapter 5",
  "is_public": true,
  "file": <PDF/image file>
}

Response:
{
  "public_id": "abc-123",
  "title": "Calculus Notes",
  "ocr_status": "processing",
  ...
}
```

### 2. Check OCR Status

```bash
GET /api/notes/abc-123/ocr-status

Response:
{
  "public_id": "abc-123",
  "title": "Calculus Notes",
  "ocr_status": "completed",
  "has_markdown": true,
  "markdown_path": "uploads/markdown/note_abc-123.md"
}
```

### 3. Get Markdown Content

```bash
GET /api/notes/abc-123/markdown

Response:
{
  "status": "completed",
  "markdown": "# Calculus Notes\n\n## Chapter 5\n...",
  "file_path": "uploads/markdown/note_abc-123.md"
}
```

### 4. Download Files

```bash
# Download original
GET /api/notes/abc-123/download/original

# Download markdown
GET /api/notes/abc-123/download/markdown
```

## Important Notes

⚠️ **IMPORTANT**:

- MonkeyOCR must be installed in a SEPARATE environment (not the Flask venv)
- The Flask app calls MonkeyOCR via subprocess
- Ensure `MONKEYOCR_PATH` points to the correct installation directory

🔒 **Security**:

- Original files and markdown files are stored separately
- Access control should be implemented for private notes
- File paths are stored in the database, not exposed directly

⚡ **Performance**:

- OCR conversion happens synchronously (blocks the upload request)
- For production, consider implementing async processing with Celery
- Typical conversion time: 3-10 seconds per page with GPU

📝 **Status Tracking**:

- `pending` - Conversion not started
- `processing` - Conversion in progress
- `completed` - Markdown available
- `failed` - Conversion failed (check logs)

## Troubleshooting

If OCR conversion fails:

1. Check logs for error messages
2. Verify MonkeyOCR installation
3. Test MonkeyOCR directly: `python parse.py test.pdf -t text`
4. Check file permissions on upload directories
5. Ensure CUDA is properly configured for GPU acceleration

## Future Enhancements

- [ ] Async processing with Celery
- [ ] Progress tracking for long conversions
- [ ] Batch conversion support
- [ ] Webhook notifications
- [ ] Retry failed conversions
- [ ] OCR quality metrics
- [ ] Support for multi-page PDFs with page splitting
