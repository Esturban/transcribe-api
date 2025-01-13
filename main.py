import argparse
import os
import time
from moviepy import VideoFileClip
import whisper
from whisper.utils import get_writer
from pydub import AudioSegment
import concurrent.futures

def extract_audio_from_video(video_path, output_audio_path):
    if not video_path.lower().endswith('.mp4'):
        raise ValueError("The input file must be an MP4 file.")
    
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(output_audio_path)

    if not os.path.exists(output_audio_path):
        raise RuntimeError("Audio extraction failed, output file does not exist.")
    print(f"Audio successfully extracted to {output_audio_path}")

def convert_audio_to_text(audio_path, verbose=False):
    model = whisper.load_model("tiny.en")
    audio = AudioSegment.from_file(audio_path)
    audio.export("temp.wav", format="wav")
    
    result = model.transcribe("temp.wav", fp16=False)
    text = result["text"]
    if verbose: print(f"Transcription: {text}")
    
    output_text_path = os.path.splitext(audio_path)[0] + '.txt'
    with open(output_text_path, 'w') as f:
        f.write(text)
        # Save as an SRT file
    srt_writer = get_writer("srt", os.path.dirname(audio_path))
    srt_writer(result, os.path.splitext(audio_path)[0] + '.srt')
    
    # Save as a VTT file
    vtt_writer = get_writer("vtt", os.path.dirname(audio_path))
    vtt_writer(result, os.path.splitext(audio_path)[0] + '.vtt')
    
    os.remove("temp.wav")

def main():
    parser = argparse.ArgumentParser(description='Extract audio from an MP4 video file and convert it to text.')
    parser.add_argument('video_path', help='The path to the MP4 video file')
    parser.add_argument('output_audio_path', help='The path where the extracted audio will be saved')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')

    args = parser.parse_args()
    
    start_time = time.time()
    if args.verbose:
        print(f"Start time: {time.ctime(start_time)}")
    
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_audio = executor.submit(extract_audio_from_video, args.video_path, args.output_audio_path)
            future_audio.result()  # Wait for audio extraction to complete
            future_text = executor.submit(convert_audio_to_text, args.output_audio_path, args.verbose)
            future_text.result()  # Wait for audio-to-text conversion to complete
    except Exception as e:
        print(f"Error: {e}")
    
    end_time = time.time()
    #if args.verbose:
    print(f"End time: {time.ctime(end_time)}")
    print(f"Total runtime: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()