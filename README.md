# Sizer AI

A FastAPI web app for resizing images to a chosen width and height using Pillow.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn src.app:app --reload
``
Open http://127.0.0.1:8000.

## Notes
- Accepts JPG, PNG, and WEBP images up to 8 MB.
- Width and height must be between 1 and 5000 pixels.
- Generated downloads use random filenames and the download endpoint only serves generated resize outputs.
