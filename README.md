# YouTube Downloader (GUI)

A lightweight, intuitive graphical user interface for yt-dlp, built with PySide6. This application allows you to easily fetch content from YouTube and other supported platforms without touching the command line.

## 🚀 Features

- Video Downloads: Save videos in high quality (MP4/MKV).
- Audio Extraction: Convert videos directly to high-quality MP3 or M4A.
- Progress Tracking: Real-time download speed and ETA.
- Queue Management: (Optional: Add if your app supports multiple links).
- Cross-Platform: Works on Linux (X11/Wayland), Windows, and macOS.

## 🛠️ Prerequisites

Before running the app, ensure you have the following installed:

1. Python 3.8+

2. FFmpeg: Required for merging video/audio and converting to MP3.
   - Linux: sudo apt install ffmpeg
   - macOS: brew install ffmpeg

3. yt-dlp: The engine powering the downloads.

## Note

please don't try to run this using the source code, this project use a private package that is not available in pypi, so you cannot run it without this private package. I'll try to make the installer and publish it in github release later when i have time.
