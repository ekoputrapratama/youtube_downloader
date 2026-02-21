import os
import mimetypes

from velra.qt.core import QBuffer, QIODevice, QUrl, QByteArray
from velra.qt.webenginecore import QWebEngineUrlSchemeHandler, QWebEngineUrlRequestJob, QWebEngineUrlScheme, QWebEngineProfile

from typing import Any, cast, Optional
from velra.browser import Scheme
from velra.utils import qtutils, log

_YTDLP = QByteArray(b'ytdlp')


class YTDLPSchemeHandler(QWebEngineUrlSchemeHandler):
  schemes: dict[str, str] = dict()
  """Handle requests on velra:// and user defined scheme in QtWebEngine."""

  def install(self, profile: QWebEngineProfile, schemes: Optional[dict[Any, Any]]) -> None:
    self.schemes = schemes if schemes is not None else {}
    """Install the handler for velra:// URLs on the given profile."""

    profile.installUrlSchemeHandler(_YTDLP, self)

    if schemes is not None:
      for scheme in schemes.keys():
        if QWebEngineUrlScheme.schemeByName(scheme.encode("ascii")).name():
          profile.installUrlSchemeHandler(scheme.encode("ascii"), self)

    # if qtutils.version_check("5.11",
    #                          compiled=False) and not qtutils.version_check("5.12", compiled=False):
    #   # WORKAROUND for https://bugreports.qt.io/browse/QTBUG-63378
    #   profile.installUrlSchemeHandler(b"chrome-error", self)
    #   profile.installUrlSchemeHandler(b"chrome-extension", self)

  def registerSchemesHandler(self, schemes: dict[str, str]) -> None:
    self.schemes |= schemes

  def registerSchemeHandler(self, protocol: str, basePath: str) -> None:
    self.schemes[protocol] = basePath

  def _check_initiator(self, job: QWebEngineUrlRequestJob) -> bool:
    """Check whether the initiator of the job should be allowed.

        Only the browser itself or velra:// pages should access any of those
        URLs. The request interceptor further locks down velra://settings/set.

        Args:
            job: QWebEngineUrlRequestJob

        Return:
            True if the initiator is allowed, False if it was blocked.
        """
    try:
      initiator = job.initiator()
      request_url = job.requestUrl()
    except AttributeError:
      # Added in Qt 5.11
      return True

    # https://codereview.qt-project.org/#/c/234849/
    is_opaque = initiator == QUrl("null")
    target = request_url.scheme(), request_url.host()

    if is_opaque and not qtutils.version_check("5.12"):
      # WORKAROUND for https://bugreports.qt.io/browse/QTBUG-70421
      # When we don't register the velra:// scheme, all requests are
      # flagged as opaque.
      return True

    if (target == ("ytdlp", "testdata") and is_opaque and qtutils.version_check("5.12")):
      # Allow requests to qute://testdata, as this is needed in Qt 5.12
      # for all tests to work properly. No qute://testdata handler is
      # installed outside of tests.
      return True

    if initiator.isValid() and initiator.scheme() != "ytdlp" and initiator.scheme(
    ) not in self.schemes.keys():
      log.webview.warning("Blocking malicious request from {} to {}".format(
        initiator.toDisplayString(), request_url.toDisplayString()))
      job.fail(QWebEngineUrlRequestJob.Error.RequestDenied)
      return False

    return True

  def requestStarted(  # pyright: ignore[reportIncompatibleMethodOverride]
      self, job: Optional[QWebEngineUrlRequestJob]) -> None:
    """Handle a request for all scheme.

        This method must be reimplemented by all custom URL scheme handlers.
        The request is asynchronous and does not need to be handled right away.

        Args:
            job: QWebEngineUrlRequestJob
        """
    assert job is not None
    url: QUrl = job.requestUrl()
    print(f"current scheme: {url.scheme()}")
    try:
        mimetype, data = Scheme.data_for_custom_scheme(url)  # type: ignore[assignment]
    except Scheme.NotFoundError:
      log.webview.debug("handling custom uri scheme for : {}".format(url.toDisplayString()))
      """
      If it's throw error it can mean that user doesn't add their own handler,
      we will try to handle it ourselves here.
      """
      scheme = url.scheme()

      if self.schemes is None or scheme not in self.schemes.keys():
        job.fail(QWebEngineUrlRequestJob.Error.UrlNotFound)
        return

      base_path = self.schemes[scheme]
      path = os.path.join(base_path, url.host(), url.path()[1:])

      if not os.path.exists(path):
        job.fail(QWebEngineUrlRequestJob.Error.UrlNotFound)
        return

      try:
        with open(path, 'rb') as file:

          content_type = mimetypes.guess_type(path)
          buff = QBuffer(parent=self)
          buff.open(QIODevice.OpenModeFlag.WriteOnly)
          buff.write(file.read())
          buff.seek(0)
          buff.close()

          assert content_type[0] is not None
          job.reply(content_type[0].encode(), buff)
      except Exception as e:
        raise e
      else:
        log.webview.debug("Returning {} data".format(mimetype))

        # We can't just use the QBuffer constructor taking a QByteArray,
        # because that somehow segfaults...
        # https://www.riverbankcomputing.com/pipermail/pyqt/2016-September/038075.html
        buf = QBuffer(parent=self)
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        buf.write(data)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
        buf.seek(0)
        buf.close()
        job.reply(mimetype.encode("ascii"), buf)

      

