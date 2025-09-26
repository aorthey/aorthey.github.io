import whisper
import subprocess
import argparse
import sys
import os
from datetime import timedelta
import yaml

# Set up argument parser
parser = argparse.ArgumentParser(description='Transcribe YouTube video to text and SRT files')
parser.add_argument('input', type=str, help='YouTube video URL or folder path')
args = parser.parse_args()

# Check if input is provided
if not args.input:
    print("Error: No input provided")
    sys.exit(1)

# Determine if input is a folder or YouTube link
if os.path.isdir(args.input):
    metadata_path = os.path.join(args.input, 'metadata.yml')
    if not os.path.exists(metadata_path):
        print(f"Error: No metadata.yml found in folder '{args.input}'")
        sys.exit(1)

    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = yaml.safe_load(f)

    video_id = metadata.get('youtube')
    if not video_id:
        print("Error: No 'youtube' entry found in metadata.yml")
        sys.exit(1)

    youtube_link = f"https://www.youtube.com/watch?v={video_id}"
    output_folder = args.input
else:
    youtube_link = args.input
    output_folder = '.'

# Download audio using yt-dlp
output_file = "downloaded_audio.wav"

print("Downloading audio from YouTube link...")

# Download error handling
try:
    result = subprocess.run([
        'yt-dlp',
        '-x',
        '--audio-format', 'wav',
        '--output', output_file,
        youtube_link
    ], check=True, capture_output=True, text=True)
except subprocess.CalledProcessError as e:
    print(f"Error downloading audio: {e.stderr}")
    sys.exit(1)

# WAV file existence check
if not os.path.exists(output_file):
    print(f"Error: WAV file '{output_file}' was not created")
    sys.exit(1)

# CPU usage for Whisper
model = whisper.load_model("large", device="cpu")

# Transcribe audio
print("Transcribing audio using Whisper...")
result = model.transcribe(output_file, verbose=False)

# Function to format time for SRT (HH:MM:SS,mmm)
def format_srt_time(seconds):
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

# Define output file paths in current directory temporarily
txt_path = "transcription.txt"
srt_path = "transcription.srt"

print(f"Writing transcribed text to {txt_path}...")
# Write to TXT file
with open(txt_path, "w", encoding="utf-8") as txt_file:
    for segment in result["segments"]:
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"].strip()
        txt_file.write(f"[{start_time:.2f}s - {end_time:.2f}s] {text}\n")

# Write to SRT file
print(f"Writing transcribed text to {srt_path}...")
with open(srt_path, "w", encoding="utf-8") as srt_file:
    for i, segment in enumerate(result["segments"], 1):
        start_time = format_srt_time(segment["start"])
        end_time = format_srt_time(segment["end"])
        text = segment["text"].strip()
        srt_file.write(f"{i}\n{start_time} --> {end_time}\n{text}\n\n")

# If output_folder is not current dir, move files there
if output_folder != '.':
    target_txt = os.path.join(output_folder, "transcription.txt")
    target_srt = os.path.join(output_folder, "transcription.srt")
    os.rename(txt_path, target_txt)
    os.rename(srt_path, target_srt)
    print(f"Moved transcription files to '{output_folder}'")

# Optional: Clean up temporary audio file
os.remove(output_file)
