from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
import os

from ocr import run_OCR

app = FastAPI()

@app.get("/")
def home():
    return {"message": "OCR API is running 🎉"}

@app.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):

    # Save uploaded image
    image_path = f"temp_{file.filename}"
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run OCR
    text = run_OCR(image_path)

    # Delete temp image
    os.remove(image_path)

    return JSONResponse({
        "filename": file.filename,
        "text": text
    })

