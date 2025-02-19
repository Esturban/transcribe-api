import argparse
import os
import time
from aims import extract_audio_from_video, convert_audio_to_text

import concurrent.futures
import logging

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    parser = argparse.ArgumentParser(description='Extract audio from an MP4 video file and convert it to text.')    
    parser.add_argument('video_path', help='The path to the MP4 video file')
    parser.add_argument('output_audio_path', help='The path where the extracted audio will be saved')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')

    args = parser.parse_args()
    
    start_time = time.time()
    if args.verbose:
        logging.info(f"Start time: {time.ctime(start_time)}")
    
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_audio = executor.submit(extract_audio_from_video, args.video_path, args.output_audio_path)
            future_audio.result()  # Wait for audio extraction to complete
            future_text = executor.submit(convert_audio_to_text, args.output_audio_path, args.verbose)
            future_text.result()  # Wait for audio-to-text conversion to complete
    except Exception as e:
        logging.error(f"Error: {e}")
    
    end_time = time.time()
    logging.info(f"End time: {time.ctime(end_time)}")
    logging.info(f"Total runtime: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()