from zshell.core.app import app, main_win
from zshell.plugin.manager import enable_plugins
import sys
import traceback
from PyQt5 import QtWidgets


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    # with open("resources/crash.log", "a+") as file:
    #     file.write(tb)
    QtWidgets.QMessageBox.warning(main_win, "Traceback", tb)


if __name__ == "__main__":
    main_win.start_plugins(enable_plugins)
    main_win.show()
    sys.excepthook = excepthook
    sys.exit(app.exec_())
