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

app = FastAPI()

# Clean temporary files (called every 5 minutes)
def clean_tmp():
    tmp_dir = tempfile.gettempdir()
    for file in os.listdir(tmp_dir):
        if file.startswith(speech_tts_prefix):
            os.remove(os.path.join(tmp_dir, file))
    print("[Speech REST API] Temporary files cleaned!")

# Preprocess text to replace numerals with words
def preprocess_text(text):
    text = re.sub(r'\d+', lambda m: num2words(int(m.group(0))), text)
    return text

# Run TTS and save file
# Returns the path to the file
def run_tts_and_save_file(text):
    # Running the TTS
    mel_outputs, mel_length, alignment = model.encode_batch([text])

    # Running Vocoder (spectrogram-to-waveform)
    # Assuming HIFIGAN is used as the vocoder in Whisper
    # You can adjust this part based on the actual vocoder used in your Whisper model
    hifi_gan = model.hifigan
    waveforms = hifi_gan.decode_batch(mel_outputs)

    # Get temporary directory
    tmp_dir = tempfile.gettempdir()

    # Save wav to temporary file
    tmp_path_wav = os.path.join(tmp_dir, speech_tts_prefix + str(uuid.uuid4()) + wav_suffix)
    torchaudio.save(tmp_path_wav, waveforms.squeeze(1), 22050)
    return tmp_path_wav

@app.route("/")
def hello():
    return "Whisper Hello World!"

@app.route('/src', methods=['POST'])
def handler():
    if not request.files:
        # If the user didn't submit any files, return a 400 (Bad Request) error.
        abort(400)

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

    # This will be automatically converted to JSON.
    return {'results': results}

# Transcribe endpoint (from the second API)
@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'Invalid input, form-data: audio'}), 400

    # Audio file
    audio_file = request.files['audio']

    # Save audio file into tmp folder
    tmp_dir = tempfile.gettempdir()
    tmp_path = os.path.join(tmp_dir, str(uuid.uuid4()))
    audio_file.save(tmp_path)

    # Load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(tmp_path)
    audio = whisper.pad_or_trim(audio)

    # Make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    # Detect the spoken language
    _, probs = model.detect_language(mel)
    language = max(probs, key=probs.get)

    # Decode the audio
    result = model.transcribe(tmp_path)
    text_result = result["text"]
    text_result_trim = text_result.strip()

    # Delete tmp file
    os.remove(tmp_path)

    return jsonify({
        'language': language,
        'text': text_result_trim
    }), 200

# TTS endpoint (from the second API)
@app.route('/tts', methods=['POST'])
def generate_tts():
    if not request.json or 'text' not in request.json:
        return jsonify({'error': 'Invalid input: text missing'}), 400

    # Sentences to generate
    text = request.json['text']

    # Remove ' and " and  from text
    text = text.replace("'", "")
    text = text.replace('"', "")

    # Preprocess text to replace numerals with words
    text = preprocess_text(text)

    # Split text by . ? !
    sentences = re.split(r' *[\.\?!][\'"\)\]]* *', text)

    # Trim sentences
    sentences = [sentence.strip() for sentence in sentences]

    # Remove empty sentences
    sentences = [sentence for sentence in sentences if sentence]

    # Logging
    print("[Speech REST API] Got request: length (" + str(len(text)) + "), sentences (" + str(len(sentences)) + ")")

    # Run TTS for each sentence
    output_files = []

    for sentence in sentences:
        print("[Speech REST API] Generating TTS: " + sentence)
        tmp_path_wav = run_tts_and_save_file(sentence)
        output_files.append(tmp_path_wav)

    # Concatenate all files
    audio = AudioSegment.empty()

    for file in output_files:
        audio += AudioSegment.from_wav(file)

    # Save audio to file
    tmp_path_opus = os.path.join(tmp_dir, speech_tts_prefix + str(uuid.uuid4()) + opus_suffix)
    audio.export(tmp_path_opus, format="opus")

    # Delete tmp files
    for file in output_files:
        os.remove(file)

    # Send file response
    return send_file(tmp_path_opus, mimetype='audio/ogg, codecs=opus')

# Health endpoint (from the second API)
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/clean', methods=['GET'])
def clean():
    clean_tmp()
    return jsonify({'status': 'ok'}), 200