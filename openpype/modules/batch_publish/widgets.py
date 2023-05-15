from qtpy import QtWidgets, QtCore, QtGui


from openpype.style import load_stylesheet

from .views import (
    ProjectsView,
    ShotsView,
    ScenesView
)


WINDOW_TITLE = "Batch Publish (beta)"
PROJECTS_TITLE = "Projects"
SHOTS_TITLE = "Shots"
SCENES_TITLE = "Scenes"


class ListPanel(QtWidgets.QWidget):
    def __init__(self, title="Title", parent=None):
        super(ListPanel, self).__init__(parent)

        self._title = title
        self.title_label = QtWidgets.QLabel(self._title)

        # ----- Layouts ----- #
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.title_label)
        self.setLayout(main_layout)

    def fill_list(self, items):
        if items:
            self.list_view.addItems(items)

    def _set_view(self, view):
        self.layout().addWidget(view)



class ProjectListPanel(ListPanel):
    def __init__(self, parent=None):
        super(ProjectListPanel,self).__init__(parent)

        self.title_label.setText(PROJECTS_TITLE)
        self.view = ProjectsView()

        self._set_view(self.view)


class ShotsListPanel(ListPanel):
    def __init__(self, parent=None):
        super(ShotsListPanel,self).__init__(parent)

        self.title_label.setText(SHOTS_TITLE)
        self.view = ShotsView()

        self._set_view(self.view)


class ScenesListPanel(ListPanel):
    def __init__(self, parent=None):
        super(ScenesListPanel,self).__init__(parent)

        self.title_label.setText(SCENES_TITLE)
        self.view = ScenesView()

        self._set_view(self.view)



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


    def _create_widgets(self):


        # ---- Panels with views ---- #
        self._projects_panel = ProjectListPanel()
        self._shots_panel = ShotsListPanel()
        self._scenes_panel = ScenesListPanel()

        # ---- Buttons ---- #
        self._cancel_btn = QtWidgets.QPushButton("Cancel")
        self._publish_cache_btn = QtWidgets.QPushButton("Publish Cache")


    def _create_layouts(self):

        # ---- List Widgets ---- #
        list_widgets_layout = QtWidgets.QHBoxLayout()
        list_widgets_layout.addWidget(self._projects_panel)
        list_widgets_layout.addWidget(self._shots_panel)
        list_widgets_layout.addWidget(self._scenes_panel)

        # ---- Buttons ---- #
        main_buttons_layout = QtWidgets.QHBoxLayout()
        main_buttons_layout.addWidget(self._cancel_btn)
        main_buttons_layout.addWidget(self._publish_cache_btn)


        # ----- Main ----- #
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(list_widgets_layout)
        main_layout.addLayout(main_buttons_layout)


    def _create_connections(self):
        self._projects_panel.view.projectChanged.connect(
            self._shots_panel.view.model.update_data
        )

        self._shots_panel.view.shotChanged.connect(
            self._scenes_panel.view.model.update_data
        )


    def _set_style_sheet(self):
        self.setStyleSheet(load_stylesheet())

    def _on_ok_clicked(self):
        self.done(1)
