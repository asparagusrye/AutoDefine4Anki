from PyQt6.QtWidgets import QDialogButtonBox, QMessageBox


class AutoDefineController:
    def __init__(self, model, view):
        self._model = model
        self._view = view
        self._connectSignalsAndSlots()

    def handle_exit_click(self):
        self._view.close()

    def handle_save_click(self):
        try:
            self._model.add_words(self._view.getListOfWord())
            self._model.export_to_csv()

            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Information)  # Set icon to error
            msg_box.setText("Successfully Export Words")
            msg_box.setWindowTitle("Done!")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)  # Only OK button
            msg_box.exec()

        except:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Critical)  # Set icon to error
            msg_box.setText("Something went wrong")
            msg_box.setWindowTitle("Error!")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)  # Only OK button
            msg_box.exec()

    def _connectSignalsAndSlots(self):
        self._view.buttons.button(QDialogButtonBox.StandardButton.Close).clicked.connect(self.handle_exit_click)

        self._view.buttons.button(QDialogButtonBox.StandardButton.Save).clicked.connect(self.handle_save_click)
