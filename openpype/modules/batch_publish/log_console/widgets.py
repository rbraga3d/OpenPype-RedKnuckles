import sys
from qtpy import QtWidgets
from qtpy import QtCore
from qtpy import QtGui
# from PyQt5.QtWidgets import QApplication, QMainWindow, QPlainTextEdit
# from PyQt5.QtCore import Qt, QThread, pyqtSignal
# from PyQt5.QtGui import QTextCursor
class LogThread(QtCore.QThread):
    log_updated = QtCore.Signal(str)

    def run(self):
        while True:
            line = sys.stdin.readline()
            self.log_updated.emit(line)


class ConsoleWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ConsoleWidget, self).__init__(parent)

        self._interpreter_window = None
        self._log_textedit = QtWidgets.QPlainTextEdit(self)


        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self._log_textedit)


    def write(self, text):
        text_cursor = QtGui.QTextCursor(self._log_textedit.document())
        text_cursor.movePosition(QtGui.QTextCursor.End)
        text_cursor.insertText(text)


    def _on_timer_timeout(self, line):
        self.write(line)



    def create_interpreter_window(self):
            """Initializa Settings Qt window."""
            if self._interpreter_window:
                return

            from openpype.modules.python_console_interpreter.window import (
                PythonInterpreterWidget
            )

            self._interpreter_window = PythonInterpreterWidget()

    def on_action_trigger(self):
        self.show_interpreter_window()

    def show_interpreter_window(self):
        self.create_interpreter_window()

        if self._interpreter_window.isVisible():
            self._interpreter_window.activateWindow()
            self._interpreter_window.raise_()
            return

        self._interpreter_window.show()
