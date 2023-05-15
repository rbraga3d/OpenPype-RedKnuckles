from pprint import pprint
from qtpy import QtWidgets, QtCore, QtGui

from openpype.client import (
    get_projects,
    get_doc_by_filter,
    get_docs_by_filter,

)

from .lib import (
    get_project_names,
    get_shots_data
)


class ProjectsModel(QtCore.QAbstractListModel):
    COLUMN_COUNT = 1


    def __init__(self, parent=None):
        super(ProjectsModel, self).__init__(parent)
        self._project_names = get_project_names()


    def rowCount(self, parent=None):
        return len(self._project_names)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row = index.row()

        if role == QtCore.Qt.DisplayRole:
            return "{}".format(self._project_names[row])

    def update_data(self, index):
        self.dataChanged.emit(index, index)


class ShotsModel(QtCore.QAbstractListModel):

    def __init__(self, parent=None):
        super(ShotsModel, self).__init__(parent)
        self._shots_names = []
        self._project_name = None

    def rowCount(self, parent=None):
        return len(self._shots_names)


    def data(self, index, role=QtCore.Qt.DisplayRole):
        row = index.row()

        if role == QtCore.Qt.DisplayRole:
            return "{}".format(self._shots_names[row]) or ""

        if role == QtCore.Qt.UserRole:
            return {"project_name": self._project_name}

    def update_data(self, index):
        self._project_name = index.data()
        shot_names = []
        for shot_data in get_shots_data(self._project_name):
            shot_names.append(shot_data["name"])

        self._shots_names = shot_names
        self.dataChanged.emit(index, index)


class ScenesModel(QtCore.QAbstractListModel):

    def __init__(self, parent=None):
        super(ScenesModel, self).__init__(parent)
        self._work_files = []

    def rowCount(self, parent=None):
        return len(self._work_files)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row = index.row()

        if role == QtCore.Qt.DisplayRole:
            return "{}".format(self._work_files[row]["name"])

    def update_data(self, index):
        shot_name = index.data()
        workfiles = []
        file_path_path = []
        project_name = index.data(QtCore.Qt.UserRole)["project_name"]
        shots_data = get_shots_data(project_name)

        for data in shots_data:
            if data["name"] == shot_name:
                for workfile in data["workfiles"]:
                    workfiles.append(workfile)

        self._work_files = workfiles
        self.dataChanged.emit(index, index)
