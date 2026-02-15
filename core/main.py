from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
import os
import uvicorn

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
        # Standardize on gemini-1.5-flash
        model = genai.GenerativeModel('gemini-1.5-flash') 

        if request.audio_data:
            # For voice messages
            response = model.generate_content([
                "Please respond to this audio request concisely.",
                {"mime_type": "audio/mp4", "data": request.audio_data}
            ])
        else:
            # For text messages
            response = model.generate_content(request.query)

        # CRITICAL: Always return a valid JSON object with the "answer" key
        if response and response.text:
            return {"answer": response.text}
        else:
            return {"answer": "AI processed the request but returned an empty response."}

    except Exception as e:
        print(f"❌ BACKEND ERROR: {e}")
        # This will show the actual error on your mobile screen
        return {"answer": f"Backend Error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)