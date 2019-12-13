from zshell.core.app import app
from zshell.core.window.main import ZShellWindow
import sys

if __name__ == "__main__":
    windows_browser = ZShellWindow()
    windows_browser.show()
    sys.exit(app.exec_())
