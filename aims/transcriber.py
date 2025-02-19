import whisper
from whisper.utils import get_writer
from pydub import AudioSegment
import logging
import os

def convert_audio_to_text(audio_path: str, verbose: bool=False, mdl: str="tiny.en", srt: bool=False, vtt: bool=False):
    model = whisper.load_model(mdl)
    #Tiny is roughly 75.6MB
    #print(model.model_path.os.path.getsize())
    audio = AudioSegment.from_file(audio_path)
    audio.export("temp.wav", format="wav")
    
    result = model.transcribe("temp.wav", fp16=False)
    text = result["text"]
    if verbose: logging.info(f"Transcription: {text}")
    
    output_text_path = os.path.splitext(audio_path)[0] + '.txt'
    with open(output_text_path, 'w') as f:
        f.write(text)
    
    # Save as an SRT file
    if srt:
        srt_writer = get_writer("srt", os.path.dirname(audio_path))
        srt_writer(result, os.path.splitext(audio_path)[0] + '.srt')
        
    if vtt:
        vtt_writer = get_writer("vtt", os.path.dirname(audio_path))
        vtt_writer(result, os.path.splitext(audio_path)[0] + '.vtt')
    
    os.remove("temp.wav")