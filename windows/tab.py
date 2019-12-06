from PyQt5 import QtCore, QtGui, QtWidgets
import time
import win32gui
import win32con
import os
import traceback
from zshell.common.utils import do_in_thread


class ZShellTabWidget(QtWidgets.QTabWidget):

    def __init__(self, parent=None):
        super(ZShellTabWidget, self).__init__(parent)
        self.index_num = 1
        self.init_ui()
        self.init_singal()

    def set_right_corner_button(self):
        self.close_button = QtWidgets.QToolButton(self)
        self.close_button.setIcon(self.style().standardIcon(
            QtWidgets.QStyle.SP_DialogYesButton))
        self.setCornerWidget(self.close_button)

    def init_ui(self):
        self.setTabsClosable(True)
        self.setUpdatesEnabled(True)
        self.set_right_corner_button()
        self.tabBar().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tabBar().customContextMenuRequested.connect(self.open_menu)

        # self.insertTab(0, PuttyTab(), "New tab")

    def open_menu(self, position):
        try:
            menu = QtWidgets.QMenu()
            clone_action = menu.addAction("克隆标签")
            action = menu.exec_(self.tabBar().mapToGlobal(position))
            if action == clone_action:
                clone_index = self.tabBar().tabAt(position)
                widget = self.widget(clone_index)
                self.ssh_tab_create(widget.host, widget.port, widget.user, widget.password, clone_index + 1)
        except:
            traceback.print_exc()

    def init_singal(self):
        self.currentChanged.connect(self.tab_change)
        self.tabCloseRequested.connect(self.tab_close)

    def tab_close(self, index):
        try:
            if index == self.currentIndex() and index > 1:
                self.setCurrentIndex(index - 1)
            self.widget(index).close_putty()
            self.widget(index).deleteLater()
            self.removeTab(index)
            self.flush_index_id()
        except:
            traceback.print_exc()

    def tab_change(self, index):
        try:
            tab_widget = self.widget(index)
            if tab_widget and tab_widget.putty_hwnd and tab_widget.process:
                # print(tab_widget.process.exitStatus())
                # print(tab_widget.process.state())
                win32gui.SetFocus(tab_widget.putty_hwnd)
        except:
            traceback.print_exc()

    def ssh_tab_create(self, host, port=None, user=None, password=None, index=None):
        if not index:
            index = self.count()
        tab_name = "%s-%s" % (self.index_num, host)
        if not port:
            port = '22'
        tab_widget = PuttyTab()
        tab_widget.add_putty(host, port, user, password)
        self.insertTab(index, tab_widget, tab_name)
        self.index_num += 1
        self.setCurrentIndex(index)
        self.flush_index_id()

    def flush_index_id(self):
        for i in range(0, self.count()):
            title = "%s-%s" % (str(i + 1), self.widget(i).host)
            self.setTabText(i, title)


class PuttyTab(QtWidgets.QWidget):

    def __init__(self):
        super(PuttyTab, self).__init__()
        self.putty_hwnd = 0
        self.putty_window = None
        self.putty_container = None
        self.putty = False
        self.process = None
        self.init_layout()

    def close_putty(self):
        if self.process:
            self.process.terminate()

    def init_layout(self):
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
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
        program = "%s/resources/putty.exe" % os.path.abspath('.')
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
                self.host
            ]
        )
        self.process = QtCore.QProcess(self)
        self.process.finished.connect(self.process_finish)
        self.process.start(program, arguments)

    def process_finish(self):
        self.deleteLater()

    def embed_putty(self):
        max_time = 500
        while self.putty_hwnd == 0 and max_time > 0:
            time.sleep(0.01)
            self.putty_hwnd = win32gui.FindWindow('PuTTY', "%s - PuTTY" % self.host)
            max_time -= 1

        if self.putty_hwnd == 0:
            return

        self.putty_window = QtGui.QWindow().fromWinId(self.putty_hwnd)
        self.putty_container = self.createWindowContainer(self.putty_window)
        self.horizontalLayout.addWidget(self.putty_container)
        win32gui.SetWindowLong(self.putty_hwnd, win32con.GWL_STYLE, win32con.WS_TABSTOP)
        win32gui.SetWindowLong(self.putty_container.winId(), win32con.GWL_STYLE,
                               win32gui.GetWindowLong(self.putty_container.winId(), win32con.GWL_STYLE)
                               )
        self.check_security_alert()

    @do_in_thread
    def check_security_alert(self):
        time.sleep(0.5)
        hwnd = win32gui.FindWindow('#32770', 'PuTTY Security Alert')
        if not hwnd:
            return
        win32gui.SetForegroundWindow(hwnd)
