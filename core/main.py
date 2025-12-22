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
# !!! PASTE YOUR KEY HERE !!!
GENAI_API_KEY = "AIzaSyAjRmbB4no4PVf098pe88cMSqkZsAI_zRw"
genai.configure(api_key=GENAI_API_KEY)

# 3. ENDPOINT
class AIRequest(BaseModel):
    query: str

@app.post("/ask_ai")
def ask_ai(request: AIRequest):
    try:
        # We switched to 'gemini-2.0-flash' because it is in your approved list
        model = genai.GenerativeModel('gemini-flash-latest')
        
        response = model.generate_content(request.query)
        return {"answer": response.text}

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {"answer": f"Backend Error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)