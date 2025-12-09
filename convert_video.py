"""
Convert JewelMart.mp4 to AVI format for better Windows DirectShow support
"""
import subprocess
import os

video_dir = r"E:\JM\JewelMart\assets"
input_file = os.path.join(video_dir, "JewelMart.mp4")
output_file = os.path.join(video_dir, "JewelMart.avi")

if not os.path.exists(input_file):
    print(f"Input file not found: {input_file}")
    exit(1)

print(f"Converting {input_file} to {output_file}...")
print("This may take a few minutes...")

try:
    # Try using ffmpeg if available
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-c:v", "mpeg4",
        "-q:v", "5",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        "-y",
        output_file
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"Successfully converted to: {output_file}")
    else:
        print(f"FFmpeg error: {result.stderr}")
        
except FileNotFoundError:
    print("FFmpeg not found. Please install FFmpeg to convert the video.")
    print("You can download it from: https://ffmpeg.org/download.html")
except Exception as e:
    print(f"Error: {e}")
