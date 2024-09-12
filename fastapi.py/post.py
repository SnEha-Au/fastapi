from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydub import AudioSegment
import speech_recognition as sr
from googletrans import Translator
import os
import shutil

app = FastAPI()

# Root GET method for basic testing
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Audio Translation API!"}

# Convert audio file to WAV format
def convert_to_wav(audio_file_path):
    audio = AudioSegment.from_file(audio_file_path)
    wav_file_path = "converted_audio.wav"
    audio.export(wav_file_path, format="wav")
    return wav_file_path

# Transcribe audio file
def transcribe_audio(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio."
    except sr.RequestError:
        return "Sorry, there was an error with the API request."

# Translate text
def translate_text(text, dest_language="es"):
    translator = Translator()
    translated = translator.translate(text, dest=dest_language)
    return translated.text

@app.post("/translate-audio/")
async def translate_audio(file: UploadFile = File(...), language_code: str = Form(...)):
    # Save the uploaded file
    temp_file_path = "temp_audio.mp3"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Convert audio file to WAV
    wav_file_path = convert_to_wav(temp_file_path)
    
    # Transcribe the audio file
    transcribed_text = transcribe_audio(wav_file_path)
    
    # Translate the transcribed text
    translated_text = translate_text(transcribed_text, dest_language=language_code)
    
    # Clean up temporary files
    os.remove(temp_file_path)
    os.remove(wav_file_path)
    
    # Return the results
    return JSONResponse(content={"transcribed_text": transcribed_text, "translated_text": translated_text})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
