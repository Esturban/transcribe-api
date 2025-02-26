import argparse
import os
import time
from aims import process_file

import logging
import shutil
# Set up basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    parser = argparse.ArgumentParser(description='Extract audio from an MP4 video file and convert it to text.')
    parser.add_argument('input_path', help='The path to the input file (video or audio) or folder containing files')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')

    args = parser.parse_args()
    
    start_time = time.time()
    if args.verbose:
        logging.info(f"Start time: {time.ctime(start_time)}")
    
    try:
        if os.path.isdir(args.input_path):
            # Process all files in the root of the folder
            for file in os.listdir(args.input_path):
                input_file_path = os.path.join(args.input_path, file)
                if os.path.isfile(input_file_path):
                    output_audio_dir = os.path.join(args.input_path, 'processed')
                    process_file(input_file_path, output_audio_dir, args.verbose)
        else:
            # Process a single file
            output_audio_dir = os.path.join(os.path.dirname(args.input_path), 'processed')
            process_file(args.input_path, output_audio_dir, args.verbose)
            # Move the original audio file to the "processed" subfolder
            os.makedirs(output_audio_dir, exist_ok=True)
            shutil.move(args.input_path, os.path.join(output_audio_dir, os.path.basename(args.input_path)))
    except Exception as e:
        logging.error(f"Error: {e}")
    
    end_time = time.time()
    logging.info(f"End time: {time.ctime(end_time)}")
    logging.info(f"Total runtime: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()