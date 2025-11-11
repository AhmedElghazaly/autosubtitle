#!/usr/bin/env python3
"""
AutoSubtitle GUI Application
Modern, responsive GUI for converting videos to subtitles
Fixed button color issue and added API key configuration
"""

import os
import sys
import threading
import math
import json
import configparser
import tkinter as tk
from pathlib import Path
from typing import Optional, List, Dict, Any
import subprocess

try:
    import customtkinter as ctk
    from tkinter import filedialog, messagebox
    from PIL import Image
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Please install: pip install customtkinter pillow")
    sys.exit(1)

# Import existing functionality
import aisub

# Configure CustomTkinter
ctk.set_appearance_mode("dark")  # Options: "dark", "light", "system"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

class ConfigManager:
    """Manage application configuration"""
    def __init__(self):
        self.config_file = Path("config.ini")
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            self.config.read(self.config_file)
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration file"""
        self.config['api'] = {
            'groq_api_key': '',
            'use_default': 'true'
        }
        self.config['settings'] = {
            'default_language': 'auto',
            'theme': 'dark',
            'auto_save_output': 'true'
        }
        self.config['paths'] = {
            'default_output_dir': '',
            'temp_dir': 'temp'
        }
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get_api_key(self) -> str:
        """Get API key from config"""
        return self.config.get('api', 'groq_api_key', fallback='')
    
    def set_api_key(self, api_key: str):
        """Set API key in config"""
        self.config.set('api', 'groq_api_key', api_key)
        self.save_config()
    
    def get_default_language(self) -> str:
        """Get default language"""
        return self.config.get('settings', 'default_language', fallback='auto')

class AutoSubtitleGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.config = ConfigManager()
        self.setup_window()
        self.setup_variables()
        self.create_widgets()
        
    def setup_window(self):
        """Configure main window"""
        self.root.title("AutoSubtitle - Video to SRT Converter")
        self.root.geometry("900x750")  # Slightly taller for API key section
        self.root.minsize(800, 650)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (750 // 2)
        self.root.geometry(f"900x750+{x}+{y}")
    
    def setup_variables(self):
        """Initialize variables"""
        self.selected_file = ctk.StringVar()
        self.output_file = ctk.StringVar()
        self.language = ctk.StringVar(value=self.config.get_default_language())
        self.api_key = ctk.StringVar(value=self.config.get_api_key())
        self.progress_value = ctk.DoubleVar()
        self.status_text = ctk.StringVar(value="Ready")
        self.is_processing = False
        
        # Supported languages
        self.languages = {
            "Auto-detect": "auto",
            "English": "en",
            "Spanish": "es", 
            "French": "fr",
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
            "Russian": "ru",
            "Chinese": "zh",
            "Japanese": "ja",
            "Korean": "ko",
            "Arabic": "ar"
        }
    
    def create_widgets(self):
        """Create and arrange GUI widgets"""
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Header
        self.create_header()
        
        # Main content
        self.create_main_content()
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Create header section"""
        header_frame = ctk.CTkFrame(self.root, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Logo/Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="🎬 AutoSubtitle",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.grid(row=0, column=1, sticky="w", padx=(20, 10), pady=20)
        
        # Theme toggle
        self.theme_button = ctk.CTkButton(
            header_frame,
            text="🌓",
            width=40,
            command=self.toggle_theme
        )
        self.theme_button.grid(row=0, column=2, padx=(10, 20), pady=20)
    
    def create_main_content(self):
        """Create main content area"""
        main_frame = ctk.CTkScrollableFrame(self.root)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # File selection section
        self.create_file_section(main_frame)
        
        # Settings section
        self.create_settings_section(main_frame)
        
        # Progress section
        self.create_progress_section(main_frame)
        
        # Action buttons
        self.create_action_section(main_frame)
    
    def create_file_section(self, parent):
        """Create file selection section"""
        file_frame = ctk.CTkFrame(parent)
        file_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        file_frame.grid_columnconfigure(1, weight=1)
        
        # Section title
        title_label = ctk.CTkLabel(
            file_frame,
            text="📁 Select Video File",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=20, pady=(20, 10))
        
        # File selection frame
        selection_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        selection_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=(0, 20))
        selection_frame.grid_columnconfigure(1, weight=1)
        
        # File path entry
        self.file_entry = ctk.CTkEntry(
            selection_frame,
            placeholder_text="Select a video file...",
            textvariable=self.selected_file,
            font=ctk.CTkFont(size=14)
        )
        self.file_entry.grid(row=0, column=0, columnspan=2, sticky="ew", padx=(0, 10))
        
        # Browse button
        browse_button = ctk.CTkButton(
            selection_frame,
            text="Browse",
            width=100,
            command=self.browse_file
        )
        browse_button.grid(row=0, column=2, sticky="e")
        
        # Drag & drop info
        drop_label = ctk.CTkLabel(
            file_frame,
            text="💡 Tip: Click the text box to select a video file",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        drop_label.grid(row=2, column=0, columnspan=3, padx=20, pady=(0, 20))
    
    def create_settings_section(self, parent):
        """Create settings section"""
        settings_frame = ctk.CTkFrame(parent)
        settings_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        settings_frame.grid_columnconfigure((1, 3), weight=1)
        
        # Section title
        title_label = ctk.CTkLabel(
            settings_frame,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=4, sticky="w", padx=20, pady=(20, 10))
        
        # API Key section
        api_label = ctk.CTkLabel(settings_frame, text="Groq API Key:")
        api_label.grid(row=1, column=0, sticky="w", padx=(20, 10), pady=(0, 20))
        
        api_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        api_frame.grid(row=1, column=1, columnspan=2, sticky="ew", pady=(0, 20))
        api_frame.grid_columnconfigure(0, weight=1)
        
        self.api_entry = ctk.CTkEntry(
            api_frame,
            placeholder_text="Enter your Groq API key or leave empty to use default",
            textvariable=self.api_key,
            font=ctk.CTkFont(size=14),
            show="*"
        )
        self.api_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Toggle API key visibility
        self.api_visible = False
        self.api_toggle_button = ctk.CTkButton(
            api_frame,
            text="👁️",
            width=40,
            command=self.toggle_api_visibility
        )
        self.api_toggle_button.grid(row=0, column=1, sticky="e")
        
        # Save API key button
        self.save_api_button = ctk.CTkButton(
            api_frame,
            text="💾 Save",
            width=60,
            command=self.save_api_key
        )
        self.save_api_button.grid(row=0, column=2, sticky="e", padx=(5, 0))
        
        # API Key help
        api_help_label = ctk.CTkLabel(
            settings_frame,
            text="💡 Get your free API key from console.groq.com",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        api_help_label.grid(row=2, column=1, columnspan=2, sticky="w", pady=(0, 10))
        
        # Language selection
        lang_label = ctk.CTkLabel(settings_frame, text="Language:")
        lang_label.grid(row=3, column=0, sticky="w", padx=(20, 10), pady=(0, 20))
        
        self.language_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=list(self.languages.keys()),
            variable=self.language,
            font=ctk.CTkFont(size=14)
        )
        self.language_menu.grid(row=3, column=1, sticky="w", pady=(0, 20))
        
        # Output file selection
        output_label = ctk.CTkLabel(settings_frame, text="Output SRT:")
        output_label.grid(row=3, column=2, sticky="w", padx=(20, 10), pady=(0, 20))
        
        output_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        output_frame.grid(row=3, column=3, sticky="ew", pady=(0, 20))
        output_frame.grid_columnconfigure(0, weight=1)
        
        self.output_entry = ctk.CTkEntry(
            output_frame,
            placeholder_text="Leave empty to auto-generate...",
            textvariable=self.output_file,
            font=ctk.CTkFont(size=14)
        )
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        output_browse = ctk.CTkButton(
            output_frame,
            text="Browse",
            width=100,
            command=self.browse_output_file
        )
        output_browse.grid(row=0, column=1, sticky="e")
    
    def create_progress_section(self, parent):
        """Create progress section"""
        progress_frame = ctk.CTkFrame(parent)
        progress_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        progress_frame.grid_columnconfigure(1, weight=1)
        
        # Section title
        title_label = ctk.CTkLabel(
            progress_frame,
            text="📊 Progress",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=20, pady=(20, 10))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            variable=self.progress_value,
            height=20
        )
        self.progress_bar.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=(0, 10))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            progress_frame,
            textvariable=self.status_text,
            font=ctk.CTkFont(size=14)
        )
        self.status_label.grid(row=2, column=0, columnspan=3, padx=20, pady=(0, 20))
        
        # Initialize progress bar
        self.progress_bar.set(0)
    
    def create_action_section(self, parent):
        """Create action buttons section"""
        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        action_frame.grid_columnconfigure(1, weight=1)
        
        # Start/Stop button
        self.action_button = ctk.CTkButton(
            action_frame,
            text="🎬 Start Processing",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            command=self.toggle_processing,
            state="disabled"
        )
        self.action_button.grid(row=0, column=1, padx=20, pady=20, sticky="ew")
        
        # Open output folder button
        self.open_button = ctk.CTkButton(
            action_frame,
            text="📁 Open Output Folder",
            font=ctk.CTkFont(size=14),
            height=40,
            command=self.open_output_folder,
            state="disabled"
        )
        self.open_button.grid(row=0, column=2, padx=(0, 20), pady=20, sticky="e")
    
    def create_footer(self):
        """Create footer with info"""
        footer_frame = ctk.CTkFrame(self.root, height=50)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))
        footer_frame.grid_columnconfigure(1, weight=1)
        
        # Info text
        info_text = "Powered by Groq Whisper API • Modern GUI • Custom API Key Support"
        info_label = ctk.CTkLabel(
            footer_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        info_label.grid(row=0, column=1, sticky="ew", pady=15)
    
    def toggle_api_visibility(self):
        """Toggle API key visibility"""
        if self.api_visible:
            self.api_entry.configure(show="*")
            self.api_visible = False
            self.api_toggle_button.configure(text="👁️")
        else:
            self.api_entry.configure(show="")
            self.api_visible = True
            self.api_toggle_button.configure(text="🙈")
    
    def save_api_key(self):
        """Save API key to configuration"""
        api_key = self.api_key.get().strip()
        if api_key:
            self.config.set_api_key(api_key)
            self.show_success("API key saved successfully!")
        else:
            self.show_error("Please enter a valid API key")
    
    def is_video_file(self, file_path: str) -> bool:
        """Check if file is a supported video format"""
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
        return Path(file_path).suffix.lower() in video_extensions
    
    def browse_file(self):
        """Browse for input video file"""
        filetypes = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm *.m4v"),
            ("MP4 files", "*.mp4"),
            ("AVI files", "*.avi"),
            ("MOV files", "*.mov"),
            ("MKV files", "*.mkv"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select a video file",
            filetypes=filetypes
        )
        
        if filename:
            self.selected_file.set(filename)
            
            # Auto-generate output path if empty
            if not self.output_file.get():
                video_path = Path(filename)
                suggested_output = str(video_path.with_suffix('.srt'))
                self.output_file.set(suggested_output)
            
            self.update_action_button_state()
    
    def browse_output_file(self):
        """Browse for output SRT file"""
        filename = filedialog.asksaveasfilename(
            title="Save SRT file as",
            defaultextension=".srt",
            filetypes=[("SRT files", "*.srt"), ("All files", "*.*")]
        )
        
        if filename:
            self.output_file.set(filename)
    
    def update_action_button_state(self):
        """Update the state of the action button"""
        has_file = bool(self.selected_file.get() and self.is_video_file(self.selected_file.get()))
        self.action_button.configure(state="normal" if has_file else "disabled")
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "light" if current_mode == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        
        # Update theme button text
        self.theme_button.configure(text="☀️" if new_mode == "dark" else "🌙")
    
    def toggle_processing(self):
        """Start or stop processing"""
        if self.is_processing:
            self.stop_processing()
        else:
            self.start_processing()
    
    def start_processing(self):
        """Start the subtitle generation process"""
        if not self.selected_file.get():
            self.show_error("Please select a video file first.")
            return
        
        self.is_processing = True
        self.action_button.configure(text="⏹️ Stop Processing", fg_color="#ff6b6b")
        self.progress_bar.set(0)
        self.status_text.set("Starting...")
        
        # Start processing in a separate thread
        self.processing_thread = threading.Thread(target=self.process_video_thread, daemon=True)
        self.processing_thread.start()
    
    def stop_processing(self):
        """Stop the processing"""
        self.is_processing = False
        # Fix: Use proper theme color instead of None
        button_fg_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        self.action_button.configure(
            text="🎬 Start Processing", 
            fg_color=button_fg_color
        )
        self.progress_bar.set(0)
        self.status_text.set("Stopped")
    
    def update_processing_function(self):
        """Update the aisub processing function to use custom API key"""
        # Set API key for this session
        if self.api_key.get():
            # Create a modified version of the Groq client
            client = aisub.Groq(api_key=self.api_key.get())
            
            # Monkey patch the client in aisub module
            aisub.client = client
            print(f"Using custom API key: {self.api_key.get()[:10]}...")
        else:
            # Reset to default
            client = aisub.Groq(api_key=aisub.GROQ_API_KEY)
            aisub.client = client
            print("Using default API key")
    
    def process_video_thread(self):
        """Process video in a separate thread"""
        try:
            # Update API key before processing
            self.update_processing_function()
            
            video_file = self.selected_file.get()
            output_file = self.output_file.get() if self.output_file.get() else None
            language_code = self.languages.get(self.language.get(), "auto")
            
            # Update progress in GUI thread
            def update_progress(step, total_steps, message):
                progress = step / total_steps
                self.root.after(0, lambda: self.progress_bar.set(progress))
                self.root.after(0, lambda: self.status_text.set(message))
            
            # Call the actual processing function with progress updates
            success = self.run_processing_with_progress(
                video_file, output_file, language_code, update_progress
            )
            
            if success and self.is_processing:
                self.root.after(0, self.processing_completed)
            elif self.is_processing:
                self.root.after(0, self.processing_failed, "Failed to process video")
                
        except Exception as e:
            if self.is_processing:
                self.root.after(0, self.processing_failed, str(e))
    
    def run_processing_with_progress(self, video_file, output_file, language_code, update_progress):
        """Run the actual processing with progress updates"""
        try:
            # Step 1: Check ffmpeg
            update_progress(1, 6, "🔍 Checking dependencies...")
            if not aisub.check_ffmpeg():
                return False
            
            # Step 2: Extract audio
            update_progress(2, 6, "🎵 Extracting audio...")
            video_path = Path(video_file)
            audio_temp_path = str(video_path.with_suffix('.tmp.mp3'))
            
            if not aisub.extract_audio(video_file, audio_temp_path):
                return False
            
            # Step 3: Compress audio
            update_progress(3, 6, "📊 Compressing audio...")
            audio_chunks = aisub.compress_audio_if_needed(audio_temp_path)
            if not audio_chunks:
                return False
            
            # Step 4: Transcribe
            update_progress(4, 6, "🤖 Transcribing with AI...")
            all_segments = []
            chunk_offsets = []
            
            # Calculate offsets
            current_offset = 0
            for chunk_path in audio_chunks:
                try:
                    cmd = [
                        "ffprobe", "-v", "error", "-show_entries", 
                        "format=duration", "-of", "json", chunk_path
                    ]
                    result = subprocess.run(cmd, capture_output=True, check=True, text=True)
                    duration = float(json.loads(result.stdout)["format"]["duration"])
                except:
                    duration = 0
                
                chunk_offsets.append(current_offset)
                current_offset += duration
            
            # Transcribe chunks
            for i, chunk_path in enumerate(audio_chunks):
                if not self.is_processing:
                    return False
                    
                result = aisub.transcribe_with_groq(
                    chunk_path, 
                    language_code if language_code != "auto" else None
                )
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
            
            # Step 5: Generate SRT
            update_progress(5, 6, "📝 Generating SRT file...")
            if not all_segments:
                return False
            
            # Sort segments
            all_segments.sort(key=lambda x: x.get("start", 0))
            
            # Generate final output path
            if output_file is None:
                output_file = str(Path(video_file).with_suffix('.srt'))
            
            success = aisub.generate_srt(all_segments, output_file)
            
            # Step 6: Cleanup
            update_progress(6, 6, "🧹 Cleaning up...")
            try:
                Path(audio_temp_path).unlink()
            except:
                pass
            
            return success
            
        except Exception as e:
            print(f"Processing error: {e}")
            return False
    
    def processing_completed(self):
        """Handle successful completion"""
        self.is_processing = False
        # Fix: Use proper theme color instead of None
        button_fg_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        self.action_button.configure(
            text="🎬 Start Processing", 
            fg_color=button_fg_color
        )
        self.status_text.set("✅ Subtitles generated successfully!")
        self.open_button.configure(state="normal")
        
        self.show_success("Subtitle generation completed successfully!")
    
    def processing_failed(self, error_msg):
        """Handle processing failure"""
        self.is_processing = False
        # Fix: Use proper theme color instead of None
        button_fg_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        self.action_button.configure(
            text="🎬 Start Processing", 
            fg_color=button_fg_color
        )
        self.status_text.set(f"❌ Failed: {error_msg}")
        
        self.show_error(f"Processing failed: {error_msg}")
    
    def open_output_folder(self):
        """Open the folder containing the output file"""
        output_path = self.output_file.get()
        if output_path:
            output_dir = Path(output_path).parent
            if output_dir.exists():
                if sys.platform.startswith('darwin'):  # macOS
                    subprocess.run(['open', str(output_dir)])
                elif sys.platform.startswith('win'):  # Windows
                    subprocess.run(['explorer', str(output_dir)])
                else:  # Linux
                    subprocess.run(['xdg-open', str(output_dir)])
    
    def show_success(self, message):
        """Show success message"""
        messagebox.showinfo("Success", message)
    
    def show_error(self, message):
        """Show error message"""
        messagebox.showerror("Error", message)
    
    def run(self):
        """Start the GUI application"""
        # Bind file selection changes
        self.selected_file.trace_add('write', lambda *args: self.update_action_button_state())
        
        # Start the main loop
        self.root.mainloop()


def main():
    """Main entry point"""
    app = AutoSubtitleGUI()
    app.run()


if __name__ == "__main__":
    main()