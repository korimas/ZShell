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

    def protocol_change(self, index):
        if self.protocol_box.currentText() == 'vnc':
            self.user_line_edit.hide()
            self.pass_line_edit.hide()
            self.port_line_edit.setPlaceholderText("端口")
        else:
            self.user_line_edit.show()
            self.pass_line_edit.show()
            self.port_line_edit.setPlaceholderText("端口(22)")

    def _setup_toolbar(self):
        self.protocol_box = QtWidgets.QComboBox()
        self.protocol_box.setFixedWidth(60)
        self.protocol_box.addItem('ssh')
        self.protocol_box.addItem('telnet')
        self.protocol_box.addItem('vnc')
        self.protocol_box.currentIndexChanged.connect(self.protocol_change)
        self.add_to_toolbar(self.protocol_box)

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
        self.save_session_button.setPopupMode(self.save_session_button.MenuButtonPopup)
        self.save_session_button.setFixedHeight(23)
        self.save_session_button.setText("连接")
        self.add_to_toolbar(self.save_session_button)
        self.save_session_button.clicked.connect(self.connect_host)

        menu_style = '''
        QMenu::item {
            padding-left:5px;
            width: 44px;
        }
        QMenu::item:selected {
            background: lightBlue;
        }
        '''
        self.save_button_menu = QtWidgets.QMenu()
        self.save_button_menu.setStyleSheet(menu_style)
        self.save_session_button.setMenu(self.save_button_menu)
        self.save_session_action = QtWidgets.QAction("保存", self.save_button_menu)
        self.save_button_menu.addAction(self.save_session_action)
        self.save_session_action.triggered.connect(self.save_to_session_manager)

    def get_session_manager_plugin(self):
        if not self.session_manager_plugin:
            self.session_manager_plugin = PluginManager().get_plugin("SessionManager")

    def clear_line_edit(self):
        self.host_line_edit.clear()
        self.port_line_edit.clear()
        self.user_line_edit.clear()
        self.pass_line_edit.clear()

    def get_host_info_from_ui(self):
        host = self.host_line_edit.text()
        port = self.port_line_edit.text() or '22'
        user = self.user_line_edit.text() or None
        password = self.pass_line_edit.text() or None
        protocol = self.protocol_box.currentText()
        self.clear_line_edit()
        return {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "protocol": protocol
        }

    def check_host_info(self, host_info):
        protocol = host_info.get('protocol')
        for key, value in host_info.items():
            if not value:
                if protocol == "vnc" and key in ['user', 'password']:
                    continue
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
