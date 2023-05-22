import os

import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds

import pyblish.api

from openpype.lib import Logger
from openpype.pipeline.publish.lib import remote_publish


class Publisher:

    def __init__(self):
         self._log = Logger.get_logger(__name__)
         self._register_callbacks()

    def _register_callbacks(self):
        pyblish.api.register_callback("published", self._on_published)

    def _deregister_callbacks(self):
        pyblish.api.deregister_callback("published", self._on_published)

    def _on_published(self, context):
        self._deregister_callbacks()


    def publish_on_farm(self):
        last_workfile = os.environ.get('AVALON_LAST_WORKFILE')
        workdir = os.environ.get('AVALON_WORKDIR')

        cmds.workspace(workdir, o=True )
        cmds.file(last_workfile, o=True, force=True)


        remote_publish(self._log, raise_error=True)
