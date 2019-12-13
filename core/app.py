from PyQt5.QtWidgets import QApplication
from zshell.core.window.main import ZShellWindow
import sys

app = QApplication(sys.argv)
main_win = ZShellWindow()