# from PySide2 import QtCore, QtWidgets
from PyQt5 import QtCore, QtWidgets
from zshell.tab import CustomTabWidget


class ZshellWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(ZshellWindow, self).__init__()
        self.setObjectName("ZShell")
        self.resize(675, 810)
        self.setWindowTitle(QtWidgets.QApplication.translate("ZShell", "ZShell", None, -1))
        self.setWindowIcon()
        self.centralwidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralwidget)
        self.init_layout()
        self.init_menubar()
        self.init_toolbar()
        self.init_tab()

    def init_toolbar(self):
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName("lineEdit")
        self.toobar_layout_h.addWidget(self.lineEdit)
        self.lineEdit.setPlaceholderText(QtWidgets.QApplication.translate("ZShell", "快速访问", None, -1))
        self.lineEdit.returnPressed.connect(self.lineEdit_function)

    def lineEdit_function(self):
        self.tabWidget.create_new_putty(self.lineEdit.text())

    def lazy_init(self):
        # TODO: do in thread
        pass

    def init_layout(self):
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.toobar_layout_h = QtWidgets.QHBoxLayout()
        self.tab_Layout_v = QtWidgets.QVBoxLayout()
        self.gridLayout.addLayout(self.toobar_layout_h, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.tab_Layout_v, 1, 0, 1, 1)

        self.setLayout(self.gridLayout)

    def init_tab(self):
        self.tabWidget = CustomTabWidget()
        self.tab_Layout_v.addWidget(self.tabWidget)

    def init_menubar(self):
        menubar = QtWidgets.QMenuBar(self)
        menubar.setGeometry(QtCore.QRect(0, 0, 675, 22))
        menubar.setObjectName("menubar")
        menuZShell = QtWidgets.QMenu(menubar)
        menuZShell.setObjectName("menuZShell")
        menuEdit = QtWidgets.QMenu(menubar)
        menuEdit.setObjectName("menuEdit")
        menuHelp = QtWidgets.QMenu(menubar)
        menuHelp.setObjectName("menuHelp")
        self.setMenuBar(menubar)
        statusbar = QtWidgets.QStatusBar(self)
        statusbar.setObjectName("statusbar")
        self.setStatusBar(statusbar)
        menubar.addAction(menuZShell.menuAction())
        menubar.addAction(menuEdit.menuAction())
        menubar.addAction(menuHelp.menuAction())
        menuZShell.setTitle(QtWidgets.QApplication.translate("ZShell", "File", None, -1))
        menuEdit.setTitle(QtWidgets.QApplication.translate("ZShell", "Edit", None, -1))
        menuHelp.setTitle(QtWidgets.QApplication.translate("ZShell", "Help", None, -1))

    def init(self):
        self.tabWidget.init()
