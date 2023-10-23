from flask import Flask, abort, request
from tempfile import NamedTemporaryFile
import whisper
import torch
import os

# Check if NVIDIA GPU is available
# torch.cuda.is_available()
DEVICE = "cpu"
# "cuda" if torch.cuda.is_available() else "cpu"

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

model_type: str = "base"

# Load the Whisper model:
print("start load model: " + model_type)
model = whisper.load_model(model_type, device=DEVICE)
print("model loaded.")

temp_audio: str = "/home/whisper-user/whisper/temp/input.wav"

#app = Flask(__name__)


@app.route("/")
def hello():
    return "Whisper Hello World!"


@app.route('/whisper', methods=['POST'])
def handler():
    if not request.files:
        abort(400)

    print("handler(POST) on /whisper start")

    results = []

    for filename, handle in request.files.items():
        temp = temp_audio
        handle.save(temp)
        # Let's get the transcript of the temporary file.
        result = model.transcribe(temp.name)
        # Now we can store the result object for this file.
        results.append({
            'filename': filename,
            'transcript': result['text'],
        })
        print("result['text']: " + result['text'])
        silent_remove(temp)
    # This will be automatically converted to JSON.
    # return {'results': results}
    return result['text']


def silent_remove(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


# Entry point
#if __name__ == '__main__':
#    port = int(os.environ.get('PORT', 8084))
    
#    print("[Whisper STT] Starting server on port " + str(port))

#    app.run(host='0.0.0.0', port=port)
