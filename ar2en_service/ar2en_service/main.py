from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import uuid
import logging

# Initialize FastAPI app
app = FastAPI()

# Initialize the Hugging Face translation pipeline
translator = pipeline("translation_ar_to_en", model="Helsinki-NLP/opus-mt-ar-en")

# In-memory store to track request statuses
translation_status = {}

# Request model for translation
class TranslationRequest(BaseModel):
    text: str

@app.post("/translate/ar2en")
def translate(request: TranslationRequest):
    # Generate a unique ID for the request
    request_id = str(uuid.uuid4())
    # Store the initial status as 'In Progress'
    translation_status[request_id] = "In Progress"
    try:
        # Perform translation
        result = translator(request.text)
        # Update status to 'Completed'
        translation_status[request_id] = "Completed"
        return {"id": request_id, "translated_text": result[0]["translation_text"]}
    except Exception as e:
        # Update status to 'Failed' in case of an error
        translation_status[request_id] = "Failed"
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/translate/ar2en/status/{id}")
def get_status(id: str = None):
    if not id:
        raise HTTPException(status_code=400, detail="ID parameter is required.")
    status = translation_status.get(id)
    if status is None:
        raise HTTPException(status_code=404, detail="Translation request not found")
    return {"id": id, "status": status}

