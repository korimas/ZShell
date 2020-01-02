from zshell.plugin.base import ZShellPlugin
from PyQt5 import QtCore, QtWidgets, QtGui
from zshell.core.manage import PluginManager
import os


class WinScpPlugin(ZShellPlugin):
    name = "WinScp"

    def __init__(self, main_win):
        super(WinScpPlugin, self).__init__(main_win)
        self.upload_window = None

    def start(self):
        self._setup_toolbar()

    def _setup_toolbar(self):
        self.winscp_button = QtWidgets.QToolButton()
        self.winscp_button.setToolTip('启动WinSCP')
        self.winscp_button.setIcon(QtGui.QIcon('resources/winscp.ico'))
        self.add_to_toolbar(self.winscp_button)

        self.winscp_button.clicked.connect(self.start_winscp)

    def start_winscp_process(self, host_info):
        program = "%s/resources/winscp.exe" % os.path.abspath('.')
        arguments = [
            "sftp://{0}:{1}@{2}:{3}".format(host_info['user'], host_info['password'], host_info['host'],
                                            host_info['port'])
        ]
        self.winscp_process = QtCore.QProcess()
        self.winscp_process.startDetached(program, arguments)

    def start_winscp(self):
        try:
            tab_manager_plugin = PluginManager().get_plugin("TabManager")
            widget = tab_manager_plugin.get_currnet_tab()
            if hasattr(widget, "host_info") and widget.host_info.get("protocol") in ['ssh']:
                host_info = widget.host_info
                self.start_winscp_process(host_info)
            else:
                self.box_info("当前标签页不支持启动WinSCP")
        except:
            pass
