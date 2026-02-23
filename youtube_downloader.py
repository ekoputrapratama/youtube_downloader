#!/usr/bin/env python3
"""Simple launcher for velra."""
import youtube_downloader.youtube_downloader as youtube_downloader
import sys

RESTART_EXIT_CODE = 2

if __name__ == "__main__":
  sys.exit(youtube_downloader.main())
