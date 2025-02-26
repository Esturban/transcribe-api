import concurrent.futures
import logging
import os
import shutil
from .parse import extract_audio_from_video
from .transcriber import convert_audio_to_text

def setup_logging(verbose):
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s', filename='transcribe.log', filemode='a')


def process_file(input_path, output_audio_dir, verbose):
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_audio_path = os.path.join(output_audio_dir, base_name + '.mp3')
    
    if input_path.lower().endswith(('.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a')):
        # If the input is already an audio file, skip audio extraction
        logging.info("Input is an audio file, skipping audio extraction.")
        logging.info(f"Converting {input_path} to text...")
        text_result = convert_audio_to_text(input_path, verbose)
        shutil.move(input_path, os.path.join(output_audio_dir, os.path.basename(input_path)))
    elif input_path.lower().endswith(('.mp4', '.mov', '.mkv', '.avi', '.wmv', '.flv')):
        # If the input is a video file, extract audio first
        logging.info("Input is a video file, extracting the audio.")
        logging.info(f"Extracting {input_path} to audio...")
        extract_audio_from_video(input_path, output_audio_path)
        logging.info(f"Converting {input_path} to text...")
        text_result = convert_audio_to_text(output_audio_path, verbose)
        shutil.move(input_path, os.path.join(output_audio_dir, os.path.basename(input_path)))
    else: 
        return None 
    
    return text_result if verbose else None

