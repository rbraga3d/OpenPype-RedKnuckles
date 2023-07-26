import os
import copy

from openpype.lib.applications import (
    get_app_environments_for_context,
    ApplicationLaunchContext,
    ApplicationManager
)
from openpype.pipeline import install_openpype_plugins
from openpype.lib import Logger


class BatchPublish:
    def __init__(self):
        self._log = Logger.get_logger("Batch-Publish-Module")
        self._app_name = "maya/2023"


    def publish(self, session):
        """Main method responsable for oepning scene in mayabatch
        and publishing to farm """

        # ----- Get current session data ----- #
        session = copy.deepcopy(session)
        project_name = session.get("AVALON_PROJECT")
        asset_name = session.get("AVALON_ASSET")
        task_name = session.get("AVALON_TASK")
        app_name = self._app_name


        app_manager = ApplicationManager()


        if not app_manager.applications.get(app_name):
            self._log.warning("App not found: {}".format(app_name))
            self._log.info("All valid apps {}".format(list(app_manager.applications.keys())))
            return

        if all([project_name, asset_name, task_name, app_name]):
            env = get_app_environments_for_context(
                project_name, asset_name, task_name, app_name
            )
        else:
            env = os.environ.copy()


        app = app_manager.applications[app_name]
        executable = app.find_executable()


        command = 'python\(\\"from\ openpype.modules.batch_publish.hosts.maya\ import\ on_maya_startup\\"\)'
        arguments = [
            "-batch",
            "-command",
            "'{}'".format(command)        ]
        data = {
                    "project_name": project_name,
                    "asset_name": asset_name,
                    "task_name": task_name,
                    "app_args": arguments,
                    "env": env,
                }
        context = ApplicationLaunchContext(
            app, executable, **data,
        )

        context.launch()
