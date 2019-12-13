from zshell.plugin.base import ZShellPlugin
from zshell.core.manage import PluginManager
from zshell.common.utils import do_in_thread
from PyQt5 import QtCore, QtWidgets
import json


class QuickConnectPlugin(ZShellPlugin):
    name = "QuickConnect"

    def __init__(self, main_win):
        super(QuickConnectPlugin, self).__init__(main_win)
        self.session_manager_plugin = None

    def start(self):
        self._setup_toolbar()

    def _setup_toolbar(self):
        # self.label = QtWidgets.QLabel()
        # self.label.setText("  快速登录:")
        # self.add_to_toolbar(self.label)

        self.host_line_edit = QtWidgets.QLineEdit()
        self.add_to_toolbar(self.host_line_edit)
        self.host_line_edit.setPlaceholderText("主机")
        self.host_line_edit.setFixedWidth(100)
        self.host_line_edit.returnPressed.connect(self.connect_host)

        self.user_line_edit = QtWidgets.QLineEdit()
        self.add_to_toolbar(self.user_line_edit)
        self.user_line_edit.setPlaceholderText("用户名")
        self.user_line_edit.setFixedWidth(100)
        self.user_line_edit.returnPressed.connect(self.connect_host)

        self.pass_line_edit = QtWidgets.QLineEdit()
        self.add_to_toolbar(self.pass_line_edit)
        self.pass_line_edit.setPlaceholderText("密码")
        self.pass_line_edit.setFixedWidth(100)
        self.pass_line_edit.returnPressed.connect(self.connect_host)

        self.port_line_edit = QtWidgets.QLineEdit()
        self.add_to_toolbar(self.port_line_edit)
        self.port_line_edit.setPlaceholderText("端口(22)")
        self.port_line_edit.setFixedWidth(100)
        self.port_line_edit.returnPressed.connect(self.connect_host)

        self.save_session_button = QtWidgets.QToolButton()
        self.save_session_button.setToolTip('保存登录信息')
        self.save_session_button.setIcon(self.save_session_button.style().standardIcon(
            QtWidgets.QStyle.SP_DialogSaveButton))
        self.add_to_toolbar(self.save_session_button)
        self.save_session_button.clicked.connect(self.save_to_session_manager)

    def get_session_manager_plugin(self):
        if not self.session_manager_plugin:
            self.session_manager_plugin = PluginManager().get_plugin("SessionManager")

    def get_host_info_from_ui(self):
        host = self.host_line_edit.text()
        port = self.port_line_edit.text() or '22'
        user = self.user_line_edit.text() or None
        password = self.pass_line_edit.text() or None
        return {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
        }

    def check_host_info(self, host_info):
        for key, value in host_info.items():
            if not value:
                self.box_info("请输入完整的主机信息")
                return False
        return True

    def save_to_session_manager(self):
        host_info = self.get_host_info_from_ui()
        if not self.check_host_info(host_info):
            return
        self.get_session_manager_plugin()
        self.session_manager_plugin.add_host(host_info)

    def connect_host(self):
        host_info = self.get_host_info_from_ui()
        if not self.check_host_info(host_info):
            return
        self.get_session_manager_plugin()
        self.session_manager_plugin.connect_host(host_info)
