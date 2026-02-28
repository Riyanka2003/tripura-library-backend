from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
import os
import uvicorn
from google.generativeai.types import RequestOptions
app = FastAPI()

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
        model = genai.GenerativeModel('gemini-1.5-flash-001') 

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)