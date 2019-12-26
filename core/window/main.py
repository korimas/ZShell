from PyQt5 import QtWidgets, QtGui, QtCore
from zshell.core.manage import PluginManager
from zshell.core.window.toolbar import ZShellToolBar


class ZShellWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(ZShellWindow, self).__init__()
        self._setup_win_base()
        self._setup_layout()
        self._setup_toolbar()
        # self._setup_plugins()

    def _setup_win_base(self):
        self.setObjectName("ZShell")
        self.setWindowTitle("ZShell")
        self.setWindowIcon(QtGui.QIcon('resources/shell.ico'))
        self.resize(675, 710)

    def _setup_layout(self):
        self.centralwidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralwidget)
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.layout_header = QtWidgets.QHBoxLayout()
        self.layout_header.setContentsMargins(2, 8, 0, 0)
        self.layout_body = QtWidgets.QVBoxLayout()
        self.gridLayout.addLayout(self.layout_header, 0, 0, 1, -1)
        self.gridLayout.addLayout(self.layout_body, 1, 0, 1, -1)
        self.setLayout(self.gridLayout)

    def start_plugins(self, plugins):
        plugin_manager = PluginManager()
        plugin_manager.set_main_win(self)
        plugin_manager.start_plugins(plugins)

    def _setup_toolbar(self):
        self.toolbar = ZShellToolBar(self)
        self.layout_header.addWidget(self.toolbar)

    def add_to_toolbar(self, widget):
        self.toolbar.addWidget(widget)

    def add_to_body(self, widget):
        self.layout_body.addWidget(widget)

    def closeEvent(self, event):
        PluginManager().close()

    def event(self, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            tab_plugin = PluginManager().get_plugin("TabManager")
            if tab_plugin:
                tab_plugin.enter_current_tab()
        return True