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
        self.tab_menu = None
        self.tab_actions = []
        self.init_ui()
        self.init_singal()

    def set_right_corner_button(self):
        self.list_tab_button = QtWidgets.QToolButton(self)
        self.list_tab_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.list_tab_button.setIcon(self.style().standardIcon(
            QtWidgets.QStyle.SP_DialogYesButton))
        self.setCornerWidget(self.list_tab_button)
        self.init_list_tab_menu()

    def init_list_tab_menu(self):
        self.tab_menu = QtWidgets.QMenu()
        self.list_tab_button.setMenu(self.tab_menu)

    def add_tab_action(self, index, tab_title):
        tab_action = QtWidgets.QAction(tab_title, self.tab_menu)
        tab_action.triggered.connect(lambda: self.jump_to_tab(tab_action))

        if index >= len(self.tab_actions):
            self.tab_menu.addAction(tab_action)
            self.tab_actions.append(tab_action)
        else:
            before_action = self.tab_actions[index]
            self.tab_menu.insertAction(before_action, tab_action)
            self.tab_actions.insert(index, tab_action)

    def closeEvent(self, QCloseEvent):
        for i in range(0, self.count()):
            widget = self.widget(i)
            if widget:
                widget.close_putty()

    def remove_tab_action(self, index):
        action = self.tab_actions[index]
        self.tab_menu.removeAction(action)
        self.tab_actions.remove(action)

    def jump_to_tab(self, tab_action):
        try:
            tab_title = tab_action.text()
            index = int(tab_title.split('-')[0]) - 1
            if index < self.count():
                self.setCurrentIndex(index)
        except:
            traceback.print_exc()

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
            self.remove_tab_action(index)
            self.flush_index_id()
        except:
            traceback.print_exc()

    def tab_change(self, index):
        try:
            tab_widget = self.widget(index)
            if tab_widget:
                if tab_widget.putty_hwnd and tab_widget.process:
                    # TODO(zpzhou): check process is alive
                    win32gui.SetFocus(tab_widget.putty_hwnd)
        except:
            traceback.print_exc()

    def ssh_tab_create(self, host, port=None, user=None, password=None, index=None):
        try:
            if not index:
                index = self.count()
            tab_name = "%s-%s" % (self.index_num, host)
            if not port:
                port = '22'
            tab_widget = PuttyTab(self)
            tab_widget.add_putty(host, port, user, password)
            self.insertTab(index, tab_widget, tab_name)
            self.index_num += 1
            self.setCurrentIndex(index)
            self.add_tab_action(index, tab_name)
            self.flush_index_id()
        except:
            traceback.print_exc()

    def flush_index_id(self):
        for i in range(0, self.count()):
            title = "%s-%s" % (str(i + 1), self.widget(i).host)
            action = self.tab_actions[i]
            action.setText(title)
            # action.setToolTip(title)
            self.setTabText(i, title)

    def upload_files(self, files):
        if self.currentWidget():
            self.currentWidget().upload_files(files)


class PuttyTab(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(PuttyTab, self).__init__(parent)
        self.putty_hwnd = 0
        self.putty_window = None
        self.putty_container = None
        self.putty = False
        self.process = None
        self.upload_process = None
        self.upload_win = None
        self.upload_finished = True
        self.init_layout()

    def close_putty(self):
        if self.process:
            self.process.kill()

    def closeEvent(self, QCloseEvent):
        self.close_putty()

    def init_layout(self):
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.horizontalLayout)

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
        self.process.finished.connect(self.putty_on_finished)
        self.process.start(program, arguments)

    def putty_on_finished(self, exitCode, exitStatus):
        print("putty finish")
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
        self.putty_container = self.createWindowContainer(self.putty_window, self)
        win32gui.SetParent(self.putty_hwnd, self.putty_container.winId())
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

    def upload_files(self, files):
        home_dir = "/home/%s" % self.user if self.user != 'root' else '/root'
        title = "上传至%s" % home_dir
        self.upload_process = QtCore.QProcess(self)
        self.upload_process.finished.connect(self.upload_on_finished)
        program = "%s/resources/pscp.exe" % os.path.abspath('.')
        arguments = [
            "-sftp"
        ]
        if self.user:
            arguments.extend(["-l", self.user])

        if self.password:
            arguments.extend(['-pw', self.password])

        arguments.extend(
            [
                "-P",
                self.port,
                files[0],
                "%s:%s" % (self.host, home_dir)
            ]
        )
        # win32gui.SetFocus(self.putty_hwnd)
        self.upload_finished = False
        self.upload_process.start(program, arguments)
        self.show_upload_win(title)

    def show_upload_win(self, title):

        if not self.upload_win:
            self.upload_win = UploadWin(self)
            self.upload_win.setWindowTitle(title)

        self.upload_win.show()
        self.upload_win.update_percent(0)
        self.update_percent()

    @do_in_thread
    def update_percent(self):
        while not self.upload_finished:
            try:
                result = self.upload_process.readAllStandardOutput()
                result_str = bytes(result).decode()
                if result_str:
                    result_arry = result_str.split('|')
                    pencent = result_arry[4].strip()
                    self.upload_win.update_percent(int(pencent.replace('%', '')))
            except:
                pass

            time.sleep(1)

    def upload_on_finished(self, exitCode, exitStatus):
        print("upload finish exitCode:%s exitStatus:%s" % (exitCode, exitStatus))
        self.upload_finished = True
        if exitCode == 0:
            self.upload_win.update_percent(100)
            self.upload_win.close()
        else:
            self.upload_win.error_msg(exitCode)


class UploadWin(QtWidgets.QDialog):

    def __init__(self, PuttyTab, parent=None):
        super(UploadWin, self).__init__(parent)
        self.PuttyTab = PuttyTab
        self.init_dialog()
        self.init_layout()
        self.init_ui()

    def closeEvent(self, QCloseEvent):
        if not self.PuttyTab.upload_finished:
            print("try to terminate pscp")
            self.PuttyTab.upload_finished = True
            self.PuttyTab.upload_process.kill()

    def update_percent(self, i):
        self.progressBar.setProperty("value", i)

    def error_msg(self, exitCode):
        QtWidgets.QMessageBox.warning(self, "失败", "上传文件失败！")

    def init_dialog(self):
        self.setWindowIcon(self.style().standardIcon(
            QtWidgets.QStyle.SP_DialogYesButton))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    def init_layout(self):
        self.layout_v = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout_v)

    def init_ui(self):
        self.add_process_bar()

    def add_process_bar(self):
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setFixedWidth(300)
        self.layout_v.addWidget(self.progressBar)
