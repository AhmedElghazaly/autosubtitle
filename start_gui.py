#!/usr/bin/env python3
"""
AutoSubtitle GUI Launcher
Modern, user-friendly interface for converting videos to subtitles
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['customtkinter', 'PIL', 'groq']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                __import__('PIL')
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstalling missing packages...")
        
        for package in missing_packages:
            if package == 'PIL':
                package = 'Pillow'
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print("✅ Dependencies installed successfully!")

def check_ffmpeg():
    """Check if ffmpeg is available"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def show_startup_info():
    """Show startup information"""
    print("🎬 AutoSubtitle GUI - Modern Video to Subtitle Converter")
    print("=" * 60)
    print("Features:")
    print("• Modern, responsive GUI with dark/light themes")
    print("• Drag & drop file support")
    print("• Real-time progress tracking")
    print("• Multiple language support")
    print("• Automatic subtitle generation")
    print("• Powered by Groq Whisper API")
    print("=" * 60)
    print()

def main():
    """Main launcher function"""
    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Show startup information
    show_startup_info()
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    check_dependencies()
    
    # Check ffmpeg
    print("🎥 Checking ffmpeg...")
    if not check_ffmpeg():
        print("⚠️  ffmpeg not found. Please install it:")
        print("   Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("   macOS: brew install ffmpeg")
        print("   Windows: Download from https://ffmpeg.org/download.html")
        print()
        
        response = input("Continue anyway? (y/N): ").lower().strip()
        if response != 'y':
            print("Aborted. Please install ffmpeg first.")
            return
    
    print("✅ All checks passed!")
    print("\n🚀 Starting AutoSubtitle GUI...")
    print()
    print("✨ New features in this version:")
    print("• Custom API key configuration")
    print("• Modern dark/light theme support")
    print("• Improved error handling")
    print("• Real-time progress tracking")
    print()
    
    try:
        # Import and run the GUI application
        from gui_app import AutoSubtitleGUI
        app = AutoSubtitleGUI()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed")
        print("2. Check that you have a display available (for GUI)")
        print("3. Verify your Groq API key is set correctly")
        
        # Try running the CLI version as fallback
        print("\n🔄 Trying CLI version as fallback...")
        try:
            import aisub
            print("CLI version available. Run: python aisub.py <video_file>")
        except Exception as cli_error:
            print(f"CLI version also failed: {cli_error}")
            print("\nIf you continue to have issues, please check the documentation at README_GUI.md")

if __name__ == "__main__":
    main()