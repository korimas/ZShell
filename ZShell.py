from PyQt5.QtWidgets import QApplication
from zshell.windows.main import ZShellWindow
import sys

if __name__ == "__main__":
    zshell_app = QApplication(sys.argv)
    windows_browser = ZShellWindow()
    windows_browser.show()
    sys.exit(zshell_app.exec_())
