import whisper
from whisper.utils import get_writer
import logging
import os

def transcribe_audio(audio_path: str=None,  mdl: str="tiny.en", dl_loc: str=None):
    if dl_loc is None:
        model = whisper.load_model(name=mdl)
    else:
        if not os.path.exists(dl_loc): os.mkdir(dl_loc)
        model = whisper.load_model(name=mdl, download_root=dl_loc)
    
    return model.transcribe(audio_path, fp16=False)
        
def whisper_write(result: dict, path: str, ext: str):
    if path.lower().endswith(('.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a')):
        ext_dir = os.path.join(os.path.dirname(path), ext)
        if not os.path.exists(ext_dir):
            os.mkdir(ext_dir)
        writer = get_writer(ext, ext_dir)
        writer(result, os.path.join(ext_dir, os.path.splitext(os.path.basename(path))[0] + '.' + ext))
                

def convert_audio_to_text(audio_path: str=None, verbose: bool=True, srt: bool=False, vtt: bool=False):
    # Get the audio transcription based on the model in the local environment with the path set
    result = transcribe_audio(audio_path, dl_loc=os.getenv("MDL_PATH"))
    # Get the text from the result
    text = result["text"]
    # Log the information
    #logging.info(f"Transcription: {text}")
    # Ensure that the audio path location is specified
    if audio_path is not None:
        logging.info(f"Audio path: {audio_path}")
        whisper_write(result, audio_path, "txt")
        if srt: whisper_write(result, audio_path, "srt")
        if vtt: whisper_write(result, audio_path, "vtt")
    return text