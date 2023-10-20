from fastapi import FastAPI, File, UploadFile, Response
from pydantic import BaseModel
from whisper import transcribe


app = FastAPI()


class TranscribeRequest(BaseModel):
    audio: bytes


class TTSRequest(BaseModel):
    text: str
    speaker: str

@app.get("/")
async def hello():
    return {"hello": "from whisper"}

@app.post("/transcribe")
async def transcribes(request: TranscribeRequest):
    audio = request.audio
    text = await transcribe(audio)
    return {"text": text}