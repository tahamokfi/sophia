import os
import librosa
import soundfile as sf
from flask import Flask, request, jsonify, render_template
from transformers import pipeline
from google.cloud import storage
import io
import traceback
import numpy as np
import ffmpeg
import math
from components.summarization import rag_query_engine

app = Flask(__name__)

transcriber = pipeline(model="openai/whisper-tiny.en")

bucket_name = 'your-bucket-name'
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_audio():
    try:
        audio_file = request.files['audio']
        print(f"Received audio file: {audio_file.filename}, Content Type: {audio_file.content_type}")
        
        if not audio_file:
            return jsonify({"error": "No audio file received"}), 400
        
        wav_data = convert_to_wav(audio_file)
        transcript = transcribe_in_batches(wav_data)
        return jsonify({"transcript": transcript})
    except Exception as e:
        error_message = f"Error in upload_audio: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        question = data.get('question')
        transcript = data.get('transcript')
        
        if not question or not transcript:
            return jsonify({"error": "Missing question or transcript"}), 400
        
        response = rag_query_engine(transcript).query(question).response
        return jsonify({"response": response})
    except Exception as e:
        error_message = f"Error in chat: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        return jsonify({"error": str(e)}), 500

def convert_to_wav(audio_file):
    try:
        audio_data = audio_file.read()
        audio_io = io.BytesIO(audio_data)
        
        if audio_file.content_type == 'audio/webm':
            out, _ = (
                ffmpeg
                .input('pipe:0')
                .output('pipe:1', format='wav')
                .run(input=audio_data, capture_stdout=True, capture_stderr=True)
            )
            wav_io = io.BytesIO(out)
        elif audio_file.content_type in ['audio/mpeg', 'audio/mp3']:
            y, sr = librosa.load(audio_io, sr=None)
            wav_io = io.BytesIO()
            sf.write(wav_io, y, sr, format='wav')
        else:
            raise ValueError(f"Unsupported audio format: {audio_file.content_type}")
        
        wav_io.seek(0)
        return wav_io.getvalue()
    except Exception as e:
        error_message = f"Error in convert_to_wav: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        raise

def transcribe_in_batches(wav_data, chunk_duration=30):
    try:
        audio, sr = librosa.load(io.BytesIO(wav_data), sr=None)
        duration = librosa.get_duration(y=audio, sr=sr)
        chunk_size = int(chunk_duration * sr)
        num_chunks = math.ceil(len(audio) / chunk_size)
        
        transcriptions = []
        for i in range(num_chunks):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, len(audio))
            chunk = audio[start:end]
            
            chunk_io = io.BytesIO()
            sf.write(chunk_io, chunk, sr, format='wav')
            chunk_io.seek(0)
            
            chunk_transcript = transcriber(chunk_io.getvalue())['text']
            transcriptions.append(chunk_transcript)
            print(f"Processed chunk {i+1}/{num_chunks}")
        
        return ' '.join(transcriptions)
    except Exception as e:
        error_message = f"Error in transcribe_in_batches: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        raise


if __name__ == '__main__':
    app.run(debug=True, port=5004)