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
        # 1. Debugging: Print what we received
        print(f"📝 Query: {request.query}")
        print(f"🎤 Audio Length: {len(request.audio_data) if request.audio_data else 'None'}")

        # 2. Safety Check: If both are empty, stop immediately
        if not request.query and not request.audio_data:
            return {"answer": "Error: No audio or text received by the server."}

        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        if request.audio_data:
            # Voice Mode
            response = model.generate_content([
                "Listen to this request and answer it concisely.",
                {
                    "mime_type": "audio/mp4",
                    "data": request.audio_data
                }
            ])
        else:
            # Text Mode
            response = model.generate_content(request.query)

        return {"answer": response.text}

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {"answer": f"Backend Error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)