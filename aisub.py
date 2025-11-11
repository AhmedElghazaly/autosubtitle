#!/usr/bin/env python3
"""
Video to Subtitle Generator using Groq Whisper API
Extracts audio from video, compresses to <18MB, transcribes, and generates SRT
"""

import os
import sys
import math
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from groq import Groq
import subprocess

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Set your API key as environment variable
MAX_FILE_SIZE_MB = 18  # Groq's limit
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Initialize Groq client
client = Groq(
    api_key=GROQ_API_KEY
)

def check_ffmpeg():
    """Check if ffmpeg is available"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ffmpeg not found. Please install ffmpeg first.")
        print("   Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("   macOS: brew install ffmpeg")
        print("   Windows: Download from https://ffmpeg.org/download.html")
        return False


def extract_audio(video_path: str, audio_path: str) -> bool:
    """
    Extract audio from video using ffmpeg
    """
    print(f"🎬 Extracting audio from {video_path}...")
    try:
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vn",  # Disable video
            "-acodec", "libmp3lame",  # MP3 codec
            "-ar", "16000",  # Sample rate 16kHz
            "-ac", "1",  # Mono
            "-b:a", "64k",  # 64kbps bitrate
            "-y",  # Overwrite if exists
            audio_path
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        
        if os.path.exists(audio_path):
            size_mb = os.path.getsize(audio_path) / (1024 * 1024)
            print(f"✅ Audio extracted: {audio_path} ({size_mb:.2f} MB)")
            return True
        return False
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to extract audio: {e.stderr.decode()}")
        return False


def compress_audio_if_needed(audio_path: str) -> List[str]:
    """
    Compress audio and split if needed to ensure each chunk < 18MB
    Returns list of audio file paths
    """
    file_size = os.path.getsize(audio_path)
    size_mb = file_size / (1024 * 1024)
    
    print(f"📊 Audio file size: {size_mb:.2f} MB")
    
    if file_size <= MAX_FILE_SIZE_BYTES:
        print("✅ File size is within limit, no compression needed")
        return [audio_path]
    
    print(f"⚠️  File too large, splitting into chunks...")
    
    # Get audio duration
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, check=True, text=True)
        duration = float(json.loads(result.stdout)["format"]["duration"])
    except Exception as e:
        print(f"❌ Could not get audio duration: {e}")
        return []
    
    # Calculate chunks
    num_chunks = math.ceil(file_size / MAX_FILE_SIZE_BYTES)
    chunk_duration = duration / num_chunks
    print(f"⏱️  Audio duration: {duration:.2f}s, splitting into {num_chunks} chunks")
    
    chunks = []
    base_name = Path(audio_path).stem
    ext = Path(audio_path).suffix
    
    for i in range(num_chunks):
        start_time = i * chunk_duration
        chunk_path = f"{base_name}_part{i+1}{ext}"
        
        print(f"🎵 Creating chunk {i+1}/{num_chunks}...")
        
        try:
            cmd = [
                "ffmpeg",
                "-i", audio_path,
                "-ss", str(start_time),
                "-t", str(chunk_duration),
                "-vn",
                "-acodec", "libmp3lame",
                "-ar", "16000",
                "-ac", "1",
                "-b:a", "64k",
                "-y",
                chunk_path
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            
            if os.path.exists(chunk_path):
                chunk_size_mb = os.path.getsize(chunk_path) / (1024 * 1024)
                print(f"   Chunk {i+1}: {chunk_size_mb:.2f} MB")
                chunks.append(chunk_path)
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create chunk {i+1}: {e.stderr.decode()}")
            continue
    
    return chunks


def transcribe_with_groq(audio_path: str, language: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Transcribe audio file using Groq Whisper API via official library
    """
    print(f"🤖 Transcribing {audio_path}...")
    
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY environment variable not set")
        return None
    
    try:
        with open(audio_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(audio_path), file),
                model="whisper-large-v3-turbo",
                response_format="verbose_json",
                timestamp_granularities=["word", "segment"],
                language=language,
                temperature=0.0
            )
            
            # Convert response object to dictionary
            result = {
                "text": transcription.text,
                "segments": getattr(transcription, 'segments', []),
                "words": getattr(transcription, 'words', [])
            }
            
            print(f"✅ Transcription complete!")
            return result
                
    except Exception as e:
        print(f"❌ Transcription failed: {str(e)}")
        return None


def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to SRT timestamp format: HH:MM:SS,mmm
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt(segments: List[Dict[str, Any]], output_path: str) -> bool:
    """
    Generate SRT subtitle file from transcription segments
    """
    print(f"📝 Generating SRT file: {output_path}...")
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            subtitle_index = 1
            for segment in segments:
                start_time = segment.get("start", 0)
                end_time = segment.get("end", 0)
                text = segment.get("text", "").strip()
                
                if not text:
                    continue
                
                # Write SRT entry
                f.write(f"{subtitle_index}\n")
                f.write(f"{format_timestamp(start_time)} --> {format_timestamp(end_time)}\n")
                f.write(f"{text}\n\n")
                subtitle_index += 1
        
        print(f"✅ SRT file generated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to generate SRT: {str(e)}")
        return False


def process_video(video_path: str, srt_output_path: Optional[str] = None, 
                  language: Optional[str] = None) -> bool:
    """
    Main function to process a video file and generate subtitles
    """
    if not check_ffmpeg():
        return False
    
    video_path_obj = Path(video_path).resolve()
    if not video_path_obj.exists():
        print(f"❌ Video file not found: {video_path_obj}")
        return False
    
    # Generate output paths
    if srt_output_path is None:
        srt_output_path = str(video_path_obj.with_suffix('.srt'))
    
    audio_temp_path = str(video_path_obj.with_suffix('.tmp.mp3'))
    
    try:
        # Step 1: Extract audio
        if not extract_audio(str(video_path), str(audio_temp_path)):
            return False
        
        # Step 2: Compress/split audio
        audio_chunks = compress_audio_if_needed(str(audio_temp_path))
        if not audio_chunks:
            return False
        
        # Step 3: Transcribe each chunk
        all_segments = []
        chunk_offsets = []
        
        # Calculate offsets for each chunk
        current_offset = 0
        for chunk_path in audio_chunks:
            # Get duration of this chunk
            try:
                cmd = [
                    "ffprobe",
                    "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "json",
                    chunk_path
                ]
                result = subprocess.run(cmd, capture_output=True, check=True, text=True)
                duration = float(json.loads(result.stdout)["format"]["duration"])
            except:
                duration = 0
            
            chunk_offsets.append(current_offset)
            current_offset += duration
        
        # Transcribe chunks and apply offsets
        for i, chunk_path in enumerate(audio_chunks):
            result = transcribe_with_groq(chunk_path, language)
            if result and result["segments"]:
                offset = chunk_offsets[i]
                for segment in result["segments"]:
                    segment["start"] += offset
                    segment["end"] += offset
                    all_segments.append(segment)
            
            # Clean up chunk file
            try:
                Path(chunk_path).unlink()
            except:
                pass
        
        if not all_segments:
            print("❌ No transcription segments found")
            return False
        
        # Sort segments by start time (in case of any overlap issues)
        all_segments.sort(key=lambda x: x.get("start", 0))
        
        # Step 4: Generate SRT
        success = generate_srt(all_segments, str(srt_output_path))
        
        # Clean up temp audio file
        try:
            Path(audio_temp_path).unlink()
        except:
            pass
        
        return success
        
    except Exception as e:
        print(f"❌ Processing failed: {str(e)}")
        return False


def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Usage: python video_to_subtitle.py <video_file> [output_srt] [language]")
        print("\nExamples:")
        print("  python video_to_subtitle.py video.mp4")
        print("  python video_to_subtitle.py video.mp4 subtitles.srt")
        print("  python video_to_subtitle.py video.mp4 subtitles.srt en")
        sys.exit(1)
    
    video_file = sys.argv[1]
    srt_file = sys.argv[2] if len(sys.argv) > 2 else None
    language = sys.argv[3] if len(sys.argv) > 3 else None
    
    print("🎬 Video to Subtitle Generator")
    print(f"📁 Input: {video_file}")
    if srt_file:
        print(f"📝 Output: {srt_file}")
    if language:
        print(f"🌐 Language: {language}")
    
    success = process_video(video_file, srt_file, language)
    
    if success:
        print("\n✅ Success! Subtitles generated.")
    else:
        print("\n❌ Failed to generate subtitles.")
        sys.exit(1)


if __name__ == "__main__":
    main()
