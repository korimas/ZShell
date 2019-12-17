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
import re


class VncTab(ZShellTab):
    signal = QtCore.pyqtSignal()

    def __init__(self, index, tab_widget, host_info, parent=None):
        super(VncTab, self).__init__(index, tab_widget, parent)
        self.host_info = host_info
        self.host = host_info.get("host")
        self.port = host_info.get("port")
        self.title = "{0}:{1}".format(self.host, self.port)
        self.vnc_hwnd = 0
        self.process_finished = False
        self.signal.connect(self.signal_handler)
        self._setup_layout()

    def signal_handler(self):
        try:
            self.embed_vnc()
            self.tab_widget.setCurrentIndex(self.index)
        except:
            import traceback
            traceback.print_exc()

    def find_vnc_hwnd(self, hwnd, windows):
        win_title = win32gui.GetWindowText(hwnd)
        win_class = win32gui.GetClassName(hwnd)
        if win_class == "vwr::CDesktopWin" and self.title in win_title:
            self.vnc_hwnd = hwnd
            self.signal.emit()

    @do_in_thread
    def find_vnc_real_win(self):
        max_time = 300
        while self.vnc_hwnd == 0 and max_time > 0 and not self.process_finished:
            try:
                windows = {}
                win32gui.EnumWindows(self.find_vnc_hwnd, windows)
                time.sleep(0.5)
                max_time -= 1
            except:
                import traceback
                traceback.print_exc()

        if self.vnc_hwnd:
            print("find vnc already {0}".format(self.vnc_hwnd))

    def _setup_layout(self):
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.horizontalLayout)

    def start(self):
        self.start_vnc_process()
        self.find_vnc_real_win()

    def enter_action(self):
        win32gui.SetFocus(self.vnc_hwnd)

    def close_action(self):
        print("close vnc")
        self.process.kill()

    def start_vnc_process(self):
        program = "%s/resources/vnc.exe" % os.path.abspath('.')
        arguments = ['{0}:{1}'.format(self.host, self.port),
                     '-AutoReconnect',
                     '-EnableToolbar=0',
                     # '-Scaling=AspectFit',
                     ]

        self.process = QtCore.QProcess(self)
        self.process.finished.connect(self.vnc_finished)
        self.process.start(program, arguments)

    def vnc_finished(self, exitCode, exitStatus):
        print("vnc exit code:{0}, status:{1}".format(exitCode, exitStatus))
        self.process_finished = True
        # self.deleteLater()

    def embed_vnc(self):
        if self.vnc_hwnd == 0:
            return
        self.vnc_window = QtGui.QWindow().fromWinId(self.vnc_hwnd)
        self.vnc_container = self.createWindowContainer(self.vnc_window, self)
        self.set_parent_for_vnc()
        self.horizontalLayout.addWidget(self.vnc_container)
        win32gui.SetWindowLong(self.vnc_hwnd, win32con.GWL_STYLE, win32con.WS_POPUP)

    def attach_thread_input(self):
        cur_thread_id = win32api.GetCurrentThreadId()
        vnc_thread_id, vnc_process_id = win32process.GetWindowThreadProcessId(self.vnc_hwnd)
        win32process.AttachThreadInput(vnc_thread_id, cur_thread_id, True)

    def set_parent_for_vnc(self):
        win32gui.SetParent(self.vnc_hwnd, self.vnc_container.winId())


class VncTabPlugin(ZShellPlugin):
    name = "VncTab"

    def __init__(self, main_win):
        super(VncTabPlugin, self).__init__(main_win)

    def get_tab_cls(self):
        return VncTab

    def close(self):
        pass
