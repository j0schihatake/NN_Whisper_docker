from flask import Flask, abort, request
import numpy as np
import subprocess
import whisper
import torch
import os

# Check if NVIDIA GPU is available
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print("------- WHISPER --------")
print("DEVICE set: " + DEVICE)
print("")
print("Aveilable Route:")
print("")
print("/")
print("")
print("/whisper : POST")
print("")

# All size model:
# tiny 1GB 32X
# base 1GB 15X
# small 2GB 6x
# medium 5GB 2x
# large 10GB 1x

model_type: str = "large-v3"

# Load the Whisper model:
print("start load model: " + model_type)
model = whisper.load_model(model_type, device=DEVICE)
print("model loaded.")

app = Flask(__name__)


@app.route("/")
def hello():
    return "Whisper Hello World!"


def load_audio_from_bytes(data: bytes, sr: int = 16000) -> np.ndarray:
    """Decode uploaded audio straight from memory via an ffmpeg pipe -- no file ever touches disk,
    which also removes the shared-temp-path race that used to hit concurrent requests."""
    cmd = [
        "ffmpeg", "-nostdin", "-threads", "0",
        "-i", "pipe:0",
        "-f", "s16le", "-ac", "1", "-acodec", "pcm_s16le", "-ar", str(sr),
        "pipe:1",
    ]
    process = subprocess.run(cmd, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.returncode != 0:
        raise RuntimeError(f"ffmpeg failed to decode audio: {process.stderr.decode(errors='ignore')}")
    return np.frombuffer(process.stdout, np.int16).flatten().astype(np.float32) / 32768.0


@app.route('/whisper', methods=['POST'])
def handler():
    if not request.files:
        abort(400)

    print("handler(POST) on /whisper start")

    results = []

    for filename, handle in request.files.items():
        audio = load_audio_from_bytes(handle.read())
        result = model.transcribe(audio)
        results.append({
            'filename': filename,
            'transcript': result['text'],
        })
        print("result['text']: " + result['text'])

    return {'results': results}


# Entry point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 28084))

    print("[Whisper STT] Starting server on port " + str(port))

    app.run(host='0.0.0.0', port=port)
