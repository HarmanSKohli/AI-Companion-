from fastapi import FastAPI, HTTPException
from groq import Groq
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Dict
from personality import get_personality_context

# 1. FIRST create app instance
app = FastAPI()

# 2. THEN load environment variables
load_dotenv()

# 3. Initialize Groq client AFTER app creation
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Request model
class ChatRequest(BaseModel):
    user_input: str
    region: str
    history: List[Dict]

# Route definition AFTER app creation
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        system_prompt = get_personality_context(request.region, request.history)
        
        messages = [
            {"role": "system", "content": system_prompt},
            *request.history,
            {"role": "user", "content": request.user_input}
        ]
        
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stop=None
        )
        
        return {"response": response.choices[0].message.content}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the app directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
