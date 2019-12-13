from PyQt5 import QtWidgets, QtGui, QtCore


class ZShellPlugin(object):
    name = None

    def __init__(self, main_win):
        self.main_win = main_win

    def start(self):
        pass

    def add_to_toolbar(self, widget):
        self.main_win.add_to_toolbar(widget)

    def add_to_body(self, widget):
        self.main_win.add_to_body(widget)

    def box_info(self, message):
        QtWidgets.QMessageBox.information(self.main_win, "info", message)

    def box_error(self, message):
        QtWidgets.QMessageBox.warning(self.main_win, "warning", message)

    def close(self):
        pass
