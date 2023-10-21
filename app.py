from flask import Flask, abort, request
from tempfile import NamedTemporaryFile
import whisper
import torch
import os

# Check if NVIDIA GPU is available
torch.cuda.is_available()
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

model_type: str = "medium"
# Load the Whisper model:
print("start load model: " + model_type)
model = whisper.load_model(model_type, device=DEVICE)
print("model loaded. start Flask.")

app = Flask(__name__)


@app.route("/")
def hello():
    return "Whisper Hello World!"


@app.route('/whisper', methods=['POST'])
def handler():
    if not request.files:
        # If the user didn't submit any files, return a 400 (Bad Request) error.
        abort(400)

    print("handler(POST) on /whisper start")

    # For each file, let's store the results in a list of dictionaries.
    results = []

    # Loop over every file that the user submitted.
    for filename, handle in request.files.items():
        # Create a temporary file.
        # The location of the temporary file is available in `temp.name`.
        temp = NamedTemporaryFile()
        # Write the user's uploaded file to the temporary file.
        # The file will get deleted when it drops out of scope.
        handle.save(temp)
        # Let's get the transcript of the temporary file.
        result = model.transcribe(temp.name)
        # Now we can store the result object for this file.
        results.append({
            'filename': filename,
            'transcript': result['text'],
        })
        print("result['text']: " + result['text'])
    # This will be automatically converted to JSON.
    # return {'results': results}
    return result['text']


# Other methods

# Entry point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8084))

    # Start server
    print("[Whisper STT] Starting server on port " + str(port))

    app.run(host='0.0.0.0', port=port)
