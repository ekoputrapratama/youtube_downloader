from velra.windows.BrowserWindow import BrowserWindow
from velra.core.Bridge import BridgeObject, Bridge
import velra.config as config

class YoutubeDownloaderWindow(BrowserWindow):
  def __init__(self, app):
    super().__init__(app=app)
    self.setWindowTitle("Youtube Downloader")


