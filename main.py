import sys
from PyQt6.QtWidgets import QApplication
from ui.mainwindow import MainWindow
from controller.maincontroller import MainController


def main():
    app = QApplication(sys.argv)

    win = MainWindow()
    controller = MainController(win)      # ⬅ keep a variable (or attach to win)
    win.controller = controller           # optional: tie lifetime to the window

    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
