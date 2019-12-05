from PyQt5 import QtWidgets


class ZShellMenubar(QtWidgets.QMenuBar):

    def __init__(self, parent=None):
        super(ZShellMenubar, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.add_file_menu()

    def add_file_menu(self):
        self.file = self.addMenu("文件(F)")

        self.new_connect = QtWidgets.QAction("新建连接", self)
        self.new_connect.setShortcut("Ctrl+N")  # 设置快捷键
        self.file.addAction(self.new_connect)

        self.new_folder = QtWidgets.QAction("新建目录", self)
        self.new_folder.setShortcut("Ctrl+Shift+N")  # 设置快捷键
        self.file.addAction(self.new_folder)
