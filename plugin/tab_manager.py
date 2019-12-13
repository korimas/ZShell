from zshell.plugin.base import ZShellPlugin
from PyQt5 import QtCore, QtWidgets
import traceback


class ListTabAction(QtWidgets.QAction):

    def __init__(self, index, name, menu):
        self.index = index
        self.name = name
        self.menu = menu
        super(ListTabAction, self).__init__(self.name, menu)
        self.triggered.connect(self.execute)

    def set_tab_index(self, index):
        self.index = index

    def update_index(self, index, name):
        self.index = index
        self.setText(name)

    def execute(self):
        self.menu.select_action(self)


class ListTabMenu(QtWidgets.QMenu):

    def __init__(self, tab_widget):
        self.tab_widget = tab_widget
        self.action_array = []
        super(ListTabMenu, self).__init__()

    def insert_action(self, index, action):
        action_count = len(self.action_array)
        if index == action_count:
            self.addAction(action)
        if index < action_count:
            before_action = self.action_array[index]
            self.insertAction(before_action, action)

        self.action_array.insert(index, action)

    def remove_action(self, index):
        delte_action = self.action_array[index]
        self.action_array.remove(delte_action)
        self.removeAction(delte_action)

    def select_action(self, action):
        self.tab_widget.setCurrentIndex(action.index)


class ZShellTab(QtWidgets.QWidget):

    def __init__(self, index, tab_widget, parent=None):
        super(ZShellTab, self).__init__(parent)
        self.index = index
        self.title = "ZShell_Tab"
        self.tab_widget = tab_widget
        self._setup_index_action(index)

    def _setup_index_action(self, index):
        self.tab_list_action = ListTabAction(index, self.gen_tab_name(), self.tab_widget.get_list_tabs_menu())

    def leave_action(self):
        pass

    def enter_action(self):
        pass

    def close_action(self):
        pass

    def gen_tab_name(self):
        return "{0}-{1}".format(self.index + 1, self.title)

    def get_tab_list_action(self):
        return self.tab_list_action

    def update_index(self, index):
        self.index = index
        self.tab_list_action.update_index(index, self.gen_tab_name())
        self.update_tab_name()

    def update_tab_name(self):
        self.tab_widget.setTabText(self.index, self.gen_tab_name())

    def get_right_click_menu(self):
        pass

    def deal_right_click_action(self, action):
        pass


class ZShellTabWidget(QtWidgets.QTabWidget):

    def __init__(self, main_win, parent=None):
        super(ZShellTabWidget, self).__init__(parent)
        self.main_win = main_win
        self.setTabsClosable(True)
        self.setUpdatesEnabled(True)
        self._setup_right_corner_button()
        self._setup_signal()
        self._setup_right_click_menu()
        self.is_close = False
        # self.test()

    def test(self):
        self.tab_create(ZShellTab)
        self.tab_create(ZShellTab)
        self.tab_create(ZShellTab)
        self.tab_create(ZShellTab)
        self.tab_create(ZShellTab)

    def _setup_right_corner_button(self):
        self.list_tabs_button = QtWidgets.QToolButton(self)
        self.list_tabs_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.list_tabs_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogYesButton))
        self.setCornerWidget(self.list_tabs_button)
        self.list_tabs_menu = ListTabMenu(self)
        self.list_tabs_button.setMenu(self.list_tabs_menu)

    def _setup_right_click_menu(self):
        self.tabBar().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tabBar().customContextMenuRequested.connect(self._right_click_menu)

    def get_list_tabs_menu(self):
        return self.list_tabs_menu

    def _right_click_menu(self, position):
        index = self.tabBar().tabAt(position)
        widget = self.widget(index)
        menu = widget.get_right_click_menu()
        if not menu:
            return
        action = menu.exec_(self.tabBar().mapToGlobal(position))
        return widget.deal_right_click_action(action)

    def _setup_signal(self):
        self.currentChanged.connect(self.tab_changed)
        self.tabCloseRequested.connect(self.tab_closed)

    def tab_changed(self, dst_index):
        try:
            if self.is_close:
                return
            cur_index = self.currentIndex()
            cur_widget = self.widget(cur_index)
            dst_widget = self.widget(dst_index)
            if cur_widget:
                cur_widget.leave_action()
            if dst_widget:
                dst_widget.enter_action()
        except:
            traceback.print_exc()

    def _tab_close(self, index):
        try:
            delete_widget = self.widget(index)
            if delete_widget:
                delete_widget.close_action()
                delete_widget.deleteLater()
        except:
            traceback.print_exc()

    def tab_closed(self, index):
        self._tab_close(index)
        try:
            self.removeTab(index)
            self.list_tabs_menu.remove_action(index)
            self.flush_index()
        except:
            traceback.print_exc()

    def tab_create(self, tab_cls, index=None, **kwargs):
        if not index:
            index = self.count()

        tab_widget = tab_cls(index, self, **kwargs)
        self.insertTab(index, tab_widget, tab_widget.gen_tab_name())
        self.list_tabs_menu.insert_action(index, tab_widget.get_tab_list_action())
        self.flush_index()
        return tab_widget

    def closeEvent(self, event):
        self.is_close = True
        for i in range(self.count() - 1, -1, -1):
            try:
                self._tab_close(i)
            except:
                pass

    def flush_index(self):
        for i in range(0, self.count()):
            self.widget(i).update_index(i)


class TabManagerPlugin(ZShellPlugin):
    name = "TabManager"

    def __init__(self, main_win):
        super(TabManagerPlugin, self).__init__(main_win)

    def _setup_tab_widget(self):
        self.tab_widget = ZShellTabWidget(self.main_win)
        self.add_to_body(self.tab_widget)

    def start(self):
        self._setup_tab_widget()

    def tab_create(self, tab_cls, **kwargs):
        index = None
        if "index" in kwargs:
            index = kwargs.pop('index')
        tab = self.tab_widget.tab_create(tab_cls, index, **kwargs)
        tab.start()

    def get_currnet_tab(self):
        return self.tab_widget.currentWidget()

    def close(self):
        self.tab_widget.close()
