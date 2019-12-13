from zshell.plugin.base import ZShellPlugin
from zshell.common.utils import do_in_thread
from PyQt5 import QtCore, QtWidgets, QtGui
from zshell.core.manage import PluginManager
import time
import os
import webbrowser
from zshell.core.app import main_win


class SettingButton(QtWidgets.QToolButton):

    def __init__(self, parent=None):
        super(SettingButton, self).__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        set_button_style = '''
        QToolButton{background-color:transparent;}
        QToolButton::menu-indicator{image:none;}
        QToolButton:hover { background-color:rgb(176, 176, 176) }
        '''
        self.setPopupMode(self.InstantPopup)
        self.setText(" ••• ")
        self.setFixedWidth(28)
        self.setFixedHeight(23)
        self.setStyleSheet(set_button_style)


class SettingQmenu(QtWidgets.QMenu):

    def __init__(self, button, parent=None):
        super(SettingQmenu, self).__init__(parent)
        self.button = button
        self._setup_ui()

    def _setup_ui(self):
        self.setFixedWidth(180)
        self.add_action_to_setting_menu()

    def add_action_to_setting_menu(self):
        self.setting_action = QtWidgets.QAction("设置", self)
        self.setting_action.setShortcut("Ctrl+S")
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


class SettingPlugin(ZShellPlugin):
    name = "Setting"

    def __init__(self, main_win):
        super(SettingPlugin, self).__init__(main_win)
        self._setup_toolbar()
        self._setup_setting_menu()

    def _setup_toolbar(self):
        self.set_button = SettingButton()
        self.add_to_toolbar(self.set_button)

    def _setup_setting_menu(self):
        self.set_menu = SettingQmenu(self.set_button)
        self.set_button.setMenu(self.set_menu)
