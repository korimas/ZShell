from zshell.plugin.base import ZShellPlugin
from zshell.common.utils import do_in_thread
from PyQt5 import QtCore, QtWidgets, QtGui
from zshell.core.manage import PluginManager
import time
import os


class UploadWindow(QtWidgets.QDialog):

    def __init__(self, host_info, parent=None):
        super(UploadWindow, self).__init__(parent)
        self.host_info = host_info
        self.host = host_info.get("host")
        self.user = host_info.get("user")
        self.port = host_info.get("port")
        self.password = host_info.get("password")
        self.upload_finished = True
        self.files = None
        self.progressBar = None
        self.init_dialog()
        self.init_layout()
        self.init_ui()

    def start_upload_process(self):
        files = self.files
        if not self.files:
            self.error_msg(999)
            self.close()

        self.upload_path_input.setDisabled(True)
        self.upload_start_button.setDisabled(True)
        upload_path = self.upload_path_input.text()
        title = "上传至%s" % upload_path
        self.setWindowTitle(title)
        self.add_process_bar()

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
                "%s:%s" % (self.host, upload_path)
            ]
        )
        self.upload_finished = False
        self.upload_process.start(program, arguments)
        self.update_percent_in_thread()

    @do_in_thread
    def update_percent_in_thread(self):
        while not self.upload_finished:
            try:
                result = self.upload_process.readAllStandardOutput()
                result_str = bytes(result).decode()
                if result_str:
                    result_arry = result_str.split('|')
                    pencent = result_arry[4].strip()
                    percent = int(pencent.replace('%', ''))
                    print(percent)
                    if pencent == 100:
                        percent = 99
                    self.update_percent(percent)
            except:
                pass

            time.sleep(0.5)

    def upload_on_finished(self, exitCode, exitStatus):
        try:
            print("upload finish exitCode:%s exitStatus:%s" % (exitCode, exitStatus))
            self.upload_finished = True
            if exitCode == 0:
                self.update_percent(99)
                self.close()
            else:
                self.error_msg(exitCode)
        except:
            pass

    def closeEvent(self, QCloseEvent):
        try:
            if not self.upload_finished:
                self.upload_finished = True
                self.upload_process.kill()
            self.deleteLater()
        except:
            pass

    def update_percent(self, i):
        if self.progressBar and not self.upload_finished:
            self.progressBar.setProperty("value", i)

    def error_msg(self, exitCode):
        QtWidgets.QMessageBox.warning(self, "失败", "上传文件失败！({0})".format(exitCode))

    def init_dialog(self):
        self.setWindowIcon(self.style().standardIcon(
            QtWidgets.QStyle.SP_DialogYesButton))
        self.setFixedWidth(300)

    def init_layout(self):
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.layout_h = QtWidgets.QHBoxLayout()
        self.layout_bar = QtWidgets.QVBoxLayout()
        self.gridLayout.addLayout(self.layout_h, 0, 0, 1, -1)
        self.gridLayout.addLayout(self.layout_bar, 1, 0, 1, -1)
        self.setLayout(self.gridLayout)

    def init_ui(self):
        self.add_upload_path_input()

    def add_upload_path_input(self):
        try:
            self.upload_path_input = QtWidgets.QLineEdit()
            self.upload_path_input.setPlaceholderText("用户名")
            self.upload_path_input.returnPressed.connect(self.start_upload_process)
            self.layout_h.addWidget(self.upload_path_input)

            self.upload_start_button = QtWidgets.QToolButton()
            self.upload_start_button.setText("确定")
            self.upload_start_button.clicked.connect(self.start_upload_process)
            self.layout_h.addWidget(self.upload_start_button)
        except:
            pass

    def upload(self, files):
        try:
            self.files = files
            self.upload_path = "/home/%s" % self.user if self.user != 'root' else '/root'
            self.upload_path_input.setText(self.upload_path)
            title = "上传至%s" % self.upload_path
            self.setWindowTitle(title)
            self.show()
        except:
            pass

    def add_process_bar(self):
        try:
            self.progressBar = QtWidgets.QProgressBar(self)
            self.progressBar.setProperty("value", 0)
            self.layout_bar.addWidget(self.progressBar)
        except:
            pass


class UploadButton(QtWidgets.QPushButton):

    def __init__(self, plugin, parent=None):
        super(UploadButton, self).__init__(parent)
        self.plugin = plugin
        self.init_ui()

    def init_ui(self):
        self.setAcceptDrops(True)

    def dropEvent(self, event):
        try:
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.plugin.upload(links)

        except Exception as e:
            print(e)

    def dragEnterEvent(self, event):
        try:
            if event.mimeData().hasUrls:
                event.accept()
            else:
                event.ignore()
        except Exception as e:
            print(e)


class TestWindow(QtWidgets.QDialog):

    def __init__(self):
        super(TestWindow, self).__init__()
        self.setWindowTitle("test")


class UploadPlugin(ZShellPlugin):
    name = "Upload"

    def __init__(self, main_win):
        super(UploadPlugin, self).__init__(main_win)
        self.upload_window = None

    def start(self):
        self._setup_toolbar()

    def _setup_toolbar(self):
        self.upload_button = UploadButton(self)
        self.upload_button.setToolTip('上传至当前标签对应的主机')
        self.upload_button.setText('拖动文件至此上传')
        self.add_to_toolbar(self.upload_button)

    def upload(self, files):
        try:
            tab_manager_plugin = PluginManager().get_plugin("TabManager")
            widget = tab_manager_plugin.get_currnet_tab()
            if hasattr(widget, "host_info") and widget.host_info.get("protocol") in ['ssh', 'telnet']:
                host_info = widget.host_info
                if self.upload_window and not self.upload_window.upload_finished:
                    self.box_error("当前已有上传任务")
                    return
                self.upload_window = UploadWindow(host_info, self.main_win)
                self.upload_window.upload(files)
            else:
                self.box_info("当前标签页不支持上传")
        except:
            pass
