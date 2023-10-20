from fastapi import FastAPI, File, UploadFile, Response
from tempfile import NamedTemporaryFile
import whisper
import torch
from num2words import num2words
from pydub import AudioSegment
import torchaudio
import os
import re
import tempfile
import uuid

# Check if NVIDIA GPU is available
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Load the Whisper model
model = whisper.load_model("large", device=DEVICE)

# TTS file prefix
speech_tts_prefix = "speech-tts-"
wav_suffix = ".wav"
opus_suffix = ".opus"


async def transcribe(audio_bytes):
    audio_stream = io.BytesIO(audio_bytes)

    result = model.transcribe(audio_stream)

    text = json.loads(result)["text"]
    print("Transcribe text: " + text)
    return text


# Preprocess text to replace numerals with words
def preprocess_text(text):
    text = re.sub(r'\d+', lambda m: num2words(int(m.group(0))), text)
    return text

# Preprocess decade and auto detect language
def decode_and_autodetect_language(audio_bytes):
    model = whisper.load_model("base")

    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio("audio.mp3")
    audio = whisper.pad_or_trim(audio)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    # detect the spoken language
    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}")

    # decode the audio
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)

    # print the recognized text
    print(result.text)
    return result.text