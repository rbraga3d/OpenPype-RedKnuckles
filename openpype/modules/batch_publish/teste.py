import os

import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds

import pyblish.api

def exe_script():


        from openpype.lib import Logger
        from openpype.pipeline.publish.lib import remote_publish

        #Registar callbacks for when publish is done
        pyblish.api.register_callback("published", on_published)


        log = Logger.get_logger(__name__)
        remote_publish(log, raise_error=True)


def on_published(context):
      print("AEEEEEEEEEEEEEEEEEEEEEEEEE PUBLICADO A DESGRACA!")
      pyblish.api.deregister_callback(on_published)

def run():
    last_workfile = os.environ.get('AVALON_LAST_WORKFILE')
    workdir = os.environ.get('AVALON_WORKDIR')

    cmds.workspace(workdir, o=True )
    cmds.file(last_workfile, o=True, force=True)


    exe_script()
