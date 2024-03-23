from PyQt6.QtWidgets import QApplication

from AutoDefineController import AutoDefineController
from AutoDefineView import AutoDefineWindow
from AutoDefineModel import *
import sys

def main():
    AutoDefineApp = QApplication([])
    autodefineWindow = AutoDefineWindow()
    autodefineWindow.show()
    AutoDefineController(model=AutoDefineModel(), view=autodefineWindow)
    sys.exit(AutoDefineApp.exec())

if __name__ == '__main__':
    main()