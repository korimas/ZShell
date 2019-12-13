from PyQt5 import QtWidgets, QtGui, QtCore


# class ZShellToolBar(QtWidgets.QToolBar):
#
#     def __init__(self, main_win):
#         super(ZShellToolBar, self).__init__()
#         self.main_win = main_win
#         self.setFixedHeight(23)


class ZShellToolBar(QtWidgets.QWidget):

    def __init__(self, main_win):
        super(ZShellToolBar, self).__init__()
        self.main_win = main_win
        self._setup_layout()

    def _setup_layout(self):
        self.layout_h = QtWidgets.QHBoxLayout()
        self.layout_h.setContentsMargins(0, 0, 0, 0)
        self.layout_h.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.setLayout(self.layout_h)

        # self.toolbar_button = QtWidgets.QToolButton()
        # self.toolbar_button.setToolTip('会话管理')
        # self.toolbar_button.setIcon(self.toolbar_button.style().standardIcon(QtWidgets.QStyle.SP_DialogYesButton))
        # self.toolbar_button.setPopupMode(self.toolbar_button.MenuButtonPopup)
        # self.toolbar_button.clicked.connect(self.show_session_manager)
        # self.addWidget(widget=self.toolbar_button)

    #
    # def show_session_manager(self):
    #     print("show")

    def addWidget(self, widget):
        # widget.setParent(self)
        self.layout_h.addWidget(widget)
