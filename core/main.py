import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import uvicorn

app = FastAPI()

# 1. NETWORK CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. AI CONFIGURATION
# ✅ FIXED: Now matching your Render variable name "GEMINI_API_KEY"
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: API Key is missing! Check 'GEMINI_API_KEY' in Render environment.")
else:
    genai.configure(api_key=api_key)

# 3. ENDPOINT
class AIRequest(BaseModel):
    query: str

@app.post("/ask_ai")
def ask_ai(request: AIRequest):
    try:
        if not api_key:
            return {"answer": "Backend Error: API Key not configured."}

        # Using 'gemini-1.5-flash' for better stability
        model = genai.GenerativeModel('gemini-flash-latest') 
        
        response = model.generate_content(request.query)
        return {"answer": response.text}

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {"answer": f"Backend Error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)