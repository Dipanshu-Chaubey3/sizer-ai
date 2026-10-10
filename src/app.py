from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image, UnidentifiedImageError

from .logic import resize_image

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
DOWNLOAD_DIR = BASE_DIR / "downloads"
TEMPLATE_DIR = BASE_DIR / "templates"
for folder in (STATIC_DIR, DOWNLOAD_DIR):
    folder.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Sizer AI")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
MAX_UPLOAD_BYTES = 8 * 1024 * 1024
MAX_DIMENSION = 5000
ALLOWED_FORMATS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/resize", response_class=HTMLResponse)
async def handle_resize(request: Request, file: UploadFile = File(...),
                        width: int = Form(...), height: int = Form(...)):
    if not (1 <= width <= MAX_DIMENSION and 1 <= height <= MAX_DIMENSION):
        raise HTTPException(status_code=400, detail=f"Width and height must be between 1 and {MAX_DIMENSION}.")
    contents = await file.read(MAX_UPLOAD_BYTES + 1)
    await file.close()
    if not contents:
        raise HTTPException(status_code=400, detail="Choose an image first.")
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image must be 8 MB or smaller.")
    try:
        from io import BytesIO
        with Image.open(BytesIO(contents)) as image:
            image.verify()
            image_format = image.format
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="Upload a valid JPG, PNG, or WEBP image.")
    if image_format not in ALLOWED_FORMATS:
        raise HTTPException(status_code=400, detail="Only JPG, PNG, and WEBP images are supported.")

    token = uuid4().hex
    input_path = STATIC_DIR / f"{token}{ALLOWED_FORMATS[image_format]}"
    output_filename = f"resized_{token}{ALLOWED_FORMATS[image_format]}"
    output_path = DOWNLOAD_DIR / output_filename
    input_path.write_bytes(contents)
    success = resize_image(str(input_path), str(output_path), width, height)
    input_path.unlink(missing_ok=True)
    if not success:
        raise HTTPException(status_code=422, detail="Could not resize this image.")
    return templates.TemplateResponse("index.html", {
        "request": request, "download_link": output_filename,
        "message": f"Success! Resized to {width} × {height} pixels."
    })

@app.get("/download/{filename}")
async def download_file(filename: str):
    # Only serve generated filenames, never arbitrary paths.
    if not filename.startswith("resized_") or Path(filename).name != filename:
        raise HTTPException(status_code=404, detail="File not found.")
    path = DOWNLOAD_DIR / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(path=str(path), filename=filename)
