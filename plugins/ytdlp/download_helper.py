import json
import yt_dlp
from velra.core.Bridge import BridgeObject
from velra.qt.core import Signal, QObject, Slot, QThread
from typing import Optional, Any


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
