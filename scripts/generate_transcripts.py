import whisper
import subprocess
import argparse
import sys
import os
from datetime import timedelta

# Set up argument parser
parser = argparse.ArgumentParser(description='Transcribe YouTube video to text and SRT files')
parser.add_argument('youtube_link', type=str, help='YouTube video URL')
args = parser.parse_args()

# Check if YouTube link is provided
if not args.youtube_link:
    print("Error: No YouTube link provided")
    sys.exit(1)

# Download audio using yt-dlp
output_file = "downloaded_audio.wav"

print("Downloading audio from youtube link...")

# Download error handling
try:
    result = subprocess.run([
        'yt-dlp',
        '-x',
        '--audio-format', 'wav',
        '--output', output_file,
        args.youtube_link
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
print("Transcribe audio using whisper...")
result = model.transcribe(output_file, verbose=False)

# Function to format time for SRT (HH:MM:SS,mmm)
def format_srt_time(seconds):
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

print("Writing transcribed text to .txt ...")
# Write to TXT file
with open("transcription.txt", "w", encoding="utf-8") as txt_file:
    for segment in result["segments"]:
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"].strip()
        txt_file.write(f"[{start_time:.2f}s - {end_time:.2f}s] {text}\n")

# Write to SRT file
print("Writing transcribed text to .srt ...")
with open("transcription.srt", "w", encoding="utf-8") as srt_file:
    for i, segment in enumerate(result["segments"], 1):
        start_time = format_srt_time(segment["start"])
        end_time = format_srt_time(segment["end"])
        text = segment["text"].strip()
        srt_file.write(f"{i}\n{start_time} --> {end_time}\n{text}\n\n")
