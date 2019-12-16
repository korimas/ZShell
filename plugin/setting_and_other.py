from zshell.plugin.base import ZShellPlugin
from zshell.plugin.tab_manager import ZShellTab
from PyQt5 import QtWidgets, QtCore, QtGui
from zshell.core.manage import PluginManager
import webbrowser
from zshell.core.app import main_win

setting_tab_opened = False


class SettingButton(QtWidgets.QToolButton):

    def __init__(self, parent=None):
        super(SettingButton, self).__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        set_button_style = '''
        QToolButton::menu-indicator{
            image:none;
        }
        QToolButton {
            background-color:transparent;
            border: none;
        }
        QToolButton:hover { 
            background-color: lightGray; 
            border: none;
        }
        '''
        self.setPopupMode(self.InstantPopup)
        self.setText(" ••• ")
        self.setFixedWidth(28)
        self.setFixedHeight(23)
        self.setStyleSheet(set_button_style)


class SettingAction(QtWidgets.QAction):

    def __init__(self, name, menu):
        super(SettingAction, self).__init__(name, menu)
        self._setup_ui()

    def _setup_ui(self):
        self.setShortcut("Ctrl+S")
        self.triggered.connect(self.open_setting_tab)

    def open_setting_tab(self):
        try:
            global setting_tab_opened
            if not setting_tab_opened:
                tab_manager_plugin = PluginManager().get_plugin("TabManager")
                tab_manager_plugin.tab_create(SettingTab)
                setting_tab_opened = True
        except:
            import traceback
            traceback.print_exc()


class SettingQmenu(QtWidgets.QMenu):

    def __init__(self, button, parent=None):
        super(SettingQmenu, self).__init__(parent)
        self.button = button
        self._setup_ui()

    def _setup_ui(self):
        self.setFixedWidth(180)
        self.add_action_to_setting_menu()

    def add_action_to_setting_menu(self):
        self.setting_action = SettingAction("设置", self)
        self.addAction(self.setting_action)
        self.help_action = QtWidgets.QAction("帮助", self)
        self.help_action.setShortcut("Ctrl+H")
        self.help_action.triggered.connect(self.help_action_handler)
        self.addAction(self.help_action)

    def help_action_handler(self):
        try:
            webbrowser.open('https://github.com/zpdev/ZShell')
        except:
            pass

    def showEvent(self, event):
        menu_x_pos = self.pos().x()
        menu_width = self.size().width()
        button_width = self.button.size().width()

        if menu_x_pos > main_win.mapToGlobal(self.button.pos()).x():
            pos_x = menu_x_pos - menu_width + button_width
            pos_y = self.pos().y()
            self.move(pos_x, pos_y)


class BaseContent(QtWidgets.QWidget):

    def __init__(self, name, parent=None):
        super(BaseContent, self).__init__(parent)
        self.name = name
        self._setup_layout()
        self._setup_ui()
        self._setup_content()

    def _setup_layout(self):
        self.layout_v = QtWidgets.QVBoxLayout()
        self.layout_v.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setLayout(self.layout_v)

    def _setup_ui(self):
        self._setup_title()

    def _setup_title(self):
        title_style = '''
        QLabel {
        font-size:16px;
        }
'''
        self.title_label = QtWidgets.QLabel()
        self.title_label.setText(self.name)
        self.title_label.setStyleSheet(title_style)
        self.title_label.setMargin(20)
        self.layout_v.addWidget(self.title_label)

    def _setup_content(self):
        pass


class AboutContent(BaseContent):

    def _setup_content(self):
        self.desc_label = QtWidgets.QLabel()
        self.desc_label.setText("此软件基于 putty 和 PyQt5 制作而成.")
        self.layout_v.addWidget(self.desc_label)

        self.author_label = QtWidgets.QLabel()
        self.author_label.setText('作者：zpzhou@hillstonenet.com\n')
        self.layout_v.addWidget(self.author_label)

        self.link_label = QtWidgets.QLabel()
        self.link_label.setText('开源地址：<a href="https://github.com/zpdev/ZShell">https://github.com/zpdev/ZShell</a>')
        self.link_label.setOpenExternalLinks(True)
        self.layout_v.addWidget(self.link_label)


class SettingTab(ZShellTab):

    def __init__(self, index, tab_widget, parent=None):
        super(SettingTab, self).__init__(index, tab_widget, parent)
        self.title = "设置"
        self.left_width = 200

    def start(self):
        self._setup_layout()
        self._setup_left_side()
        self._setup_tab_content()

    def _setup_layout(self):
        self.layout_h = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout_h)

    def _setup_left_side(self):
        self.left_side = QtWidgets.QWidget()
        self.left_side.setFixedWidth(235)
        self.left_side.setStyleSheet("border-right: 1px solid gray;")
        self.left_layout = QtWidgets.QVBoxLayout()
        self.left_side.setLayout(self.left_layout)
        self.layout_h.addWidget(self.left_side)

    def add_to_left_side(self, widget):
        self.left_layout.addWidget(widget)

    def _setup_tab_content(self):
        qlist_widget_style = '''
        QListWidget, QListView, QTreeWidget, QTreeView {
            outline: 0px;
        }
        
        QListWidget {
            min-width: 200px;
            max-width: 200px;
            color: Black;
        }
        QListWidget::Item {
            border-left: 5px solid transparent;
            color: Black;
            margin: 5px 0px;
            padding: 0px 20px;
        }
        QListWidget::Item:hover {            
            background: lightGray;
        }
        QListWidget::Item:selected {
            background: lightGray;
            border-left: 5px solid lightBlue;
            color: Black;
        }
        HistoryPanel:hover {
            background: lightGray;
        }
        '''
        title_style = '''
        QLabel {
            font-size:20px;
            font-weight: bold;
        }
        '''
        self.left_title = QtWidgets.QLabel()
        self.left_title.setText("设置")
        self.left_title.setStyleSheet(title_style)
        self.left_title.setMargin(20)
        self.add_to_left_side(self.left_title)

        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("    搜索设置")
        self.search_input.setFixedWidth(200)
        self.search_input.setFixedHeight(39)
        self.add_to_left_side(self.search_input)

        self.left_list = QtWidgets.QListWidget()
        self.left_list.setStyleSheet(qlist_widget_style)
        self.add_to_left_side(self.left_list)

        self.right_side = QtWidgets.QStackedWidget()
        self.layout_h.addWidget(self.right_side)

        self.left_list.currentRowChanged.connect(self.right_side.setCurrentIndex)  # list和右侧窗口的index对应绑定
        self.left_list.setFrameShape(QtWidgets.QListWidget.NoFrame)  # 去掉边框
        self.left_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # 隐藏滚动条
        self.left_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        list_str = ['会话', '终端', '窗口', '连接', '关于']
        setting_widget_list = [BaseContent, BaseContent, BaseContent, BaseContent, AboutContent]

        for i in range(len(list_str)):
            item = QtWidgets.QListWidgetItem(list_str[i], self.left_list)  # 左侧选项的添加
            item.setSizeHint(QtCore.QSize(self.left_width, 50))
            item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)  # 居中显示
            if setting_widget_list[i]:
                widget = setting_widget_list[i](list_str[i])
                self.right_side.addWidget(widget)
            if i == 0:
                item.setSelected(True)

    def close_action(self):
        global setting_tab_opened
        setting_tab_opened = False


class SettingPlugin(ZShellPlugin):
    name = "Setting"

    def __init__(self, main_win):
        super(SettingPlugin, self).__init__(main_win)

    def start(self):
        self._setup_toolbar()
        self._setup_setting_menu()

    def _setup_toolbar(self):
        self.set_button = SettingButton()
        self.add_to_toolbar(self.set_button)

    def _setup_setting_menu(self):
        self.set_menu = SettingQmenu(self.set_button)
        self.set_button.setMenu(self.set_menu)
