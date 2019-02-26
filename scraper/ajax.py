from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtWebKit import *

app = QApplication([])
webview = QWebView()
loop = QEventLoop()
webview.loadFinished.connect(loop.quit)

def render_ajax(url):
    print 'Rendering: %s' % url
    webview.load(QUrl(url))
    loop.exec_()
    return webview.page().mainFrame().toHtml()
