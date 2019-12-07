from PyQt5 import QtCore, QtWidgets
import json
import traceback
import os


# from zshell.common.utils import do_in_thread


class ZShellToolBar(QtWidgets.QWidget):

    def __init__(self, main_win=None):
        super(ZShellToolBar, self).__init__()
        self.main_win = main_win
        self.host_info = {}
        self.session_manager_dailog = None
        self.session_action_index = {}
        self.upload_win = None
        self.session_empty = True
        self.empty_action = None
        self.upload_button = None
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
        self.add_upload_area()
        self.add_spacer()
        self.add_about_button()

    def add_spacer(self):
        self.spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layout_h.addItem(self.spacer_item)

    def add_upload_area(self):
        self.upload_button = UploadButton(self.main_win, self)
        self.upload_button.setToolTip('上传至当前标签对应的主机')
        self.upload_button.setText('拖动文件至此上传')
        self.layout_h.addWidget(self.upload_button)

    def add_about_button(self):
        self.about_button = QtWidgets.QPushButton(self)
        self.about_button.setToolTip('关于')
        # self.about_button.setIcon(self.style().standardIcon(
        #     QtWidgets.QStyle.SP_DialogHelpButton))
        self.about_button.setText('?')
        self.about_button.setFixedWidth(24)
        self.layout_h.addWidget(self.about_button)
        self.about_button.clicked.connect(self.about)

    def about(self):
        QtWidgets.QMessageBox.information(self, "关于", "作者：zpzhou@hillstonenet.com\n项目：https://github.com/zpdev/ZShell")

    def add_quick_connect(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setText("  快速登录：")
        self.layout_h.addWidget(self.label)

        self.host_line_edit = QtWidgets.QLineEdit(self)
        self.layout_h.addWidget(self.host_line_edit)
        self.host_line_edit.setPlaceholderText("主机")
        self.host_line_edit.setFixedWidth(100)
        self.host_line_edit.returnPressed.connect(self.quick_connect_handler)

        self.user_line_edit = QtWidgets.QLineEdit(self)
        self.layout_h.addWidget(self.user_line_edit)
        self.user_line_edit.setPlaceholderText("用户名")
        self.user_line_edit.setFixedWidth(100)
        self.user_line_edit.returnPressed.connect(self.quick_connect_handler)

        self.pass_line_edit = QtWidgets.QLineEdit(self)
        self.layout_h.addWidget(self.pass_line_edit)
        self.pass_line_edit.setPlaceholderText("密码")
        self.pass_line_edit.setFixedWidth(100)
        self.pass_line_edit.returnPressed.connect(self.quick_connect_handler)

        self.port_line_edit = QtWidgets.QLineEdit(self)
        self.layout_h.addWidget(self.port_line_edit)
        self.port_line_edit.setPlaceholderText("端口(22)")
        self.port_line_edit.setFixedWidth(100)
        self.port_line_edit.returnPressed.connect(self.quick_connect_handler)

        self.save_session_button = QtWidgets.QToolButton(self)
        self.save_session_button.setToolTip('保存登录信息')
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
        port = self.port_line_edit.text() or '22'
        user = self.user_line_edit.text() or None
        password = self.pass_line_edit.text() or None

        if not host or not user or not password:
            QtWidgets.QMessageBox.information(self, "提示", "请输入完整的登录信息")
            return

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
        port = self.port_line_edit.text() or '22'
        user = self.user_line_edit.text() or None
        password = self.pass_line_edit.text() or None

        if not host or not user or not password:
            QtWidgets.QMessageBox.information(self, "提示", "请输入完整的登录信息")
            return
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

        if self.host_info:
            self.session_empty = False

        for key, host_info in self.host_info.items():
            self.add_menu_action(host_info)

        if self.session_empty:
            self.add_empty_action()

    def add_empty_action(self):
        if not self.empty_action:
            self.empty_action = QtWidgets.QAction(" - Empty - ", self.host_menu)
            self.empty_action.setEnabled(False)
        self.host_menu.addAction(self.empty_action)
        self.session_empty = True

    def delete_empty_action(self):
        self.host_menu.removeAction(self.empty_action)
        self.session_empty = False

    def add_menu_action(self, host_info):
        host = host_info['host']
        user = host_info['user']
        key = "%s(%s)" % (host, user)
        host_connect_action = QtWidgets.QAction(key, self.host_menu)
        host_connect_action.triggered.connect(lambda: self.connect_action_handler(key))
        self.host_menu.addAction(host_connect_action)
        self.session_action_index[key] = host_connect_action
        if self.session_empty:
            self.delete_empty_action()

    def delete_menu_action(self, action_name):
        self.host_menu.removeAction(self.session_action_index[action_name])
        self.session_action_index.pop(action_name)

        if not self.session_action_index:
            self.add_empty_action()

    def show_session_manager(self):
        if not self.session_manager_dailog:
            self.session_manager_dailog = SessionManagerWin(self)

        self.session_manager_dailog.flush(self.host_info)
        self.session_manager_dailog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.session_manager_dailog.show()


class SessionManagerWin(QtWidgets.QDialog):

    def __init__(self, toolbar):
        super(SessionManagerWin, self).__init__()
        self.toolbar = toolbar
        self.main_win = toolbar.main_win
        self.host_info = {}
        self.hosts = []
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
                self.toolbar.delete_menu_action(host_key)
                new_hosts_text = json.dumps(self.host_info)
                with open("resources\hosts.json", 'w') as file_w:
                    file_w.write(new_hosts_text)

        except:
            traceback.print_exc()


class UploadButton(QtWidgets.QPushButton):

    def __init__(self, main_win, parent=None):
        super(UploadButton, self).__init__(parent)
        self.main_win = main_win
        self.init_ui()

    def init_ui(self):
        self.setAcceptDrops(True)

    def dropEvent(self, event):
        try:
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.main_win.tabWidget.upload_files(links)

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

    # def dragMoveEvent(self, event):
    #     try:
    #         print("drag move event")
    #         print(event)
    #         event.ignore()
    #     except Exception as e:
    #         print(e)
