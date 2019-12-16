from zshell.plugin.base import ZShellPlugin
from zshell.core.manage import PluginManager
from PyQt5 import QtCore, QtWidgets
import json


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
        self.setPopupMode(self.MenuButtonPopup)
        self.clicked.connect(self.plugin.show_session_manager)


class SessionManagerMenu(QtWidgets.QMenu):

    def __init__(self):
        super(SessionManagerMenu, self).__init__()

    def delete_action(self, index):
        action = self.actions()[index]
        self.removeAction(action)


class SessionManagerWindow(QtWidgets.QDialog):

    def __init__(self, plugin, parent=None):
        super(SessionManagerWindow, self).__init__(parent)
        self.plugin = plugin
        self.sessions = []
        self._setup_dialog()
        self._setup_layout()
        self._setup_session_list()
        self._setup_session_manage_menu()

    def _setup_dialog(self):
        self.setWindowTitle("Sessions")
        self.setWindowIcon(self.style().standardIcon(
            QtWidgets.QStyle.SP_DialogYesButton))
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    def _setup_layout(self):
        self.layout_v = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout_v)

    def _setup_session_list(self):
        self.session_list_view = QtWidgets.QListView(self)
        self.layout_v.addWidget(self.session_list_view)

        self.session_list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.session_list_view.customContextMenuRequested.connect(self.session_right_click)
        self.session_list_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.session_list_view.doubleClicked.connect(self.session_double_click_action)
        self.slm = QtCore.QStringListModel()
        self.slm.setStringList(self.sessions)
        self.session_list_view.setModel(self.slm)

    def _setup_session_manage_menu(self):
        self.session_manage_menu = QtWidgets.QMenu()
        self.delete_action = self.session_manage_menu.addAction("删除")

    def session_right_click(self, position):
        try:
            action = self.session_manage_menu.exec_(self.session_list_view.mapToGlobal(position))
            if action == self.delete_action:
                row_index = self.session_list_view.currentIndex().row()
                host_key = self.sessions.pop(row_index)
                self.plugin.remove_host(host_key, row_index)
                self.slm.removeRow(row_index)

        except:
            import traceback
            traceback.print_exc()

    def session_double_click_action(self, qModelIndex):
        try:
            self.close()
            session_index = qModelIndex.row()
            host_key = self.sessions[session_index]
            self.plugin.connect_host_by_key(host_key)
        except:
            import traceback
            traceback.print_exc()

    def flush_sessions(self):
        self.sessions = self.plugin.get_hosts_record()
        self.slm.setStringList(self.sessions)


class SessionManagerPlugin(ZShellPlugin):
    name = "SessionManager"

    def __init__(self, main_win):
        super(SessionManagerPlugin, self).__init__(main_win)
        self.hosts_info = {}
        self.session_manager_window = None

    def start(self):
        self._setup_toolbar_button()
        self._setup_host_menu()

    def _setup_toolbar_button(self):
        self.toolbar_button = SessionManagerToolButton(self)
        self.add_to_toolbar(self.toolbar_button)

    def show_session_manager(self):
        if not self.session_manager_window:
            self.session_manager_window = SessionManagerWindow(self, self.main_win)
        self.session_manager_window.flush_sessions()
        self.session_manager_window.show()

    def read_hosts_info_from_file(self):
        try:
            with open("resources\hosts.json", 'r') as file_r:
                hosts_text = file_r.read()

            if hosts_text:
                self.hosts_info = json.loads(hosts_text)
        except:
            pass

    def write_hosts_info_to_file(self):
        try:
            new_hosts_text = json.dumps(self.hosts_info)

            with open("resources\hosts.json", 'w') as file_w:
                file_w.write(new_hosts_text)
        except:
            pass

    # @do_in_thread
    def _setup_host_menu(self):
        self.host_menu = SessionManagerMenu()
        self.toolbar_button.setMenu(self.host_menu)
        self.add_hosts_info_to_menu()

    def add_hosts_info_to_menu(self):
        self.read_hosts_info_from_file()
        for host_key, host_info in self.hosts_info.items():
            self.add_host_info_action(host_key)
        self.host_menu.show()

    def add_host_info_action(self, host_key):
        host_action = SessionManagerMenuAction(self, host_key, self.host_menu)
        self.host_menu.addAction(host_action)

    def del_host_info_action(self, action_index):
        self.host_menu.delete_action(action_index)

    def get_hosts_record(self):
        return list(self.hosts_info.keys())

    def gen_host_key(self, host_info):
        host = host_info['host']
        user = host_info['user']
        return "{0}({1})".format(host, user)

    def add_host(self, host_info):
        host_key = self.gen_host_key(host_info)
        if host_key not in self.hosts_info:
            self.hosts_info[host_key] = host_info
            self.write_hosts_info_to_file()
            self.add_host_info_action(host_key)
        else:
            self.box_info("当前主机信息已存在！")

    def remove_host(self, host_key, action_index):
        self.hosts_info.pop(host_key)
        self.write_hosts_info_to_file()
        self.del_host_info_action(action_index)

    def connect_host_by_key(self, host_key):
        host_info = self.hosts_info.get(host_key)
        self.connect_host(host_info)

    def connect_host(self, host_info):
        try:
            putty_plugin = PluginManager().get_plugin("PuttyTab")
            tab_manager_plugin = PluginManager().get_plugin("TabManager")
            tab_cls = putty_plugin.get_tab_cls()
            tab_manager_plugin.tab_create(tab_cls, host_info=host_info)
        except:
            import traceback
            traceback.print_exc()
