from pprint import pprint
from qtpy import QtWidgets, QtCore, QtGui

from openpype.pipeline import AvalonMongoDB
from openpype.client import (
    get_projects,
    get_docs_by_filter
)
from openpype.style import load_stylesheet

WINDOW_TITLE = "Batch Publish (beta)"
PROJECTS_TITLE = "Projects"
SHOTS_TITLE = "Shots"
SCENES_TITLE = "Scenes"

class ListPanel(QtWidgets.QWidget):
    def __init__(self, title="Title", parent=None):
        super(ListPanel, self).__init__(parent)

        self._title = title
        self.title_label = QtWidgets.QLabel(self._title)
        self.list_view = QtWidgets.QListWidget()

        # ----- Layouts ----- #
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.list_view)
        self.setLayout(main_layout)

    def fill_list(self, items):
        if items:
            self.list_view.addItems(items)

class ProjectListPanel(ListPanel):
    def __init__(self, dbcon, parent=None):
        super(ProjectListPanel,self).__init__(parent)
        self._dbcon = dbcon
        self.title_label.setText(PROJECTS_TITLE)

        shots = get_docs_by_filter("Development", {'data.entityType':'Shot'})
        for shot in shots:
            print(shot["name"])





    def get_projects_list(self):
        projects_name = []
        for project in self._dbcon.projects():
            projects_name.append(project["name"])
        return projects_name

    def fill_project_list(self):
        self.fill_list(self.get_projects_list())


class ShotsListPanel(ListPanel):
    def __init__(self, parent=None):
        super(ShotsListPanel,self).__init__(parent)
        self.title_label.setText(SHOTS_TITLE)

class ScenesListPanel(ListPanel):
    def __init__(self, parent=None):
        super(ScenesListPanel,self).__init__(parent)
        self.title_label.setText(SCENES_TITLE)




class BatchPublishDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(BatchPublishDialog, self).__init__(parent)

        self.setWindowTitle(WINDOW_TITLE)
        self._dbcon = AvalonMongoDB()

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
        self._projects_list_view = ProjectListPanel(self._dbcon)
        self._shots_list_view = ShotsListPanel()
        self._scenes_list_view = ScenesListPanel()

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
