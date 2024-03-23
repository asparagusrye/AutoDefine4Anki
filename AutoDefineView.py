from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget, QBoxLayout, QFormLayout, QTextEdit, QDialogButtonBox, QHBoxLayout, QLabel, QGroupBox,
)

import sys


class AutoDefineWindow(QMainWindow):
    WINDOW_SIZE = 720

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCalc")
        self.setFixedSize(AutoDefineWindow.WINDOW_SIZE, AutoDefineWindow.WINDOW_SIZE)
        self.generalLayout = QVBoxLayout()
        self.generalLayout.setContentsMargins(20, 20, 20, 20)
        centralWidget = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        self.setCentralWidget(centralWidget)
        self._createDisplay()

    def _createDisplay(self):
        self.generalLayout.addWidget(QLabel("Keywords"))
        self.generalLayout.addWidget(QTextEdit())
        self.buttons = QDialogButtonBox()
        self.buttons.setStandardButtons(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Close)
        self.generalLayout.addWidget(self.buttons)

    def getListOfWord(self):
        searchBox = self.generalLayout.itemAt(1).widget()
        if isinstance(searchBox, QTextEdit):
            return searchBox.toPlainText().split("\n")
