from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import shutil
import os
from .logic import resize_image

app = FastAPI()

# Create folders if they don't exist
for folder in ["static", "downloads"]:
    if not os.path.exists(folder):
        os.makedirs(folder)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/resize")
async def handle_resize(
    request: Request, 
    file: UploadFile = File(...), 
    width: int = Form(...), 
    height: int = Form(...)
):
    input_path = f"static/{file.filename}"
    output_filename = f"resized_{file.filename}"
    output_path = f"downloads/{output_filename}"
    
    # Save original
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Process resize
    success = resize_image(input_path, output_path, width, height)
    
    if success:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "download_link": output_filename,
            "message": f"Success! Resized to {width}x{height}"
        })
    return {"error": "Processing failed"}

@app.get("/download/{filename}")
async def download_file(filename: str):
    return FileResponse(path=f"downloads/{filename}", filename=filename)