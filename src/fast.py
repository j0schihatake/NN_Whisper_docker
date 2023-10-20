from fastapi import FastAPI, File, UploadFile, Response
from pydantic import BaseModel
from tts import transcribes
import whisper
import json
import io

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
async def transcribe(request: TranscribeRequest):
    text = await transcribes(request)
    return {"text": text}


#@app.post("/transcribest")
#async def transcribe_audio_file(file: UploadFile = File(...)):
#    audio = await file.read()
#    buffer = io.BytesIO(audio)
#    buffer.name = 'audio.m4a'  # pretty sure any string here will do
#    result = whisper.transcribe("whisper-1", buffer)
#    text = json.loads(result)["text"]
#    print("Transcribe text: " + text)
#    return text
