from zshell.plugin.base import ZShellPlugin
from zshell.plugin.tab_manager import ZShellTab
from zshell.common.utils import do_in_thread
from PyQt5 import QtCore, QtWidgets, QtGui
import win32gui
import win32con
import win32api
import win32process
import time
import os


class PuttyTab(ZShellTab):

    def __init__(self, index, tab_widget, host_info, parent=None):
        super(PuttyTab, self).__init__(index, tab_widget, parent)
        self.host_info = host_info
        self.host = host_info.get("host")
        self.user = host_info.get("user")
        self.port = host_info.get("port")
        self.password = host_info.get("password")
        self.title = self.host
        self.putty_hwnd = 0
        self._setup_layout()

    def get_right_click_menu(self):
        if not self.right_click_menu:
            self.right_click_menu = QtWidgets.QMenu()
            self.clone_action = self.right_click_menu.addAction("克隆标签")
        return self.right_click_menu

    def deal_right_click_action(self, action):
        if action == self.clone_action:
            widget = self.tab_widget.tab_create(self.__class__, self.index + 1, host_info=self.host_info)
            widget.start()

    def _setup_layout(self):
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.horizontalLayout)

    def start(self):
        self.start_putty_process()
        self.embed_putty()
        self.tab_widget.setCurrentIndex(self.index)

    def enter_action(self):
        win32gui.SetFocus(self.putty_hwnd)

    def close_action(self):
        print("close putty")
        self.process.kill()

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
        self.process.finished.connect(self.putty_finished)
        self.process.start(program, arguments)

    def putty_finished(self):
        self.deleteLater()
        # self.tab_widget.removeTab(self.index)

    def embed_putty(self):
        max_time = 500
        while self.putty_hwnd == 0 and max_time > 0:
            time.sleep(0.01)
            self.putty_hwnd = win32gui.FindWindow('PuTTY', "%s - PuTTY" % self.host)
            max_time -= 1

        if self.putty_hwnd == 0:
            return

        self.putty_window = QtGui.QWindow().fromWinId(self.putty_hwnd)
        self.putty_container = self.createWindowContainer(self.putty_window, self)
        self.set_parent_for_putty()
        self.horizontalLayout.addWidget(self.putty_container)
        win32gui.SetWindowLong(self.putty_hwnd, win32con.GWL_STYLE, win32con.WS_TABSTOP)

        self.check_security_alert()

    def reset_win_style(self):
        style = win32gui.GetWindowLong(self.putty_hwnd, win32con.GWL_STYLE)
        style = style & ~ win32con.WS_POPUP
        style = style & ~ win32con.WS_CAPTION
        style = style & ~ win32con.WS_THICKFRAME
        style = style | win32con.WS_CHILD
        win32gui.SetWindowLong(self.putty_hwnd, win32con.GWL_STYLE, style)

    def attach_thread_input(self):
        cur_thread_id = win32api.GetCurrentThreadId()
        putty_thread_id, putty_process_id = win32process.GetWindowThreadProcessId(self.putty_hwnd)
        win32process.AttachThreadInput(putty_thread_id, cur_thread_id, True)

    def set_parent_for_putty(self):
        win32gui.SetParent(self.putty_hwnd, self.putty_container.winId())
        # self.putty_container_window = QtGui.QWindow().fromWinId(self.putty_container.winId())
        # self.putty_window.setParent(self.putty_container_window)

    @do_in_thread
    def check_security_alert(self):
        time.sleep(0.5)
        hwnd = win32gui.FindWindow('#32770', 'PuTTY Security Alert')
        if not hwnd:
            return
        win32gui.SetForegroundWindow(hwnd)


class PuttyTabPlugin(ZShellPlugin):
    name = "PuttyTab"

    def __init__(self, main_win):
        super(PuttyTabPlugin, self).__init__(main_win)

    def get_tab_cls(self):
        return PuttyTab

    def close(self):
        pass
