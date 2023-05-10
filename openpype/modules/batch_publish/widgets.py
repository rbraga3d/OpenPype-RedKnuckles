"""
This class will be refactored
For now, it's just being used as an addon prototype
"""


from pprint import pprint
from qtpy import QtWidgets, QtCore, QtGui

from openpype.client import (
    get_projects,
    get_whole_project,
    get_doc_by_filter,
    get_docs_by_filter,

)
from openpype.style import load_stylesheet

WINDOW_TITLE = "Batch Publish (beta)"
PROJECTS_TITLE = "Projects"
SHOTS_TITLE = "Shots"
SCENES_TITLE = "Scenes"


def get_shots_data(project_name):
    """Organize shot names and their work files into dicts:
    i.e {"SH001": {
            "files_data": [
                        {
                            "name": 'file_name_v001.ma',
                            "path": '/path/to/file_name_v001.ma'
                        },
                        {
                            "name": 'file_name_v002.ma',
                            "path": '/path/to/file_name_v001.ma'
                        }
                        ]}}

    Args:
        project_name (str): Name of project where to look for.

    Returns:
        List: List with dicts containing shot names and their work files data..
    """
    data = []


    # ----- Get animation tasks ----- #
    mongo_filter = {
        "type":"workfile",
        "task_name":"Animation"
        }
    anim_tasks = get_docs_by_filter(project_name, mongo_filter)
    anim_tasks = list(anim_tasks)

    # ----- Get animation tasks ----- #
    mongo_filter = {
        "data.entityType": "Shot"
    }
    shot_assets = get_docs_by_filter(project_name, mongo_filter)
    shot_names = [shot_asset["name"] for shot_asset in shot_assets]

    # ----- Put all shot files into their respective dict ----- #
    for shot_name in shot_names:
        shot_struct = {}
        shot_struct[shot_name] = {"files_data": []}
        for task in anim_tasks:
            parent_id = task["parent"]
            parent = get_doc_by_filter(project_name, {"_id":parent_id})
            parent_name = parent["name"]

            file_struct = {
                "name": task["filename"],
                "path": task["files"][0]
            }

            if shot_name == parent_name:
                shot_struct[shot_name]["files_data"].append(file_struct)

        data.append(shot_struct)


    return data





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
    def __init__(self, parent=None):
        super(ProjectListPanel,self).__init__(parent)

        self.title_label.setText(PROJECTS_TITLE)
        self.refresh_list()

    def get_project_names(self):
        project_names = []
        for project in get_projects():
            project_names.append(project["name"])
        return project_names

    def refresh_list(self):
        self.fill_list(self.get_project_names())


class ShotsListPanel(ListPanel):
    def __init__(self, parent=None):
        super(ShotsListPanel,self).__init__(parent)
        self.title_label.setText(SHOTS_TITLE)

        self.refresh_list("Development")

    def get_shot_names(self, project_name):
        shot_names = []
        mongo_filter = {'data.entityType':'Shot'}

        shots = get_docs_by_filter(project_name, mongo_filter)
        for shot in shots:
            shot_names.append(shot['name'])

        return shot_names

    def refresh_list(self, project_name):
        self.fill_list(self.get_shot_names(project_name))


class ScenesListPanel(ListPanel):
    def __init__(self, parent=None):
        super(ScenesListPanel,self).__init__(parent)
        self.title_label.setText(SCENES_TITLE)



class BatchPublishDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(BatchPublishDialog, self).__init__(parent)

        self.setWindowTitle(WINDOW_TITLE)

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

        get_shots_data("Development")


    def _create_widgets(self):


        # ---- List Widgets ---- #
        self._projects_list_view = ProjectListPanel()
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
