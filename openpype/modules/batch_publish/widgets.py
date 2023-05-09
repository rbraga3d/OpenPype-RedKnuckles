from qtpy import QtWidgets, QtCore, QtGui

from openpype.pipeline import AvalonMongoDB
from openpype.style import load_stylesheet


class ListPanel(QtWidgets.QWidget):
    def __init__(self, title, parent=None):
        super(ListPanel, self).__init__(parent)

        self._title = QtWidgets.QLabel(title)
        self._list_view = QtWidgets.QListView()

        # ----- Layouts ----- #
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._title)
        main_layout.addWidget(self._list_view)
        self.setLayout(main_layout)

        # ----- Style Sheets ----- #
        #self.setStyleSheet(load_stylesheet())




class BatchPublishDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(BatchPublishDialog, self).__init__(parent)

        self.setWindowTitle("Batch Publish")

        self._create_widgets()
        self._create_layouts()
        self._create_connections()
        self._set_style_sheet()

        # Allow minimize
        self.setWindowFlags(
            QtCore.Qt.Window
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowMinimizeButtonHint
            | QtCore.Qt.WindowCloseButtonHint
        )



    def _create_widgets(self):

        # ---- List Widgets ---- #
        self._projects_list_view = ListPanel("Projects")
        self._shots_list_view = ListPanel("Shots")
        self._scenes_list_view = ListPanel("Scenes")

        # ---- Buttons ---- #
        self._cancel_btn = QtWidgets.QPushButton("Cancel")
        self._publish_cache_btn = QtWidgets.QPushButton("Publish Cache")




    def _create_layouts(self):

        # ---- List Widgets ---- #
        list_widgets_layout = QtWidgets.QHBoxLayout()
        list_widgets_layout.addWidget(self._projects_list_view)
        list_widgets_layout.addWidget(self._shots_list_view)
        list_widgets_layout.addWidget(self._scenes_list_view)

        # ---- Buttons ---- #
        main_buttons_layout = QtWidgets.QHBoxLayout()
        main_buttons_layout.addWidget(self._cancel_btn)
        main_buttons_layout.addWidget(self._publish_cache_btn)


        # ----- Main ----- #
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(list_widgets_layout)
        main_layout.addLayout(main_buttons_layout)


    def _create_connections(self):
        pass


    def _set_style_sheet(self):
        self.setStyleSheet(load_stylesheet())

    def _on_ok_clicked(self):
        self.done(1)
