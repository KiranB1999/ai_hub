from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import ollama
import fitz  # PyMuPDF for PDF handling
from pydantic import BaseModel
import os

app = FastAPI()

# ✅ FULLY ENABLE CORS (Fixing "Access-Control-Allow-Origin" issue)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow ALL origins (use specific frontend URL later)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# ✅ Model for handling chat messages
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    prompt = f"User: {request.message}\nDeepSeek:"
    response = ollama.chat(model="deepseek-r1:8b", messages=[{"role": "user", "content": prompt}], stream=False)
    return {"response": response["message"]["content"]}

# ✅ API to handle PDF uploads and extract text
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"

    # Save the uploaded file
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Extract text from the PDF
    doc = fitz.open(file_path)
    extracted_text = "\n".join([page.get_text() for page in doc])

    return {"text": extracted_text}
