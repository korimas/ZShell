from zshell.core.app import app, main_win
from zshell.plugin.manager import enable_plugins
import sys

if __name__ == "__main__":
    main_win.start_plugins(enable_plugins)
    main_win.show()
    sys.exit(app.exec_())
