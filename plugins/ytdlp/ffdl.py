import ffmpeg_downloader as ffdl
from velra.core.Bridge import BridgeObject
from velra.qt.core import Signal, QObject, Slot, QThread, QStandardPaths
from typing import Optional, Any
from .utils import log


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
    log.debug(f"latest version {latestBuild}")

    if not ffdl.installed() or shouldUpgrade:
      dstpaths = ffdl._backend.download(latestBuild, dst=cacheDir, no_cache_dir=True, proxy=None, retries=None, timeout=None, progress=None)
      log.debug(f"destination path {dstpaths}")
      ffdl._backend.install(*dstpaths, progress=None)

    log.debug(f"ffmpeg path {ffdl.ffmpeg_path}")
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
