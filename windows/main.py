from PyQt5 import QtWidgets, QtGui, QtCore
from zshell.windows.tab import ZShellTabWidget
from zshell.windows.toolbar import ZShellToolBar
from zshell.windows.menubar import ZShellMenubar


class ZShellWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(ZShellWindow, self).__init__()
        self.init_window()
        self.init_layout()
        # self.init_menubar()
        self.init_toolbar()
        self.init_tab()

    def init_window(self):
        self.setObjectName("ZShell")
        self.resize(675, 710)
        self.setWindowTitle("ZShell")
        self.setWindowIcon(QtGui.QIcon('resources/shell.ico'))
        self.centralwidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralwidget)

    def closeEvent(self, QCloseEvent):
        self.tabWidget.close()

    def init_layout(self):
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.layout_h = QtWidgets.QHBoxLayout()
        self.layout_v = QtWidgets.QVBoxLayout()
        self.gridLayout.addLayout(self.layout_h, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.layout_v, 1, 0, 1, 1)
        self.setLayout(self.gridLayout)

    def init_toolbar(self):
        self.toolbar = ZShellToolBar(self)
        self.layout_h.addWidget(self.toolbar)

    def init_tab(self):
        self.tabWidget = ZShellTabWidget(self)
        self.layout_v.addWidget(self.tabWidget)

    def init_menubar(self):
        menubar = ZShellMenubar(self)
        self.setMenuBar(menubar)
