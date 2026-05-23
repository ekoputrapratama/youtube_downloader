import sys
import yt_dlp
import requests
import json
import os
import logging
from bs4 import BeautifulSoup
from velra.core.Bridge import BridgeObject, Bridge
from velra.qt.core import Signal, QObject, Slot, QThread, QStandardPaths
from velra.qt.gui import QDesktopServices
from velra.qt.webchannel import QWebChannel
from velra.qt.widgets import QFileDialog
from velra.browser.webengine.WebView import VWebEnginePage
from typing import Optional, Any, Literal, get_args
from typing_extensions import LiteralString
from tempfile import mkdtemp
from packaging.version import Version
import ffmpeg_downloader as ffdl

isLinux = sys.platform.startswith('linux')
isWindows = sys.platform.startswith('win')
ytdlp: Optional["YTDLP"] = None
ytdlpLog = logging.getLogger("ytdlp")


def compose_version_spec(version: Version | Literal["snapshot"], option: LiteralString | None = None):
  return f"{version}@{option}" if option else str(version)


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


class FfmpegDownloadHandler(QThread):
  _downloader: Optional["FfmpegDownloader"]

  def __init__(self, parent=None, downloader=None):
    QThread.__init__(self, parent)
    self._downloader = downloader

  def run(self):
    cacheDir = ffdl._backend.cache_dir()
    releases = ffdl._backend.list()
    latestVersion = max([b.version for b in releases])
    latestBuild = [b for b in releases if b.version == latestVersion][0]
    # find existing version
    current_version, _, _ = ffdl._backend.ffmpeg_version()
    shouldUpgrade = latestVersion > current_version
    ytdlpLog.debug(f"latest version {latestBuild}")

    if not ffdl.installed() or shouldUpgrade:
      dstpaths = ffdl._backend.download(latestBuild, dst=cacheDir, no_cache_dir=True, proxy=None, retries=None, timeout=None, progress=None)
      ytdlpLog.debug(f"destination path {dstpaths}")
      ffdl._backend.install(*dstpaths, progress=None)

    ytdlpLog.debug(f"ffmpeg path {ffdl.ffmpeg_path}")
    # if self._downloader is not None:
    assert self._downloader is not None
    # sometimes this code emit the event too fast, so the javascript event is not fired in the client
    self.sleep(1)
    self._downloader.onFinished.emit(ffdl.ffmpeg_path)


class FfmpegDownloader(BridgeObject):
  onFinished = Signal(str)
  _handler = None

  def __init__(self, parent=None, *args, **kwargs):
    QObject.__init__(self, parent=parent)
    self._handler = FfmpegDownloadHandler(downloader=self, parent=self)

  @Slot()
  def start(self):
    assert self._handler is not None
    self._handler.start()


class DownloadHandler(QThread):
  _queue: Optional["DownloadQueue"] = None
  _item: Optional[dict]

  def __init__(self, parent=None, queue=None, item=None):
    QThread.__init__(self, parent)
    self._queue = queue
    self._item = item

  def run(self):
    assert self._queue is not None
    assert self._item is not None
    assert self._queue._ydl is not None
    self._queue._ydl.download([self._item["url"]])


class DownloadQueue(BridgeObject):
  onProgress = Signal(str)
  _item: Optional[dict] = None
  _ydl = None
  _handler = None
  _currentDownloadProgress = None

  def __init__(self, options: dict[str, Any], parent=None, item=None, *args, **kwargs):
    QObject.__init__(self, parent=parent)
    self._item = item
    assert item is not None
    if item["type"] == "audio":
      format = f"{item['format']}/bestaudio/best"
      paths: dict[str, str] = dict()
      paths['home'] = item["downloadDirectory"]
      self._ydl = yt_dlp.YoutubeDL({  # noqa
        "ffmpeg_location":
        options["ffmpeg_location"],
        "paths":
        paths,
        "noplaylist":
        item["noPlaylist"],
        "format":
        format,
        # 'logger': self.logger,
        'progress_hooks': [self.progressHook],
        "postprocessors": [{  # Extract audio using ffmpeg
          "key": "FFmpegExtractAudio",
          "preferredcodec": item['format'],
        }]
      })  # type: ignore
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
    assert self._item is not None
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
      item = dict(self._item)
      item["status"] = "Downloading"
      item["percentage"] = percentage
      progress = json.dumps(item)
      self.onProgress.emit(progress)

  @Slot()
  def start(self):
    assert self._handler is not None
    self._handler.start()


class YTDLP(BridgeObject):
  noop_signal = Bridge.signal()

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  @Slot(result=FfmpegDownloader)
  def initializeFfmpeg(self):
    handler = FfmpegDownloader(parent=self)
    handler.start()
    return handler

  @Slot(str, str, result=DownloadQueue)
  def download(self, jsonStr: str, options: str):
    try:
      item = json.loads(jsonStr)
      opts = json.loads(options)
      assert item is not None
      downloadQueue = DownloadQueue(parent=self, item=item, options=opts)
      return downloadQueue
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

  @Slot(result=str)
  def selectDirectory(self):
    return QFileDialog.getExistingDirectory(None, "Select Directory")

  @Slot(result=str)
  def getDefaultDownloadDirectory(self):
    return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)


def beforeLoad(channel: QWebChannel, page: VWebEnginePage) -> None:
  current_dir = os.path.dirname(os.path.abspath(__file__))
  sys.path.append(current_dir)
  global ytdlp  # noqa
  assert ytdlp is not None
  channel.registerObject("YTDLP", ytdlp)


def activate() -> None:
  global ytdlp
  if ytdlp is None:
    ytdlp = YTDLP()


def deactivate() -> None:
  global ytdlp
  ytdlp = None
