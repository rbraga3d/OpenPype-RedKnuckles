import os
import subprocess
import copy
import socket

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
        self._mayapy_path = "/usr/autodesk/maya2023/bin/mayapy"




    def publish(self, session):
        """Main method responsable for oepning scene in mayapy
        and publishing to farm """

        # ----- Get current session data ----- #
        session = copy.deepcopy(session)
        project_name = session.get("AVALON_PROJECT")
        asset_name = session.get("AVALON_ASSET")
        task_name = session.get("AVALON_TASK")

        app_name = self._app_name

        install_openpype_plugins()

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

        # ----- Run MayaPy ---- #
        # It will run MayaPy with proper environments
        # and then a command from 'args' list will be executed after
        # maya is open and idle
        mayapy_path = self._mayapy_path
        command = "from openpype.modules.batch_publish.hosts.maya import Publisher; \
        cmds.evalDeferred(Publisher().publish_on_farm)"

        args = (
            mayapy_path,
            "-c",
            command
        )

        subprocess.Popen(args, env=env)
