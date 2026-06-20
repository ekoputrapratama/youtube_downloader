import sys
import json

from velra.core.Bridge import BridgeObject, Bridge
from velra.qt.core import Signal, QObject, Slot, QThread, QStandardPaths
from velra.qt.gui import QDesktopServices
from velra.qt.webchannel import QWebChannel
from velra.qt.widgets import QFileDialog
from velra.browser.webengine.WebView import VWebEnginePage
from typing import Optional
from .download_helper import DownloadQueue
from .ffdl import FfmpegDownloader
from .utils import log, getSiteTitle

isLinux = sys.platform.startswith('linux')
isWindows = sys.platform.startswith('win')
ytdlp: Optional["YTDLP"] = None


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


class YTDLP(BridgeObject):
  noop_signal = Bridge.signal()

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  @Slot(result=FfmpegDownloader)
  def initializeFfmpeg(self):
    handler = FfmpegDownloader(parent=self)
    return handler

  @Slot(str, str, result=DownloadQueue)
  def download(self, jsonStr: str, options: str):
    try:
      item = json.loads(jsonStr)
      opts = json.loads(options)
      assert item is not None
      downloadQueue = DownloadQueue(parent=self, item=item, options=opts)
      return downloadQueue
    except Exception as e:
      print(f"failed configuring yt-dlp {e}")

    return None

  @Slot(str, result=str)
  def getTitle(self, url: str):
    title = getSiteTitle(url)
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
  # current_dir = os.path.dirname(os.path.abspath(__file__))
  # sys.path.append(current_dir)
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
