# YouTube Downloader (GUI)

A lightweight, intuitive graphical user interface for yt-dlp, built with PySide6. This application allows you to easily fetch content from YouTube and other supported platforms without touching the command line.

### Support the project

<a href='https://ko-fi.com/ekoputrapratama' target='_blank'><img src="https://storage.ko-fi.com/cdn/brandasset/v2/support_me_on_kofi_blue.png" width="155" height="35"/></a>&nbsp;&nbsp;

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

### Additional requirements for WSL

- nvidia-libgl
- Network Security Services / nss
- libxcomposite
- libxdamage
- libxrandr
- libxtst
- libxkbfile
- libtiff
- libfbclient
- postgresql-libs
- mariadb-lts-libs
- unixodbc

## Note

please don't try to run this using the source code, this project use a private package that is not available in pypi, so you cannot run it without this private package. download the portable exe file [here](https://github.com/ekoputrapratama/youtube_downloader/releases).
