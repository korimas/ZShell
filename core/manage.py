from zshell.common.utils import Singleton
from PyQt5 import QtWidgets


class PluginManager(Singleton):

    def __init__(self):
        self.plugin_dict = {}
        self.main_win = None

    def set_main_win(self, main_win):
        self.main_win = main_win

    def start_plugins(self, plugins):
        for plugin_cls in plugins:
            if plugin_cls.name:
                print("start {0}".format(plugin_cls.name))
                plugin_obj = plugin_cls(self.main_win)
                plugin_obj.start()
                self.plugin_dict[plugin_cls.name] = plugin_obj

            else:
                QtWidgets.QMessageBox.warning(self.main_win, "warning", "插件名称不能为空。")

    def get_plugin(self, name):
        return self.plugin_dict.get(name)

    def close(self):
        for key, value in self.plugin_dict.items():
            try:
                value.close()
            except:
                pass
