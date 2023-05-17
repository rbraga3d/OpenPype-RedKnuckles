"""
The main dialog (BatchPublishAddon) was copied
from the main Launcher window class.
.openpype/tools/launcher/window.py

"""

import copy
import logging

from qtpy import QtWidgets, QtCore, QtGui

from openpype import style
from openpype import resources
from openpype.pipeline import AvalonMongoDB

import qtawesome
from openpype.tools.launcher.models import (
    LauncherModel,
    ProjectModel
)
from openpype.tools.launcher.lib import get_action_label

from openpype.tools.launcher.widgets import (
    ProjectBar,
    ActionBar,
    ActionHistory,
    SlidePageWidget,
    LauncherAssetsWidget,
    LauncherTaskWidget
)
from openpype.tools.launcher.window import (
    ProjectsPanel,
    AssetsPanel
)


from openpype.tools.flickcharm import FlickCharm



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
    """Launcher interface"""
    message_timeout = 5000

    def __init__(self, parent=None):
        super(BatchPublishDialog, self).__init__(parent)

        self.log = logging.getLogger(
            ".".join([__name__, self.__class__.__name__])
        )

        self.dbcon = AvalonMongoDB()

        self.setWindowTitle(WINDOW_TITLE)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)

        icon = QtGui.QIcon(resources.get_openpype_icon_filepath())
        self.setWindowIcon(icon)
        self.setStyleSheet(style.load_stylesheet())

        # Allow minimize
        self.setWindowFlags(
            QtCore.Qt.Window
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowMinimizeButtonHint
            | QtCore.Qt.WindowCloseButtonHint
        )

        launcher_model = LauncherModel(self.dbcon)

        project_panel = ProjectsPanel(launcher_model)
        asset_panel = AssetsPanel(launcher_model, self.dbcon)

        page_slider = SlidePageWidget()
        page_slider.addWidget(project_panel)
        page_slider.addWidget(asset_panel)


        # actions
        actions_bar = ActionBar(launcher_model, self.dbcon, self)

        # statusbar
        message_label = QtWidgets.QLabel(self)

        action_history = ActionHistory(self)
        action_history.setStatusTip("Show Action History")

        status_layout = QtWidgets.QHBoxLayout()
        status_layout.addWidget(message_label, 1)
        status_layout.addWidget(action_history, 0)

        # Vertically split Pages and Actions
        body = QtWidgets.QSplitter(self)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )
        body.setOrientation(QtCore.Qt.Vertical)
        body.addWidget(page_slider)
        body.addWidget(actions_bar)

        # Set useful default sizes and set stretch
        # for the pages so that is the only one that
        # stretches on UI resize.
        body.setStretchFactor(0, 10)
        body.setSizes([580, 160])

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(body)
        layout.addLayout(status_layout)

        message_timer = QtCore.QTimer()
        message_timer.setInterval(self.message_timeout)
        message_timer.setSingleShot(True)

        message_timer.timeout.connect(self._on_message_timeout)

        # signals
        actions_bar.action_clicked.connect(self.on_action_clicked)
        action_history.trigger_history.connect(self.on_history_action)
        launcher_model.project_changed.connect(self.on_project_change)
        launcher_model.timer_timeout.connect(self._on_refresh_timeout)
        asset_panel.back_clicked.connect(self.on_back_clicked)
        asset_panel.session_changed.connect(self.on_session_changed)

        self.resize(520, 740)

        self._page = 0

        self._message_timer = message_timer

        self._launcher_model = launcher_model

        self._message_label = message_label
        self.project_panel = project_panel
        self.asset_panel = asset_panel
        self.actions_bar = actions_bar
        self.action_history = action_history
        self.page_slider = page_slider

    def showEvent(self, event):
        self._launcher_model.set_active(True)
        self._launcher_model.start_refresh_timer(True)

        super(BatchPublishDialog, self).showEvent(event)

    def _on_refresh_timeout(self):
        # Stop timer if widget is not visible
        if not self.isVisible():
            self._launcher_model.stop_refresh_timer()

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.ActivationChange:
            self._launcher_model.set_active(self.isActiveWindow())
        super(BatchPublishDialog, self).changeEvent(event)

    def set_page(self, page):
        current = self.page_slider.currentIndex()
        if current == page and self._page == page:
            return

        direction = "right" if page > current else "left"
        self._page = page
        self.page_slider.slide_view(page, direction=direction)

    def _on_message_timeout(self):
        self._message_label.setText("")

    def echo(self, message):
        self._message_label.setText(str(message))
        self._message_timer.start()
        self.log.debug(message)

    def on_session_changed(self):
        self.filter_actions()

    def discover_actions(self):
        self.actions_bar.discover_actions()

    def filter_actions(self):
        self.actions_bar.filter_actions()

    def on_project_change(self, project_name):
        # Update the Action plug-ins available for the current project
        self.set_page(1)
        self.discover_actions()

    def on_back_clicked(self):
        self._launcher_model.set_project_name(None)
        self.set_page(0)
        self.discover_actions()

    def on_action_clicked(self, action):
        self.echo("Running action: {}".format(get_action_label(action)))
        self.run_action(action)

    def on_history_action(self, history_data):
        action, session = history_data
        app = QtWidgets.QApplication.instance()
        modifiers = app.keyboardModifiers()

        is_control_down = QtCore.Qt.ControlModifier & modifiers
        if is_control_down:
            # Revert to that "session" location
            self.set_session(session)
        else:
            # User is holding control, rerun the action
            self.run_action(action, session=session)

    def run_action(self, action, session=None):
        if session is None:
            session = copy.deepcopy(self.dbcon.Session)

        filtered_session = {
            key: value
            for key, value in session.items()
            if value
        }
        # Add to history
        self.action_history.add_action(action, filtered_session)

        # Process the Action
        try:
            action().process(filtered_session)
        except Exception as exc:
            self.log.warning("Action launch failed.", exc_info=True)
            self.echo("Failed: {}".format(str(exc)))

    def set_session(self, session):
        project_name = session.get("AVALON_PROJECT")
        asset_name = session.get("AVALON_ASSET")
        task_name = session.get("AVALON_TASK")

        if project_name:
            # Force the "in project" view.
            self.page_slider.slide_view(1, direction="right")
            index = self.asset_panel.project_bar.project_combobox.findText(
                project_name
            )
            if index >= 0:
                self.asset_panel.project_bar.project_combobox.setCurrentIndex(
                    index
                )

        if asset_name:
            self.asset_panel.select_asset(asset_name)

        if task_name:
            # requires a forced refresh first
            self.asset_panel.select_task_name(task_name)
