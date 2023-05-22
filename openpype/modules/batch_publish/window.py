import copy
import logging

from qtpy import QtWidgets, QtCore, QtGui
import qtawesome

from openpype import style
from openpype import resources
from openpype.pipeline import AvalonMongoDB

from openpype.tools.flickcharm import FlickCharm

# ----- Imported from launcher app ----- #
from openpype.tools.launcher.models import (
    LauncherModel,

)
from openpype.tools.launcher.lib import get_action_label
from openpype.tools.launcher.widgets import (
    ActionBar,
    ActionHistory,
    SlidePageWidget,

)
from openpype.tools.launcher.window import (
    ProjectsPanel,
    AssetsPanel

)


# ---------------------------------------#
from .app import BatchPublish
from .log_console.widgets import ConsoleWidget, LogThread


class BatchPublishDialog(QtWidgets.QDialog):
    """Launcher interface"""
    message_timeout = 5000

    def __init__(self, parent=None):
        super(BatchPublishDialog, self).__init__(parent)


        self.log = logging.getLogger(
            ".".join([__name__, self.__class__.__name__])
        )
        self.dbcon = AvalonMongoDB()

        self.setWindowTitle("Batch Publish on Farm (beta)")
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

        # Main action button
        main_action_btn = QtWidgets.QPushButton("Batch Publish on Farm")
        main_action_btn.setFixedHeight(50)

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
        body.addWidget(main_action_btn)
        #body.addWidget(actions_bar)

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
        main_action_btn.clicked.connect(self.on_main_clicked)
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
        for key,value in session.items():
            print("{} = {}".format(key, value))


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


    def on_main_clicked(self):
        self._run_batch_publish()


    def _run_batch_publish(self):

        batch_publish_app = BatchPublish()
        batch_publish_app.publish(self.dbcon.Session)
