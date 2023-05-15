from qtpy import QtWidgets, QtCore, QtGui

from .models import (
    ProjectsModel,
    ShotsModel,
    ScenesModel
)

class ProjectsView(QtWidgets.QListView):

    projectChanged = QtCore.Signal(QtCore.QModelIndex)

    def __init__(self, parent=None):
        super(ProjectsView, self).__init__(parent)

        self.model = ProjectsModel()
        self.setModel(self.model)

        #Connections
        self.clicked.connect(self.on_clicked)


    def on_clicked(self, index):
        self.projectChanged.emit(index)


class ShotsView(QtWidgets.QListView):

    shotChanged = QtCore.Signal(QtCore.QModelIndex)

    def __init__(self, parent=None):
        super(ShotsView, self).__init__(parent)

        self.model = ShotsModel()
        self.setModel(self.model)


        #Connections
        self.clicked.connect(self.on_clicked)

    def on_clicked(self, index):
        self.shotChanged.emit(index)


class ScenesView(QtWidgets.QListView):

    def __init__(self, parent=None):
        super(ScenesView, self).__init__(parent)

        self.model = ScenesModel()
        self.setModel(self.model)
