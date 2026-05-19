# YouTube Downloader (GUI)

A lightweight, intuitive graphical user interface for yt-dlp, built with PySide6. This application allows you to easily fetch content from YouTube and other supported platforms without touching the command line.

### Support the project

<a href="https://www.buymeacoffee.com/ekoputraprm" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

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
