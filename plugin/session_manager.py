from zshell.plugin.base import ZShellPlugin
from zshell.core.manage import PluginManager
from PyQt5 import QtCore, QtWidgets, QtGui
from zshell.common.security import decrypt, encrypt
import json
import shutil
import os
import subprocess


class SessionManagerMenuAction(QtWidgets.QAction):

    def __init__(self, plugin, host_key, menu):
        super(SessionManagerMenuAction, self).__init__(host_key, menu)
        self.host_key = host_key
        self.plugin = plugin
        self.triggered.connect(self.connect_host)

    def connect_host(self):
        self.plugin.connect_host_by_key(self.host_key)


class SessionManagerToolButton(QtWidgets.QToolButton):

    def __init__(self, plugin):
        super(SessionManagerToolButton, self).__init__()
        self.plugin = plugin
        self._setup_button()

    def _setup_button(self):
        self.setToolTip('会话管理')
        self.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogYesButton))
        # self.setPopupMode(self.MenuButtonPopup)
        self.clicked.connect(self.plugin.show_session_manager)


class SessionManagerMenu(QtWidgets.QMenu):

    def __init__(self):
        super(SessionManagerMenu, self).__init__()

    def delete_action(self, index):
        action = self.actions()[index]
        self.removeAction(action)


class IconProvider(QtWidgets.QFileIconProvider):

    def icon(self, fileInfo):
        filename = fileInfo.fileName()
        if filename.endswith(".ssh"):
            return QtGui.QIcon("resources\\ssh.ico")
        elif filename.endswith(".telnet"):
            return QtGui.QIcon("resources\\telnet.ico")
        elif filename.endswith(".vnc"):
            return QtGui.QIcon("resources\\vnc.ico")
        return QtWidgets.QFileIconProvider.icon(self, fileInfo)


class SessionInfoWindow(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(SessionInfoWindow, self).__init__(parent)
        self._setup_dialog()
        self._setup_layout()
        self._setup_host_info_ui()
        self.update_flag = False
        self.root_path = "resources/sessions"

    def set_path(self, path):
        self.root_path = path

    def set_update(self, flag):
        self.update_flag = flag

    def _setup_dialog(self):
        self.setWindowTitle("Session Info")
        self.setWindowIcon(self.style().standardIcon(
            QtWidgets.QStyle.SP_DialogYesButton))

    def _setup_layout(self):
        self.gridLayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridLayout)

    def _setup_host_info_ui(self):

        self.name_label = QtWidgets.QLabel()
        self.name_label.setText("名称: ")
        self.gridLayout.addWidget(self.name_label, 0, 0, 1, 1)

        self.name_line = QtWidgets.QLineEdit()
        self.gridLayout.addWidget(self.name_line, 0, 1, 1, 1)

        self.host_label = QtWidgets.QLabel()
        self.host_label.setText("主机: ")
        self.gridLayout.addWidget(self.host_label, 1, 0, 1, 1)

        self.host_line = QtWidgets.QLineEdit()
        self.gridLayout.addWidget(self.host_line, 1, 1, 1, 1)

        self.protocol_label = QtWidgets.QLabel()
        self.protocol_label.setText("协议: ")
        self.gridLayout.addWidget(self.protocol_label, 2, 0, 1, 1)

        self.protocol_box = QtWidgets.QComboBox()
        # self.protocol_box.setFixedWidth(60)
        self.protocol_box.addItem('ssh')
        self.protocol_box.addItem('telnet')
        self.protocol_box.addItem('vnc')
        self.protocol_box.currentIndexChanged.connect(self.protocol_change)
        self.gridLayout.addWidget(self.protocol_box, 2, 1, 1, 1)

        self.port_label = QtWidgets.QLabel()
        self.port_label.setText("端口: ")
        self.gridLayout.addWidget(self.port_label, 3, 0, 1, 1)

        self.port_line = QtWidgets.QLineEdit()
        self.gridLayout.addWidget(self.port_line, 3, 1, 1, 1)

        self.user_label = QtWidgets.QLabel()
        self.user_label.setText("用户: ")
        self.gridLayout.addWidget(self.user_label, 4, 0, 1, 1)

        self.user_line = QtWidgets.QLineEdit()
        self.gridLayout.addWidget(self.user_line, 4, 1, 1, 1)

        self.pass_label = QtWidgets.QLabel()
        self.pass_label.setText("密码: ")
        self.gridLayout.addWidget(self.pass_label, 5, 0, 1, 1)

        self.pass_line = QtWidgets.QLineEdit()
        self.gridLayout.addWidget(self.pass_line, 5, 1, 1, 1)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.gridLayout.addLayout(self.button_layout, 6, 0, 1, -1)

        self.ok_button = QtWidgets.QPushButton()
        self.ok_button.setText("确认")
        self.button_layout.addWidget(self.ok_button)
        self.ok_button.clicked.connect(self.save_session)

        self.cancel_button = QtWidgets.QPushButton()
        self.cancel_button.setText("取消")
        self.button_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.cancel_session)

    def protocol_change(self):
        if self.protocol_box.currentText() == 'vnc':
            self.user_line.hide()
            self.user_label.hide()
            self.pass_line.hide()
            self.pass_label.hide()
        else:
            self.user_line.show()
            self.user_label.show()
            self.pass_label.show()
            self.pass_line.show()

    def cancel_session(self):
        self.close()

    def get_index_by_protocol(self, protocol):
        protocol_map = {
            "ssh": 0,
            "telnet": 1,
            "vnc": 2
        }
        return protocol_map[protocol]

    def load_host_info(self, host_info):
        self.name_line.setText(host_info['name'])
        self.host_line.setText(host_info['host'])
        self.port_line.setText(host_info['port'])
        self.pass_line.setText(host_info['password'])
        self.user_line.setText(host_info['user'])
        self.protocol_box.setCurrentIndex(self.get_index_by_protocol(host_info['protocol']))
        self.loaded_host_info = host_info

    def get_host_info_by_ui(self):
        name = self.name_line.text()
        host = self.host_line.text()
        port = self.port_line.text() or '22'
        user = self.user_line.text() or None
        password = self.pass_line.text() or None
        protocol = self.protocol_box.currentText()
        if (not host or not port or not protocol or not name) or \
                (protocol != 'vnc' and (not user or not password)):
            QtWidgets.QMessageBox.warning(self, "warning", "主机信息不完整")
            return

        host_info = {
            "name": name,
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "protocol": protocol
        }
        return host_info

    def save_session(self):
        host_info = self.get_host_info_by_ui()
        if not host_info:
            return

        file_name = "%(name)s.%(protocol)s" % host_info
        content = encrypt(json.dumps(host_info)).decode()
        file_path = "{0}/{1}".format(self.root_path, file_name)

        if self.update_flag:
            old_file_name = "%(name)s.%(protocol)s" % self.loaded_host_info
            if file_name == old_file_name:
                with open(file_path, "w+") as file:
                    file.write(content)
                self.close()
                return

            else:
                if os.path.exists(file_path):
                    QtWidgets.QMessageBox.warning(self, "warning", "该主机已存在")
                    return

                os.remove("{0}/{1}".format(self.root_path, old_file_name))

                with open(file_path, "w+") as file:
                    file.write(content)
                self.close()
        else:
            if os.path.exists(file_path):
                QtWidgets.QMessageBox.warning(self, "warning", "该主机已存在")
                return
            with open(file_path, "w+") as file:
                file.write(content)
            self.close()


class CreateDirWindow(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(CreateDirWindow, self).__init__(parent)
        self._setup_dialog()
        self._setup_layout()
        self._setup_ui()
        self.root_path = "resources/sessions"
        self.update_flag = False
        self.old_dir_path = None

    def update_dir(self, dir_path, dir_name):
        self.setWindowTitle("更新目录")
        self.update_flag = True
        self.old_dir_path = dir_path
        self.dir_name_line.setText(dir_name)

    def _setup_dialog(self):
        self.setWindowTitle("创建目录")
        self.setWindowIcon(self.style().standardIcon(
            QtWidgets.QStyle.SP_DialogYesButton))

    def _setup_layout(self):
        self.h_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.h_layout)

    def _setup_ui(self):
        self.dir_name_line = QtWidgets.QLineEdit()
        self.dir_name_line.setPlaceholderText("目录名")
        self.h_layout.addWidget(self.dir_name_line)

        self.ok_button = QtWidgets.QPushButton()
        self.ok_button.setText("确认")
        self.h_layout.addWidget(self.ok_button)

        self.ok_button.clicked.connect(self.create_dir)

    def set_path(self, path):
        self.root_path = path

    def create_dir(self):
        if not self.update_flag:
            dir_name = self.dir_name_line.text()
            dir_path = self.root_path + "/" + dir_name
            os.mkdir(dir_path)
            self.close()
        else:
            new_dir_path = self.root_path + "/" + self.dir_name_line.text()
            os.rename(self.old_dir_path, new_dir_path)
            self.close()


class SessionManagerWindow(QtWidgets.QDialog):

    def __init__(self, plugin, parent=None):
        super(SessionManagerWindow, self).__init__(parent)
        self.plugin = plugin
        self.sessions = []
        self._setup_dialog()
        self._setup_layout()
        self._setup_buttons()
        self._setup_session_list()
        self._setup_session_manage_menu()
        self._setup_session_manager_dir_menu()

    def _setup_dialog(self):
        self.setWindowTitle("Sessions")
        self.setWindowIcon(self.style().standardIcon(
            QtWidgets.QStyle.SP_DialogYesButton))

    def _setup_layout(self):
        self.layout_v = QtWidgets.QVBoxLayout()
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.layout_v.addLayout(self.button_layout)
        self.setLayout(self.layout_v)

    def _setup_buttons(self):
        self.create_button = QtWidgets.QToolButton()
        self.create_button.setPopupMode(self.create_button.MenuButtonPopup)
        self.create_button.setFixedHeight(23)
        self.create_button.setFixedWidth(68)
        self.create_button.setText("新建会话")
        self.button_layout.addWidget(self.create_button)
        self.create_button.clicked.connect(self.create_session)

        menu_style = '''
                QMenu::item {
                    padding-left:5px;
                    width: 60px;
                }
                QMenu::item:selected {
                    background: lightBlue;
                }
                '''
        self.create_button_menu = QtWidgets.QMenu()
        self.create_button_menu.setStyleSheet(menu_style)
        self.create_button.setMenu(self.create_button_menu)
        self.create_dir_action = QtWidgets.QAction("新建目录", self.create_button_menu)
        self.create_button_menu.addAction(self.create_dir_action)
        self.create_dir_action.triggered.connect(self.create_dir)

        # self.update_button = QtWidgets.QPushButton()
        # self.update_button.setText("编辑")
        # self.button_layout.addWidget(self.update_button)
        # self.update_button.clicked.connect(self.update_session)

        # self.delete_button = QtWidgets.QPushButton()
        # self.delete_button.setText("删除")
        # self.button_layout.addWidget(self.delete_button)

        self.open_dir_button = QtWidgets.QPushButton()
        self.open_dir_button.setText("浏览文件夹")
        self.button_layout.addWidget(self.open_dir_button)
        self.open_dir_button.clicked.connect(self.open_dir)

    def open_dir(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl().fromLocalFile(self.file_model.rootPath()))

    def create_dir(self):
        try:
            current_index = self.view.currentIndex()
            file_path = self.file_model.filePath(current_index)
            if not file_path:
                file_path = "resources/sessions"
            elif not self.file_model.isDir(current_index):
                file_path = self.file_model.filePath(current_index.parent())
            self.create_dir_window = CreateDirWindow(self)
            self.create_dir_window.set_path(file_path)
            self.create_dir_window.show()
        except:
            pass

    def update_session(self):
        try:
            current_index = self.view.currentIndex()
            if self.file_model.isDir(current_index):
                self.update_dir(current_index)
            else:
                file_path = self.file_model.filePath(current_index)
                parent_path = self.file_model.filePath(current_index.parent())
                with open(file_path, 'r') as file:
                    hosts_text = file.read()
                    hosts_json_text = decrypt(hosts_text.encode())
                    host_info = json.loads(hosts_json_text)
                    file_name = self.file_model.fileName(current_index)
                    name, extension = os.path.splitext(file_name)
                    host_info['name'] = name
                    self.session_info_window = SessionInfoWindow(self)
                    self.session_info_window.load_host_info(host_info)
                    self.session_info_window.set_path(parent_path)
                    self.session_info_window.set_update(True)
                    self.session_info_window.show()
        except:
            pass

    def update_dir(self, index):
        try:
            dir_path = self.file_model.filePath(index)
            self.create_dir_window = CreateDirWindow(self)
            self.create_dir_window.set_path(self.file_model.filePath(index.parent()))
            self.create_dir_window.update_dir(dir_path, self.file_model.fileName(index))
            self.create_dir_window.show()
        except:
            pass

    def create_session(self):
        try:
            current_index = self.view.currentIndex()
            self.session_info_window = SessionInfoWindow(self)
            if current_index.row() >= 0:

                if self.file_model.isDir(current_index):
                    self.session_info_window.set_path(self.file_model.filePath(current_index))
                else:
                    self.session_info_window.set_path(self.file_model.filePath(current_index.parent()))

            self.session_info_window.show()
        except:
            pass

    def root_dir_menu_exec(self, position):
        try:
            action = self.root_dir_session_menu.exec_(self.view.mapToGlobal(position))
            if action == self.root_create_dir_action:
                self.create_dir_window = CreateDirWindow(self)
                self.create_dir_window.set_path("resources/sessions")
                self.create_dir_window.show()

            elif action == self.root_create_session_action:
                self.session_info_window = SessionInfoWindow(self)
                self.session_info_window.show()
        except:
            pass

    def dir_menu_exec(self, position):
        try:
            action = self.dir_session_menu.exec_(self.view.mapToGlobal(position))
            current_index = self.view.indexAt(position)
            if action == self.create_dir_action:
                file_path = self.file_model.filePath(current_index)
                self.create_dir_window = CreateDirWindow(self)
                self.create_dir_window.set_path(file_path)
                self.create_dir_window.show()
            elif action == self.delete_dir_action:
                self.delete_action_handler(current_index)

            elif action == self.create_session_action:
                self.session_info_window = SessionInfoWindow(self)
                file_path = self.file_model.filePath(current_index)
                self.session_info_window.set_path(file_path)
                self.session_info_window.show()
            elif action == self.update_dir_action:
                self.update_session()
        except:
            pass

    def delete_action_handler(self, current_index):
        try:
            file_path = self.file_model.filePath(current_index)
            if self.file_model.isDir(current_index):
                shutil.rmtree(file_path)
            else:
                os.remove(file_path)
        except:
            pass

    def session_menu_exec(self, current_index, position):
        action = self.session_manage_menu.exec_(self.view.mapToGlobal(position))
        if action == self.delete_action:
            self.delete_action_handler(current_index)
        elif action == self.update_action:
            self.update_session()

    def session_right_click(self, position):
        try:
            current_index = self.view.indexAt(position)
            if current_index.row() < 0:
                self.root_dir_menu_exec(position)
            else:
                if self.file_model.isDir(current_index):
                    self.dir_menu_exec(position)
                else:
                    self.session_menu_exec(current_index, position)

        except:
            pass

    def session_double_click_action(self, qModelIndex):
        try:
            if self.file_model.isDir(qModelIndex):
                return

            self.close()
            file_path = self.file_model.filePath(qModelIndex)
            with open(file_path, 'r') as file:
                hosts_text = file.read()
                hosts_json_text = decrypt(hosts_text.encode())
                host_info = json.loads(hosts_json_text)
                self.plugin.connect_host(host_info)
        except:
            pass

    # def flush_sessions(self):
    #     self.sessions = self.plugin.get_hosts_record()
    #     self.slm.setStringList(self.sessions)

    def _setup_session_list(self):
        file_model = QtWidgets.QFileSystemModel()
        self.file_model = file_model
        file_model.setRootPath('resources\\sessions')
        file_model.setIconProvider(IconProvider())
        self.view = QtWidgets.QTreeView(self)
        self.view.setSortingEnabled(True)
        self.view.setModel(file_model)
        for i in range(1, file_model.columnCount()):
            self.view.hideColumn(i)

        self.view.setHeaderHidden(True)
        self.view.setRootIndex(file_model.index('resources\\sessions'))
        self.layout_v.addWidget(self.view)

        self.view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.session_right_click)
        self.view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.view.doubleClicked.connect(self.session_double_click_action)

    def _setup_session_manage_menu(self):
        self.session_manage_menu = QtWidgets.QMenu()
        self.delete_action = self.session_manage_menu.addAction("删除")
        self.update_action = self.session_manage_menu.addAction("编辑")

    def _setup_session_manager_dir_menu(self):
        self.root_dir_session_menu = QtWidgets.QMenu()
        self.root_create_session_action = self.root_dir_session_menu.addAction("新建会话")
        self.root_create_dir_action = self.root_dir_session_menu.addAction("新建目录")

        self.dir_session_menu = QtWidgets.QMenu()
        self.create_session_action = self.dir_session_menu.addAction("新建会话")
        self.create_dir_action = self.dir_session_menu.addAction("新建目录")
        self.delete_dir_action = self.dir_session_menu.addAction("删除")
        self.update_dir_action = self.dir_session_menu.addAction("编辑")


class SessionManagerPlugin(ZShellPlugin):
    name = "SessionManager"

    def __init__(self, main_win):
        super(SessionManagerPlugin, self).__init__(main_win)
        self.hosts_info = {}
        self.session_manager_window = None

    def start(self):
        self._setup_toolbar_button()
        # self._setup_host_menu()

    def _setup_toolbar_button(self):
        self.toolbar_button = SessionManagerToolButton(self)
        self.add_to_toolbar(self.toolbar_button)

    def show_session_manager(self):
        try:
            self.session_manager_window = SessionManagerWindow(self, self.main_win)
            self.session_manager_window.show()
        except:
            pass

    # def read_hosts_info_from_file(self):
    #     try:
    #         with open("resources\hosts.json", 'r') as file_r:
    #             hosts_text = file_r.read()
    #
    #         if hosts_text:
    #             hosts_json_text = decrypt(hosts_text.encode())
    #             self.hosts_info = json.loads(hosts_json_text)
    #     except Exception as e:
    #         self.box_error("无法读取主机信息，主机信息已损坏: {0}！".format(e))

    # def write_hosts_info_to_file(self):
    #     try:
    #         new_hosts_text = json.dumps(self.hosts_info)
    #         new_hosts_text = encrypt(new_hosts_text).decode()
    #
    #         with open("resources\hosts.json", 'w') as file_w:
    #             file_w.write(new_hosts_text)
    #     except Exception as e:
    #         self.box_error("保存主机信息失败:{0}！".format(e))

    # @do_in_thread
    # def _setup_host_menu(self):
    # self.host_menu = SessionManagerMenu()
    # menu_style = '''
    #         QMenu::item {
    #             background: white;
    #         }
    #         '''
    # self.host_menu.setStyleSheet(menu_style)
    # self.toolbar_button.setMenu(self.host_menu)
    # self.add_hosts_info_to_menu()

    # def add_hosts_info_to_menu(self):
    #     self.read_hosts_info_from_file()
    #     for host_key, host_info in self.hosts_info.items():
    #         self.add_host_info_action(host_key, host_info['protocol'])
    #     self.host_menu.show()
    #
    # def add_host_info_action(self, host_key, host_type):
    #     host_action = SessionManagerMenuAction(self, host_key, self.host_menu)
    #     icon_path = "resources/{0}.ico".format(host_type)
    #     host_action.setIcon(QtGui.QIcon(icon_path))
    #     self.host_menu.addAction(host_action)
    #
    # def del_host_info_action(self, action_index):
    #     self.host_menu.delete_action(action_index)

    def get_hosts_record(self):
        return list(self.hosts_info.keys())

    def gen_host_key(self, host_info):
        host = host_info['host']
        user = host_info['user']
        port = host_info['port']
        protocol = host_info['protocol']
        if protocol == 'vnc':
            host = "{0}:{1}".format(host, port)
        host_key = "[{0}] {1}".format(protocol, host)
        if user:
            host_key = "{0} ({1})".format(host_key, user)
        return host_key

    def add_host(self, host_info):
        if not host_info.get('name'):
            host_info['name'] = host_info.get("host")
        self.session_info = SessionInfoWindow(self.main_win)
        self.session_info.load_host_info(host_info)
        self.session_info.show()

    # def remove_host(self, host_key, action_index):
    #     self.hosts_info.pop(host_key)
    #     self.write_hosts_info_to_file()
    #     self.del_host_info_action(action_index)

    # def connect_host_by_key(self, host_key):
    #     host_info = self.hosts_info.get(host_key)
    #     self.connect_host(host_info)

    def connect_host(self, host_info):
        try:
            if host_info.get("protocol") == "vnc":
                tab_plugin = PluginManager().get_plugin("VncTab")
            else:
                tab_plugin = PluginManager().get_plugin("PuttyTab")

            tab_manager_plugin = PluginManager().get_plugin("TabManager")
            tab_cls = tab_plugin.get_tab_cls()
            tab_manager_plugin.tab_create(tab_cls, host_info=host_info)
        except:
            import traceback
            traceback.print_exc()
