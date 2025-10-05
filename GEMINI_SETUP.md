# Gemini OCR Setup Guide

## ✅ What Changed

We've replaced MonkeyOCR with **Google Gemini AI** for OCR conversion. This is:

- ✅ Much lighter (no heavy models to download)
- ✅ More accurate for handwritten notes
- ✅ Supports LaTeX math equations
- ✅ Cloud-based (no local compute needed)
- ✅ Simple to set up

## 🔑 Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Get API key" or "Create API key"
3. Copy your API key

## ⚙️ Configuration

1. Open `.env` file in the project root
2. Replace `your_gemini_api_key_here` with your actual API key:
   ```
   GEMINI_API_KEY=AIzaSy...your_actual_key_here
   ```

## 📦 Dependencies

Already installed:

- `google-genai` - Gemini AI SDK
- `Pillow` - Image processing
- `PyMuPDF` - PDF to image conversion

## 🚀 How It Works

### Upload Flow:

1. User uploads PDF/image via POST /api/notes
2. Backend converts PDF pages to images (if needed)
3. Each image is sent to Gemini 2.0 Flash for OCR
4. Gemini returns markdown with:
   - Extracted text
   - LaTeX equations ($ inline $ and $$ block $$)
   - Proper formatting (headers, lists, tables)
5. Markdown saved to `uploads/markdown/`
6. Both original and markdown accessible via API

### Features:

- **Handwritten notes** → Clean markdown text
- **Math equations** → LaTeX format
- **Multi-page PDFs** → Each page processed separately
- **Diagrams** → Described in [Image: ...] format
- **Tables** → Markdown table format

## 📝 API Usage

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
  "ocr_status": "processing",
  ...
}
```

### 2. Get Markdown

```bash
GET /api/notes/abc-123/markdown

Response:
{
  "status": "completed",
  "markdown": "# Chapter 5\n\n## Derivatives\n\n...",
  "file_path": "uploads/markdown/note_abc-123.md"
}
```

### 3. Download Files

```bash
GET /api/notes/abc-123/download/original  # Original PDF/image
GET /api/notes/abc-123/download/markdown  # Converted markdown
```

## 🎯 Models Used

- **Gemini 2.0 Flash Experimental** - Latest, fastest model
  - Excellent for handwritten text
  - Supports vision + text understanding
  - Optimized for structured output
  - API: `gemini-2.0-flash-exp`

## 📚 Implementation Details

The OCR service uses the new Google Gen AI SDK:

```python
from google import genai
from google.genai import types

# Initialize client
client = genai.Client(api_key='YOUR_API_KEY')

# Generate content with image
response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents=[prompt, types.Part.from_image(pil_image)]
)
```

## 💰 Pricing

Gemini 2.0 Flash (Free tier):

- 15 requests per minute
- 1,500 requests per day
- 1 million tokens per day

For production, you may need to upgrade to paid plan.

## 🔧 Troubleshooting

### "GEMINI_API_KEY not configured"

- Make sure you added your API key to `.env`
- Restart the Flask server after updating `.env`

### "Error processing with Gemini"

- Check your API key is valid
- Ensure you haven't exceeded rate limits (15/min, 1500/day)
- Check internet connection

### "No markdown content generated"

- The image might be too blurry
- Try with a clearer image/PDF
- Check Flask logs for detailed error

## 🗑️ Cleanup

MonkeyOCR files can be safely deleted:

```powershell
Remove-Item -Recurse -Force D:\codes\hackUTA\MonkeyOCR
```

## 🎉 Advantages Over MonkeyOCR

| Feature      | MonkeyOCR              | Gemini AI             |
| ------------ | ---------------------- | --------------------- |
| Setup        | Complex (7.5GB models) | Simple (API key only) |
| Memory       | 25GB+ RAM needed       | No local resources    |
| Speed        | 30-60s per page (CPU)  | 2-5s per page         |
| Accuracy     | Good                   | Excellent             |
| Math Support | Basic                  | LaTeX formatting      |
| Maintenance  | Model updates needed   | Always latest model   |
| Cost         | Free (but heavy)       | Free tier available   |

## 📚 Documentation

- [Gemini AI Docs](https://ai.google.dev/docs)
- [Python SDK](https://github.com/google/generative-ai-python)
- [Rate Limits](https://ai.google.dev/pricing)
