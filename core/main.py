from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from google.generativeai.types import RequestOptions
import fitz  # This is the correct import for PyMuPDF
from PIL import Image
import io
from fastapi import UploadFile, File, HTTPException

app = FastAPI()

# --- PROFESSIONAL CORS CONFIGURATION ---
origins = [
    "http://localhost:3000",
    "https://tripura-library-live.vercel.app", # Primary Alias
    "https://tripura-library-live-4r18s168e-riyanka-bhowmiks-projects.vercel.app" # Deployment URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "online", "version": "1.0.1"}

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Update the Request Model to accept Audio
class AIRequest(BaseModel):
    query: str = ""
    audio_data: str = None  # This will hold the voice recording (Base64)

@app.post("/ask_ai")
def ask_ai(request: AIRequest):
    try:
        # Using a fixed version '001' is more stable than 'latest'
        model = genai.GenerativeModel('gemini-2.5-flash') 

        if request.audio_data:
            # Voice Mode
            response = model.generate_content([
                "Answer this voice request concisely.",
                {"mime_type": "audio/mp4", "data": request.audio_data}
            ])
        else:
            # Text Mode
            response = model.generate_content(request.query)

        if response and response.text:
            return {"answer": response.text}
        else:
            return {"answer": "AI processed the request but the response was empty."}

    except Exception as e:
        # This sends the ACTUAL error message to your phone screen
        return {"answer": f"Backend Error: {str(e)}"}

@app.post("/api/extract-metadata")
async def extract_metadata(file: UploadFile = File(...)):
    # 1. Read the PDF content
    pdf_content = await file.read()
    doc = fitz.open(stream=pdf_content, filetype="pdf")
    
    # 2. Extract text from the first two pages for metadata
    text_sample = ""
    for i in range(min(2, len(doc))):
        text_sample += doc[i].get_text()

    # 3. Extract the first page as an image (Cover Page)
    page = doc[0]
    pix = page.get_pixmap()
    img_data = pix.tobytes("jpg")
    
    # 4. Ask Gemini (Updated for cleaner JSON)
    prompt = f"""
    Extract the following details from this book text:
    - Title
    - Author
    - ISBN
    - Edition
    - Category
    
    Text: {text_sample[:2000]}
    Return ONLY a raw JSON object. Do not include markdown formatting or backticks.
    """
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    
    # Clean the response in case Gemini adds backticks anyway
    clean_json = response.text.replace('```json', '').replace('```', '').strip()
    
    return {
        "metadata": clean_json,
        "has_cover": True
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)