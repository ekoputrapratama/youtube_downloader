import sys
import yt_dlp
import requests
import json

from bs4 import BeautifulSoup
from velra.core.Bridge import BridgeObject, Bridge
from velra.qt.core import Signal, QObject, Slot, QThread
from velra.qt.gui import QDesktopServices
from velra.qt.webchannel import QWebChannel
from velra.browser.webengine.WebView import VWebEnginePage
from typing import Optional


isLinux = sys.platform.startswith('linux')
isWindows = sys.platform.startswith('win')
ytdlp: Optional["YTDLP"] = None


def get_site_title(url):
  """
  Fetches the title of a webpage from a given URL.
  """
  try:
      # Send a GET request to the URL
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    # Raise an exception for bad status codes (4xx or 5xx)
    response.raise_for_status()

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the <title> tag and get its text
    title_tag = soup.find('title')

    if title_tag:
      # Return the stripped text of the title tag
      return title_tag.get_text(strip=True)
    else:
      return "No title found"

  except requests.exceptions.RequestException as e:
      return f"Error fetching the page: {e}"


class YTDLPLogger:
  def __init__(self, ytdlp: "YTDLP"):
    self.ytdlp = ytdlp

  def debug(self, msg):
    # print(msg)
    pass

  def warning(self, msg):
    # print(msg)
    pass

  def error(self, msg):
    # print(msg)
    pass


class DownloadHandler(QThread):
  _queue: Optional["DownloadQueue"] = None
  _item: Optional[dict]

  def __init__(self, parent=None, queue=None, item=None):
    QThread.__init__(self, parent)
    self._queue = queue
    self._item = item
  
  def run(self):
    self._queue._ydl.download([self._item["url"]])


class DownloadQueue(BridgeObject):
  onProgress = Signal(str)
  _item: Optional[dict] = None
  _ydl = None
  _handler = None
  _currentDownloadProgress = None
  
  def __init__(self, parent=None, item=None, *args, **kwargs):
    QObject.__init__(self, parent=parent)
    self._item = item
    if item["type"] == "audio":
      format = f"{item['format']}/bestaudio/best"
      self._ydl = yt_dlp.YoutubeDL({
        "noplaylist": item["noPlaylist"], 
        "format": format,
        # 'logger': self.logger,
        'progress_hooks': [self.progressHook],
        "postprocessors": [{  # Extract audio using ffmpeg
          "key": "FFmpegExtractAudio",
          "preferredcodec": item['format'],
        }]
      })
    else:
      format = f"{item['format']}/bestvideo/best"
      self._ydl = yt_dlp.YoutubeDL({
        "noplaylist": item["noPlaylist"],
        "format": format,
        # 'logger': self.logger,
        'progress_hooks': [self.progressHook],
      })

    self._handler = DownloadHandler(queue=self, item=item)

  def progressHook(self, d):

    if d['status'] == 'finished':
      print('Done downloading, now post-processing... ')
      item = dict(self._item)
      item["status"] = "Finished"
      progress = json.dumps(item)
      self.onProgress.emit(progress)
    elif d['status'] == 'downloading':
      downloadedBytes = d['downloaded_bytes']
      totalBytes = d['total_bytes']
      percentage = downloadedBytes / totalBytes * 100
      print(f"percentage {percentage}")
      # self._currentDownloadProgress = DownloadProgress(percentage=percentage, item=self._item)
      item = dict(self._item)
      item["status"] = "Downloading"
      item["percentage"] = percentage
      progress = json.dumps(item)
      self.onProgress.emit(progress)
      # print("status downloading...") 

  @Slot()
  def start(self):
    self._handler.start()


class YTDLP(BridgeObject):
  noop_signal = Bridge.signal()

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  @Slot(str, result=DownloadQueue)
  def download(self, jsonStr: str):
    print(f"downloading {jsonStr}")
    deviceQueue = None
    try:
      item = json.loads(jsonStr)
      deviceQueue = DownloadQueue(parent=self, item=item)
      return deviceQueue
      # thread = threading.Thread(target=ydl.download, args=([item["url"]]))
      # thread.start()
    except Exception as e:
      print(f"failed configuring yt-dlp {e}")

    return None

  @Slot(str, result=str)
  def getTitle(self, url: str):
    title = get_site_title(url)
    return title.replace("- YouTube", "")

  @Slot(str, result=None)
  def openUrl(self, url: str):
    QDesktopServices.openUrl(url)


def beforeLoad(channel: QWebChannel, page: VWebEnginePage) -> None:
  global ytdlp
  assert ytdlp is not None
  channel.registerObject("YTDLP", ytdlp)


def activate() -> None:
  global ytdlp
  if ytdlp is None:
    ytdlp = YTDLP()


def deactivate() -> None:
  global ytdlp
  ytdlp = None
