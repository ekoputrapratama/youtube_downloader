import os
import sys
import signal
import json
import argparse

from pathlib import Path
from typing import Optional
from PySide6.QtCore import Qt, QTimer, QUrl
from velra.qt.webenginecore import QWebEngineProfile, QWebEngineUrlScheme
from velra.Application import VApplication
from velra.velra import get_argparser
from velra.misc import earlyinit
from velra.browser.Scheme import add_scheme_handler
from velra.utils import standarddir, utils, resources
from velra.config import config

from youtube_downloader.YoutubeDownloaderWindow import YoutubeDownloaderWindow
# from youtube_downloader.utils import getArgsParser

app: Optional[VApplication] = None


def sigint_handler(*args):
  global app
  """Handler for the SIGINT signal."""
  if app is not None:
    app.quit()


def _unpack_json_args(args):
  """Restore arguments from --json-args after a restart.

    When restarting, we serialize the argparse namespace into json, and
    construct a "fake" argparse.Namespace here based on the data loaded
    from json.
    """
  new_args = vars(args)
  data = json.loads(args.json_args)
  new_args.update(data)
  return argparse.Namespace(**new_args)


def main():
  signal.signal(signal.SIGINT, sigint_handler)
  global app
  # add this to fix error running in wsl
  os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
  """
  This attribute need to be set before QCoreApplication created,
  it will still show warning because QWebEngineView::initialize
  call this at the end.
  """
  # MyApp.setAttribute(Qt.AA_ShareOpenGLContexts, True)
  parser = get_argparser()
  parser.add_argument('--dev', help="Turn on development mode.", action='store_true')
  argv = sys.argv[1:]
  args = parser.parse_args(argv)
  if args.json_args is not None:
    args = _unpack_json_args(args)

  earlyinit.early_init(args)
  standarddir.init(args)
  config.init(args, "ytdlp")

  app = YoutubeDownloaderApp(args)
  app.setOrganizationName("ytdlp")
  app.setApplicationName("ytdlp")

  # Python cannot handle signals while the Qt event loop is running.
  # so we need to use QTimer to let the interpreter run from time to time.
  # https://stackoverflow.com/questions/4938723/what-is-the-correct-way-to-make-my-pyqt-application-quit-when-killed-from-the-co
  timer = QTimer()
  timer.start(500)  # You may change this if you wish.
  timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.
  sys.exit(app.exec())


def resource_path(relative_path):
  """ Get absolute path to resource, works for dev and for PyInstaller """
  base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
  return os.path.join(base_path, relative_path)


class YoutubeDownloaderApp(VApplication):
  def __init__(self, args):
    if args.dev:
      plugin_dir = os.path.join(os.path.dirname(__file__), '..', "plugins")
    else:
      if utils.isLinux:
        plugin_dir = resource_path(os.path.join("plugins"))
      else:
        plugin_dir = resource_path(os.path.join("..", "plugins"))

    self.registerUriScheme("ytdlp", os.path.dirname(__file__))
    self.registerUriScheme("plugins", plugin_dir)

    super().__init__(args, "ytdlp")
    print(f"registering plugin directory {plugin_dir}")
    self.registerPluginDir(plugin_dir)

    self.window = YoutubeDownloaderWindow(self)
    # self.window.webview.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)

    print("load downloader url")
    if args.dev:
      self.window.loadUrl(args.url[0])
    else:
      self.window.loadUrl('ytdlp://app/index.html')

    self.window.show()

  @add_scheme_handler("ytdlp")
  def handleYtdlpScheme(url: QUrl):  # type: ignore
    print("handling ytdlp scheme request with host={}".format(url.host()))
    host = url.host()

    if host in ["app"]:
      path = os.path.join(host, url.path()[1:])
      abs_path = Path(os.path.dirname(__file__)).parent
      # base_path = os.path.join(abs_path.absolute)
      path = os.path.join(abs_path, path)

      mimetype = utils.getContentType(path)
      data = resources.readResourceFile(path, binary=True)

    return mimetype, data  # type: ignore
