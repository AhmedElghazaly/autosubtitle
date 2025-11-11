# AutoSubtitle GUI 🎬

A modern, user-friendly GUI application for converting videos to subtitle files using AI-powered transcription. Now with custom API key support and enhanced user experience!

## ✨ Latest Updates (v2.0)

🆕 **NEW FEATURES:**
- **Custom API Key Support**: Use your own Groq API key for unlimited usage
- **API Key Management**: Save, toggle visibility, and persist settings
- **Configuration System**: Settings automatically saved to config.ini
- **Enhanced Error Handling**: Improved user feedback and error recovery
- **Fixed Button Issues**: Resolved button color problems for smooth operation

## Features

### 🎨 **Modern Interface**
- Clean, responsive dark/light theme design with persistent settings
- Intuitive file selection with browse functionality
- Real-time progress tracking with visual feedback
- Professional color scheme and layout
- Configuration management with automatic persistence

### 🚀 **Powerful Processing**
- AI-powered transcription using Groq Whisper API
- Custom API key support - use your own key for unlimited usage
- Multiple language support (Auto-detect, English, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese, Korean, Arabic)
- Automatic audio compression and splitting for large files
- Progress tracking with detailed status updates
- Threaded processing - GUI stays responsive during operations

### 🎯 **User-Friendly**
- Simple setup with automatic dependency checking
- One-click file selection and processing
- Automatic output file naming
- API key input with visibility toggle (👁️ ↔ 🙈)
- Save API key functionality with persistent storage
- Error handling with user-friendly messages
- Open output folder functionality

## Installation

### Prerequisites

1. **Python 3.13+**
2. **ffmpeg** (required for audio extraction)
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # macOS
   brew install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

### Quick Start

1. **Clone or download the project**
2. **Run the GUI launcher:**
   ```bash
   python start_gui.py
   ```

The launcher will automatically:
- Check and install missing dependencies
- Verify ffmpeg installation
- Start the GUI application

### Manual Installation

If you prefer to install dependencies manually:

```bash
pip install customtkinter Pillow groq configparser
```

## Usage

### GUI Application

#### 1. **Start the application:**
```bash
python gui_app.py
```
or
```bash
python start_gui.py
```

#### 2. **Configure API Key :**
- Click on the "Groq API Key" field
- Enter your API key from [console.groq.com](https://console.groq.com)
- Click "👁️" to toggle visibility if needed
- Click "💾 Save" to store your key securely
- Your key will be saved to `config.ini` and used automatically

#### 3. **Select a video file:**
- Click the file selection box to browse for videos
- Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WEBM, M4V
- Output SRT file path will be auto-generated (or set custom location)

#### 4. **Configure settings:**
- **Language**: Choose from 12 languages or use auto-detect
- **Output SRT**: Set custom output path (optional)

#### 5. **Start processing:**
- Click "🎬 Start Processing"
- Watch real-time progress updates
- See detailed status messages (🔍 Checking, 🎵 Extracting, 🤖 Transcribing, etc.)
- Wait for completion notification

#### 6. **Access results:**
- Click "📁 Open Output Folder" to view generated SRT file
- Find your subtitle file with the same name as your video

### Theme Toggle
- Click the "🌓" button in the header to toggle between dark and light themes
- Theme preference is automatically saved

### Command Line Interface

The original CLI functionality is still available:

```bash
python aisub.py <video_file> [output_srt] [language]
```

Examples:
```bash
python aisub.py video.mp4
python aisub.py video.mp4 subtitles.srt
python aisub.py video.mp4 subtitles.srt en
```

## Architecture

### Files Structure

```
autosubtitle/
├── gui_app.py          # Main GUI application with API key support
├── start_gui.py        # Smart launcher with dependency checking
├── config.ini          # Configuration file (auto-generated)
├── README_GUI.md       # Complete documentation
├── FINAL_STATUS.md     # Implementation summary
├── aisub.py            # Original CLI functionality
└── AGENTS.md           # Development guidelines
```

### Dependencies

- **customtkinter**: Modern GUI components
- **Pillow**: Image processing for enhanced UI
- **configparser**: Configuration file management
- **groq**: AI transcription API client
- **tkinter**: Python's built-in GUI toolkit
- **subprocess**: External process management (ffmpeg)

## Features Breakdown

### 🎨 Modern UI Design
- **CustomTkinter Framework**: Provides modern, native-looking widgets
- **Dark/Light Themes**: Toggle between visual themes with persistence
- **Responsive Layout**: Adapts to different window sizes
- **Progress Tracking**: Real-time visual feedback with detailed status
- **Configuration Management**: Settings saved automatically

### 🔧 Processing Pipeline
1. **Audio Extraction**: Extract audio from video using ffmpeg
2. **Compression**: Optimize file size for API limits (<18MB)
3. **Splitting**: Handle large files by chunking
4. **Transcription**: AI-powered speech-to-text conversion
5. **SRT Generation**: Format results into standard subtitle files
6. **Cleanup**: Remove temporary files automatically

### 🌍 Multi-Language Support
- **Auto-detect**: Automatically identify spoken language
- **Manual Selection**: Choose from 12 supported languages
- **High Accuracy**: Powered by Groq's advanced Whisper model

### 🔑 API Key Management
- **Custom Keys**: Use your own Groq API key for unlimited usage
- **Secure Input**: Password-masked input field with visibility toggle
- **Persistent Storage**: API keys saved securely in config.ini
- **Auto-Loading**: Saved keys automatically loaded on startup

### 🚀 Performance Optimizations
- **Threaded Processing**: GUI remains responsive during processing
- **Memory Management**: Efficient cleanup of temporary files
- **Error Handling**: Graceful failure recovery with user feedback
- **Progress Updates**: Real-time status updates throughout pipeline

## API Key Setup

### Get Your Free API Key

1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Generate a new API key
4. Copy your API key

### Configure in GUI

1. **Enter API Key**: 
   - Click on the "Groq API Key" field
   - Paste your API key
   - Click "👁️" to verify (toggle visibility)

2. **Save Configuration**:
   - Click "💾 Save" button
   - Key is stored securely in `config.ini`
   - Settings persist across application restarts

3. **Verify Usage**:
   - Start processing a video
   - Check console output for "Using custom API key" message
   - Monitor your usage at console.groq.com

> **💡 Benefits of Custom API Key:**
> - No usage limits from demo keys
> - Personal usage tracking
> - More reliable processing
> - Professional-grade reliability

## Troubleshooting

### Common Issues

**"ffmpeg not found"**
- Install ffmpeg using your system's package manager
- Verify installation: `ffmpeg -version`

**"No valid API key provided"**
- Enter your Groq API key in the settings
- Click "💾 Save" to store it
- Restart the application if needed

**"No display found" (Linux)**
- Ensure X11 forwarding is enabled for GUI applications
- Try running: `export DISPLAY=:0`
- Check if GUI environment is properly configured

**Import errors**
- Run `python start_gui.py` to auto-install dependencies
- Or manually: `pip install customtkinter Pillow groq configparser`

**Button color issues**
- This has been fixed in v2.0
- If you encounter any button issues, restart the application

### GUI Issues

**Application won't start**
1. Check Python version (3.13+)
2. Verify display availability
3. Ensure all dependencies are installed
4. Try CLI version as fallback

**Processing fails**
1. Check ffmpeg installation
2. Verify video file is not corrupted
3. Ensure sufficient disk space
4. Check API key validity
5. Monitor Groq API usage limits

**API Key Problems**
1. Verify API key is valid at console.groq.com
2. Check if you've exceeded usage limits
3. Try regenerating a new API key
4. Ensure proper formatting (no extra spaces)

### Performance Issues

**Slow processing**
- Large video files take more time
- Check internet connection for API calls
- Monitor system resources

**Memory usage**
- Application cleans up temporary files automatically
- Large files may temporarily use more memory during processing

## Configuration File

The application automatically creates and manages `config.ini`:

```ini
[api]
groq_api_key = your_key_here
use_default = false

[settings]
default_language = auto
theme = dark
auto_save_output = true

[paths]
default_output_dir = 
temp_dir = temp
```

### Managing Configuration

- **Automatic**: Settings are saved automatically
- **Manual**: Edit config.ini directly if needed
- **Reset**: Delete config.ini to reset to defaults
- **Backup**: Configuration file can be backed up easily



## Version History

### v2.0 (Latest)
- ✅ Fixed button color issue (no more None errors)
- ✅ Added custom API key configuration
- ✅ Added API key visibility toggle
- ✅ Added persistent configuration management
- ✅ Enhanced error handling
- ✅ Improved user interface

### v1.0
- ✅ Initial GUI implementation
- ✅ Basic file selection and processing
- ✅ Progress tracking
- ✅ Theme support

---

🎬 **Enjoy creating subtitles with AI-powered accuracy, modern convenience, and unlimited API key support!**
