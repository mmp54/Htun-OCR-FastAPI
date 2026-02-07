from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid

from ocr import run_OCR

app = FastAPI()

# -----------------------------
# CORS (VERY IMPORTANT)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # later you can restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "OCR API is running 🎉"}

@app.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):

    # Unique temp filename (safe for multi users)
    temp_name = f"/tmp/{uuid.uuid4()}_{file.filename}"

    try:
        # Save uploaded image
        with open(temp_name, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Run OCR
        text = run_OCR(temp_name)

        return {
            "filename": file.filename,
            "text": text
        }

    finally:
        # Cleanup
        if os.path.exists(temp_name):
            os.remove(temp_name)
