from PyQt5 import QtCore, QtWidgets
import json
import traceback


# from zshell.common.utils import do_in_thread


class ZShellToolBar(QtWidgets.QWidget):

    def __init__(self, main_win=None):
        super(ZShellToolBar, self).__init__()
        self.main_win = main_win
        self.host_info = {}
        self.connect_action_dict = {}
        self.session_manager_dailog = None
        self.session_action_index = {}
        self.init_layout()
        self.init_ui()

    def init_layout(self):
        self.layout_h = QtWidgets.QHBoxLayout()
        self.layout_h.setContentsMargins(0, 0, 0, 0)
        self.layout_h.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.setLayout(self.layout_h)

    def init_ui(self):
        self.add_sessions_button()
        self.add_quick_connect()
        self.add_about_button()

    def add_about_button(self):
        self.about_button = QtWidgets.QToolButton(self)
        self.about_button.setToolTip('关于')
        self.about_button.setIcon(self.style().standardIcon(
            QtWidgets.QStyle.SP_DialogHelpButton))
        self.layout_h.addWidget(self.about_button)
        self.about_button.clicked.connect(self.about)

    def about(self):
        QtWidgets.QMessageBox.information(self, "关于", "作者：zpzhou@hillstonenet.com")

    def add_quick_connect(self):
        self.host_line_edit = QtWidgets.QLineEdit(self)
        self.layout_h.addWidget(self.host_line_edit)
        self.host_line_edit.setPlaceholderText("主机")
        self.host_line_edit.setFixedWidth(120)
        self.host_line_edit.returnPressed.connect(self.quick_connect_handler)

        self.port_line_edit = QtWidgets.QLineEdit(self)
        self.layout_h.addWidget(self.port_line_edit)
        self.port_line_edit.setPlaceholderText("端口")
        self.port_line_edit.setFixedWidth(120)
        self.port_line_edit.returnPressed.connect(self.quick_connect_handler)

        self.user_line_edit = QtWidgets.QLineEdit(self)
        self.layout_h.addWidget(self.user_line_edit)
        self.user_line_edit.setPlaceholderText("用户名")
        self.user_line_edit.setFixedWidth(120)
        self.user_line_edit.returnPressed.connect(self.quick_connect_handler)

        self.pass_line_edit = QtWidgets.QLineEdit(self)
        self.layout_h.addWidget(self.pass_line_edit)
        self.pass_line_edit.setPlaceholderText("密码")
        self.pass_line_edit.setFixedWidth(120)
        self.pass_line_edit.returnPressed.connect(self.quick_connect_handler)

        self.save_session_button = QtWidgets.QToolButton(self)
        self.save_session_button.setToolTip('保存')
        self.save_session_button.setIcon(self.style().standardIcon(
            QtWidgets.QStyle.SP_DialogSaveButton))
        self.layout_h.addWidget(self.save_session_button)
        self.save_session_button.clicked.connect(self.session_save)

    def session_save(self):
        host_info = self.record_save()
        if host_info:
            self.add_menu_action(host_info)

    def record_save(self):
        host = self.host_line_edit.text()
        if not host:
            return
        port = self.port_line_edit.text() or '22'
        user = self.user_line_edit.text() or None
        password = self.pass_line_edit.text() or None

        host_info = {
            "host": host,
            "port": port,
            "user": user,
            "password": password
        }

        key = "%s(%s)" % (host, user)
        if key in self.host_info:
            return

        self.host_info[key] = host_info

        new_hosts_text = json.dumps(self.host_info)

        with open("resources\hosts.json", 'w') as file_w:
            file_w.write(new_hosts_text)

        return host_info

    def quick_connect_handler(self):
        host = self.host_line_edit.text()
        if not host:
            return
        port = self.port_line_edit.text() or '22'
        user = self.user_line_edit.text() or None
        password = self.pass_line_edit.text() or None
        self.main_win.tabWidget.ssh_tab_create(host, port, user, password)

    def add_sessions_button(self):
        self.sessions_button = QtWidgets.QToolButton(self)
        self.sessions_button.setToolTip('会话')
        self.sessions_button.setIcon(self.style().standardIcon(
            QtWidgets.QStyle.SP_DialogYesButton))
        self.sessions_button.setPopupMode(self.sessions_button.MenuButtonPopup)
        self.layout_h.addWidget(self.sessions_button)
        self.host_menu = QtWidgets.QMenu()
        self.sessions_button.setMenu(self.host_menu)
        self.sessions_button.clicked.connect(self.show_session_manager)
        self.add_all_menu_action()

    def connect_action_handler(self, host):
        try:
            host_info = self.host_info[host]
            self.main_win.tabWidget.ssh_tab_create(**host_info)
        except:
            traceback.print_exc()

    # @do_in_thread
    def add_all_menu_action(self):
        with open("resources\hosts.json", 'r') as file_r:
            hosts_text = file_r.read()

        if hosts_text:
            self.host_info = json.loads(hosts_text)

        for key, host_info in self.host_info.items():
            self.add_menu_action(host_info)

    def add_menu_action(self, host_info):
        host = host_info['host']
        user = host_info['user']
        key = "%s(%s)" % (host, user)
        host_connect_action = QtWidgets.QAction(key, self.host_menu)
        host_connect_action.triggered.connect(lambda: self.connect_action_handler(key))
        self.host_menu.addAction(host_connect_action)
        self.session_action_index[key] = host_connect_action

    def show_session_manager(self):
        if not self.session_manager_dailog:
            self.session_manager_dailog = SessionManagerWin(self.host_menu, self.session_action_index, self.main_win)

        self.session_manager_dailog.flush(self.host_info)
        self.session_manager_dailog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.session_manager_dailog.show()


class SessionManagerWin(QtWidgets.QDialog):

    def __init__(self, session_menu, session_action_index, main_win):
        super(SessionManagerWin, self).__init__()
        self.main_win = main_win
        self.host_info = {}
        self.hosts = list(self.host_info.keys())
        self.session_menu = session_menu
        self.session_action_index = session_action_index
        self.init_dialog()
        self.init_layout()
        self.init_ui()

    def flush(self, host_info):
        self.host_info = host_info
        self.hosts = list(self.host_info.keys())
        self.flush_session_list()

    def init_dialog(self):
        self.setWindowTitle("Sessions")
        self.setWindowIcon(self.style().standardIcon(
            QtWidgets.QStyle.SP_DialogYesButton))

    def init_layout(self):
        self.layout_v = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout_v)

    def init_ui(self):
        self.session_list_view = QtWidgets.QListView(self)
        self.layout_v.addWidget(self.session_list_view)
        self.session_list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.session_list_view.customContextMenuRequested.connect(self.open_menu)
        self.session_list_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        # self.session_list_view.clicked.connect(self.click_list_item)
        self.session_list_view.doubleClicked.connect(self.connect_host)
        self.slm = QtCore.QStringListModel()

    def flush_session_list(self):
        self.slm.setStringList(self.hosts)
        self.session_list_view.setModel(self.slm)

    def connect_host(self, qModelIndex):
        try:
            self.close()
            host = self.hosts[qModelIndex.row()]
            host_info = self.host_info[host]
            self.main_win.tabWidget.ssh_tab_create(**host_info)
        except:
            traceback.print_exc()

    # def click_list_item(self, qModelIndex):
    #     try:
    #         host = self.hosts[qModelIndex.row()]
    #         print("你选择了: " + str(self.host_info[host]))
    #     except:
    #         traceback.print_exc()

    def open_menu(self, position):
        try:
            menu = QtWidgets.QMenu()
            delete_action = menu.addAction("删除")
            action = menu.exec_(self.session_list_view.mapToGlobal(position))
            if action == delete_action:
                row_index = self.session_list_view.currentIndex().row()
                host_key = self.hosts[row_index]
                self.host_info.pop(host_key)
                self.hosts.remove(host_key)
                self.slm.removeRow(row_index)
                new_hosts_text = json.dumps(self.host_info)
                self.session_menu.removeAction(self.session_action_index[host_key])
                self.session_action_index.pop(host_key)
                with open("resources\hosts.json", 'w') as file_w:
                    file_w.write(new_hosts_text)

        except:
            traceback.print_exc()
