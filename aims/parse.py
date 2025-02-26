import logging
from moviepy import VideoFileClip
import os

def extract_audio_from_video(video_path: str, output_audio_path: str):
    """
    Extract audio from an MP4 video file and save it to a separate audio file.

    Args:
        video_path (str): The path to the MP4 video file.
        output_audio_path (str): The path where the extracted audio will be saved.
    """
    # Validate that input file is MP4 format
    if not video_path.lower().endswith('.mp4'):
        logging.error("The input file must be an MP4 file.")
        raise ValueError("The input file must be an MP4 file.")
    
    # Load video and extract audio using moviepy
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(output_audio_path)

    # Verify that audio file was created successfully
    if not os.path.exists(output_audio_path):
        logging.error("Audio extraction failed, output file does not exist.")
        raise RuntimeError("Audio extraction failed, output file does not exist.")
    logging.info(f"Audio successfully extracted to {output_audio_path}")
