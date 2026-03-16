from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
import os
import base64
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

# ... (all your imports and middle code remain the same) ...

@app.post("/api/extract-metadata")
async def extract_metadata(file: UploadFile = File(...)):
    try:
        # 1. Read the PDF content from the upload
        pdf_content = await file.read()
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        
        # 2. Extract text for Gemini (Metadata)
        text_sample = ""
        for i in range(min(2, len(doc))):
            text_sample += doc[i].get_text()

        # 3. EXTRACTION OF COVER PAGE (The "JPG code")
        # Grab the first page
        page = doc[0]
        # Render page to an image (pixmap)
        pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72)) # Higher DPI for professional look
        # Convert pixmap to JPEG bytes
        img_bytes = pix.tobytes("jpg")
        
        # Encode bytes to Base64 string so it can travel in JSON
        base64_cover = base64.b64encode(img_bytes).decode('utf-8')
        cover_url = f"data:image/jpeg;base64,{base64_cover}"

        # In your extract_metadata function in main.py

        standards = "General, Class 1, Class 2, Class 3, Class 4, Class 5, Class 6, Class 7, Class 8, Class 9, Class 10, Class 11, Class 12"
        categories = "Textbooks, History, Science, Physics, Chemistry, Biology, English literarture, English Grammer, Bengali, Bengali Grammer, Computer, EVS, Psychology, Sociology, Political Science, Education, Kokborok, Geography, Mathematics, Life Science, Physical Science, General Knowledge"

        prompt = (
            f"Extract book details from this text: {text_sample[:2000]}. "
            f"Return ONLY a raw JSON object with these EXACT keys: "
            f"'title', 'author', 'isbn', 'edition', 'category', 'language', 'standard', 'subjects', 'description'.\n\n"
            f"CRITICAL RULES:\n"
            f"1. 'standard' MUST be exactly one of these: [{standards}].\n"
            f"2. 'category' MUST be exactly one of these: [{categories}].\n"
            f"3. If ISBN is not found, use null.\n"
            f"4. Do not use markdown backticks."
        )
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        # More robust cleaning of Markdown/Backticks
        clean_json = response.text.strip().removeprefix('```json').removesuffix('```').strip()
        
        # 5. Return everything to the Frontend
        return {
            "metadata": clean_json, 
            "cover_preview": cover_url, # This will show the image in your dashboard
            "success": True
        }

    except Exception as e:
        print(f"Error during extraction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Render handles this via the Start Command in Settings.