# from PySide2 import QtCore, QtGui, QtWidgets
from PyQt5 import QtCore, QtGui, QtWidgets
import time
import win32gui
import win32con
import os


class CustomTabWidget(QtWidgets.QTabWidget):

    def __init__(self):
        super(CustomTabWidget, self).__init__()
        self.setTabsClosable(True)

    def init(self):
        self.init_ui()
        self.init_singal()

    def init_singal(self):
        self.currentChanged.connect(self.tab_change)
        self.tabCloseRequested.connect(self.close_tab)

    def close_tab(self, index):
        if index == self.currentIndex():
            self.setCurrentIndex(index - 1)
        self.widget(index).deleteLater()
        self.removeTab(index)

    def init_ui(self):
        self.setUpdatesEnabled(True)
        self.insertTab(0, PuttyTab(), "New tab")
        self.insertTab(1, CreateTab(), '')

        self.build_button = QtWidgets.QToolButton()
        self.label = QtWidgets.QLabel()
        self.label.setText('+ ')
        self.tabBar().setTabButton(1, QtWidgets.QTabBar.RightSide, self.label)

    def tab_change(self, index):
        if index == self.count() - 1:
            self.create_new_tab(index)

        tab_widget = self.widget(index)

        if tab_widget is None:
            return self.close()
        if tab_widget.putty_hwnd:
            win32gui.SetFocus(tab_widget.putty_hwnd)

    def create_new_tab(self, index=None):
        if not index:
            index = self.count() - 1

        if index == 0:
            tab_name = "New tab"
        else:
            tab_name = "New tab%d" % index
        self.insertTab(index, PuttyTab(), tab_name)
        self.setCurrentIndex(index)

    def create_new_putty(self, host, index=None):

        if not self.currentWidget().putty:
            self.currentWidget().add_putty(host)
            self.setTabText(self.currentIndex(), host)
            return

        if not index:
            index = self.count() - 1

        tab_widget = PuttyTab()
        self.insertTab(index, tab_widget, host)
        self.setCurrentIndex(index)
        tab_widget.add_putty(host)


class CreateTab(QtWidgets.QWidget):

    def __init__(self):
        super(CreateTab, self).__init__()
        self.setObjectName("new_tab")
        self.setEnabled(False)


class PuttyTab(QtWidgets.QWidget):

    def __init__(self):
        super(PuttyTab, self).__init__()
        self.putty_hwnd = 0
        self.putty_window = None
        self.putty_container = None
        self.init_layout()
        self.putty = False

    def init_layout(self):
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.horizontalLayout)
        self.horizontalLayout.setObjectName("horizontalLayout")

    def add_putty(self, host, port="22", user=None, password=None):
        self.putty = True
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.start_putty_process()
        self.embed_putty()

    def start_putty_process(self):
        program = "putty.exe"
        arguments = [
            # "-load",
            # "Default Settings",
            "-ssh"
        ]
        if self.user:
            arguments.extend(["-l", self.user])

        if self.password:
            arguments.extend(['-pw', self.password])

        arguments.extend(
            [
                self.host,
                "-P",
                self.port,
                "-loghost",
                "ZShell"
            ]
        )

        process = QtCore.QProcess(self)
        process.setProgram(program)
        process.setArguments(arguments)
        process.start()

    def embed_putty(self):
        max_time = 5000
        while self.putty_hwnd == 0 and max_time > 0:
            time.sleep(0.01)
            self.putty_hwnd = win32gui.FindWindow('PuTTY', "ZShell - PuTTY")
            max_time -= 1

        if max_time <= 0:
            return

        self.putty_window = QtGui.QWindow().fromWinId(self.putty_hwnd)
        self.putty_container = self.createWindowContainer(self.putty_window, parent=self)
        self.horizontalLayout.addWidget(self.putty_container)

        win32gui.SetWindowLong(self.putty_hwnd, win32con.GWL_STYLE, win32con.WS_POPUP)

        style = win32gui.GetWindowLong(self.putty_container.winId(), win32con.GWL_STYLE)
        win32gui.SetWindowLong(self.putty_container.winId(), win32con.GWL_STYLE, style)


class PuttyConsole(QtWidgets.QWidget):

    def __init__(self, host, port="22", user=None, password=None):
        super(PuttyConsole, self).__init__()
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.putty_hwnd = 0
        self.putty_window = None
        self.putty_container = None
        self.setObjectName("putty_console")
        self.init_layout()
        self.init_putty_console()
        self.putty = True

    def init_layout(self):
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.horizontalLayout)
        self.horizontalLayout.setObjectName("horizontalLayout")

    def init_putty_console(self):
        self.start_putty_process()
        self.embed_putty()

    def start_putty_process(self):
        program = "%s\putty.exe" % os.path.abspath('.')
        arguments = [
            "-load",
            "Default Settings",
            "-ssh"
        ]
        if self.user:
            arguments.extend(["-l", self.user])

        if self.password:
            arguments.extend(['-pw', self.password])

        arguments.extend(
            [
                self.host,
                "-P",
                self.port,
                "-loghost",
                "ZShell"
            ]
        )

        process = QtCore.QProcess(self)
        process.setProgram(program)
        process.setArguments(arguments)
        process.start()

    def embed_putty(self):
        max_time = 5000
        while self.putty_hwnd == 0 and max_time > 0:
            time.sleep(0.01)
            self.putty_hwnd = win32gui.FindWindow('PuTTY', "ZShell - PuTTY")
            max_time -= 1

        if max_time <= 0:
            return

        self.putty_window = QtGui.QWindow().fromWinId(self.putty_hwnd)
        self.putty_container = self.createWindowContainer(self.putty_window, parent=self)
        self.horizontalLayout.addWidget(self.putty_container)

        win32gui.SetWindowLong(self.putty_hwnd, win32con.GWL_STYLE, win32con.WS_POPUP)

        style = win32gui.GetWindowLong(self.putty_container.winId(), win32con.GWL_STYLE)
        win32gui.SetWindowLong(self.putty_container.winId(), win32con.GWL_STYLE, style)
