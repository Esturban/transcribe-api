#import concurrent.futures
import logging
import os
import shutil
from .parse import extract_audio_from_video
from .transcriber import convert_audio_to_text
import random  # Import random for variability

def setup_logging(verbose):
    log_level = logging.INFO if verbose else logging.CRITICAL
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s', filename='transcribe.log', filemode='a')


def process_file(input_path, output_audio_dir: str=None, verbose: bool=False):
    
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    
    if input_path.lower().endswith(('.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a')):
        # If the input is already an audio file, skip audio extraction
        logging.info("Input is an audio file, skipping audio extraction.")
        logging.info(f"Converting {input_path} to text...")
        text_result = convert_audio_to_text(input_path, verbose)
        if output_audio_dir is not None: 
            output_audio_path = os.path.join(output_audio_dir, base_name + '.mp3')
            shutil.move(input_path, os.path.join(output_audio_dir, os.path.basename(input_path)))
    elif input_path.lower().endswith(('.mp4', '.mov', '.mkv', '.avi', '.wmv', '.flv')):
        # If the input is a video file, extract audio first
        logging.info("Input is a video file, extracting the audio.")
        logging.info(f"Extracting {input_path} to audio...")
        extract_audio_from_video(input_path, output_audio_path)
        logging.info(f"Converting {input_path} to text...")
        text_result = convert_audio_to_text(output_audio_path, verbose)
        if output_audio_dir is not None: shutil.move(input_path, os.path.join(output_audio_dir, os.path.basename(input_path)))
    else: 
        return None 
    
    return text_result if verbose else None

# Unicode spaces dictionary
unicode_spaces = {
    'Em Space': '\u2003',
    'En Space': '\u2002',
    'Thin Space': '\u2009',
    'Hair Space': '\u200A',
    'Narrow No-Break': '\u202F',
    'Hair Space3': '\u200A\u200A\u200A',
    'Zero Width Space': '\u200B',
    'Word Joiner': '\u2060'
}

def replace_spaces_with_unicode(text: str, unicode_space_name: str) -> str:
    """Replace spaces in the text with the specified Unicode character by name."""
    unicode_character = unicode_spaces.get(unicode_space_name)
    if unicode_character is None:
        raise ValueError(f"Invalid Unicode space name: {unicode_space_name}")
    return text.replace(' ', unicode_character)

def replace_spaces_in_lines(text_lines: list, unicode_space_names: list) -> list:
    """Replace spaces in each line of text with varying Unicode characters based on the provided names."""
    modified_lines = []
    for line in text_lines:
        
        # Randomly select a Unicode space name from the provided list
        space_name = random.choice(unicode_space_names)
        modified_line = replace_spaces_with_unicode(line, space_name)
        modified_lines.append(modified_line)
    
    return modified_lines
