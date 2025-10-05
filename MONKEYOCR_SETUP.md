# MonkeyOCR Integration Setup Guide

## Overview

This guide will help you set up MonkeyOCR for automatic conversion of handwritten notes to markdown.

## Prerequisites

- Python 3.10
- CUDA 12.6 or 11.8 (for GPU acceleration)
- At least 8GB GPU memory recommended

## Installation Steps

### 1. Install MonkeyOCR

Create a separate conda environment for MonkeyOCR:

```bash
conda create -n MonkeyOCR python=3.10
conda activate MonkeyOCR

# Clone MonkeyOCR repository
git clone https://github.com/Yuliang-Liu/MonkeyOCR.git
cd MonkeyOCR

# Set CUDA version
export CUDA_VERSION=126  # for CUDA 12.6
# export CUDA_VERSION=118  # for CUDA 11.8

# Install PaddlePaddle
pip install paddlepaddle-gpu==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu${CUDA_VERSION}/

# Install PaddleX
pip install "paddlex[base]"

# Install PyTorch
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu126

# Install MonkeyOCR
pip install -e .

# Install LMDeploy (recommended backend)
pip install lmdeploy==0.9.2
```

### 2. Download Model Weights

```bash
pip install huggingface_hub

# Download MonkeyOCR-pro-3B model (recommended)
python tools/download_model.py -n MonkeyOCR-pro-3B

# OR download smaller MonkeyOCR model
# python tools/download_model.py -n MonkeyOCR
```

### 3. Test MonkeyOCR Installation

```bash
# Test with a sample file
python parse.py /path/to/sample.pdf -t text
```

### 4. Configure the Flask Application

Update the environment variable in your Flask app's `.env` file:

```env
MONKEYOCR_PATH=/full/path/to/MonkeyOCR
```

For example:

```env
MONKEYOCR_PATH=C:/Users/YourName/MonkeyOCR
```

Or on Linux/Mac:

```env
MONKEYOCR_PATH=/home/username/MonkeyOCR
```

### 5. Run Database Migrations

The Note model has been updated with new fields for OCR support:

```bash
cd d:\codes\hackUTA\note-sharing-platform
flask db migrate -m "Add OCR fields to Note model"
flask db upgrade
```

### 6. Create Upload Directories

```bash
mkdir -p uploads/notes
mkdir -p uploads/markdown
```

## How It Works

### File Upload Flow:

1. **User uploads a handwritten note** (PDF or image) via POST `/api/notes`
2. **Original file is saved** to `uploads/notes/`
3. **Note record is created** with `ocr_status='pending'`
4. **MonkeyOCR conversion starts**:
   - Status changes to `ocr_status='processing'`
   - MonkeyOCR converts the file to markdown
   - Markdown file is saved to `uploads/markdown/`
5. **Conversion completes**:
   - Status changes to `ocr_status='completed'`
   - `markdown_path` is updated with the file path
6. **Users can access**:
   - Original file via `/api/notes/<id>/download/original`
   - Markdown content via `/api/notes/<id>/markdown`
   - Markdown file via `/api/notes/<id>/download/markdown`

### API Endpoints:

- `POST /api/notes` - Upload note (triggers OCR)
- `GET /api/notes/<public_id>/ocr-status` - Check OCR conversion status
- `GET /api/notes/<public_id>/markdown` - Get markdown content
- `GET /api/notes/<public_id>/download/original` - Download original file
- `GET /api/notes/<public_id>/download/markdown` - Download markdown file

### OCR Status Values:

- `pending` - OCR conversion not started yet
- `processing` - OCR conversion in progress
- `completed` - OCR conversion successful, markdown available
- `failed` - OCR conversion failed

## Troubleshooting

### Issue: "out of resource: shared memory" error on RTX 30/40 series

Apply the LMDeploy patch:

```bash
cd MonkeyOCR
python tools/lmdeploy_patcher.py patch
```

### Issue: Conversion timeout

Increase the timeout in `app/services/ocr_service.py`:

```python
timeout=600  # Change from 300 to 600 seconds
```

### Issue: MonkeyOCR not found

Make sure:

1. `MONKEYOCR_PATH` environment variable is set correctly
2. MonkeyOCR is installed in that location
3. The Flask app can access that path

### Issue: Model not found

Download the model weights again:

```bash
cd MonkeyOCR
python tools/download_model.py -n MonkeyOCR-pro-3B
```

## Performance Notes

- **RTX 3090**: ~0.338 pages/second with LMDeploy
- **Transformers backend**: ~0.015 pages/second
- **Recommendation**: Use LMDeploy backend for best performance

## Future Improvements

- [ ] Implement async processing with Celery for better performance
- [ ] Add progress updates during conversion
- [ ] Support batch conversion
- [ ] Add retry logic for failed conversions
- [ ] Implement webhook notifications on completion

## Testing

Test the OCR integration:

```bash
# 1. Upload a note with a PDF
curl -X POST http://localhost:5000/api/notes \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Test Note" \
  -F "description=Test" \
  -F "is_public=true" \
  -F "file=@/path/to/handwritten_note.pdf"

# 2. Check OCR status
curl http://localhost:5000/api/notes/<public_id>/ocr-status

# 3. Get markdown content
curl http://localhost:5000/api/notes/<public_id>/markdown

# 4. Download markdown file
curl http://localhost:5000/api/notes/<public_id>/download/markdown -o note.md
```

## Additional Resources

- [MonkeyOCR GitHub](https://github.com/Yuliang-Liu/MonkeyOCR)
- [MonkeyOCR Documentation](https://github.com/Yuliang-Liu/MonkeyOCR/blob/main/README.md)
- [LMDeploy Documentation](https://github.com/InternLM/lmdeploy)
