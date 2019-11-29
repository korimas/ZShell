from zshell.mainWin import ZshellWindow
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    zshell_app = QApplication(sys.argv)
    windows_browser = ZshellWindow()
    windows_browser.show()
    windows_browser.init()
    sys.exit(zshell_app.exec_())
