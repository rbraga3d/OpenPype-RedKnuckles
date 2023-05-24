import os

import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds

import pyblish.api

from openpype.lib import Logger
from openpype.pipeline.publish.lib import remote_publish
from openpype.hosts.maya.api.lib import get_frame_range
from openpype.pipeline.load import (
    get_outdated_containers,
    update_container
)

class Publisher:

    def __init__(self):

        self._log = Logger.get_logger(__name__)
        self._register_callbacks()

    def _register_callbacks(self):
        pyblish.api.register_callback("published", self._on_published)

    def _deregister_callbacks(self):
        pyblish.api.deregister_callback("published", self._on_published)

    def _on_published(self, context):
        self._log.info("Published!")
        self._deregister_callbacks()


    def _get_instances(self):
        """Return all instances from scene.

        This returns list of instance sets

        Returns:
            list: list of instances

        """
        objectset = cmds.ls("*.id", long=True, type="objectSet",
                            recursive=True, objectsOnly=True)

        instances = []
        for objset in objectset:
            if not cmds.attributeQuery("id", node=objset, exists=True):
                continue

            id_attr = "{}.id".format(objset)
            if cmds.getAttr(id_attr) != "pyblish.avalon.instance":
                continue

            has_family = cmds.attributeQuery("family",
                                            node=objset,
                                            exists=True)
            if not has_family:
                continue

            instances.append(objset)

            #if cmds.getAttr(
                    #"{}.family".format(objset)) in "pointcache":
                #instances.append(objset)

        return instances


    def _has_farm_attr(self, instance):
        return cmds.attributeQuery("farm", node=instance, exists=True)

    def _has_frame_range_attrs(self, instance):
        if cmds.attributeQuery("frameStart", node=instance, exists=True) \
        and cmds.attributeQuery("frameEnd", node=instance, exists=True):
            return True

        return False

    def _enable_instances_farm_attribute(self):
        instances = self._get_instances()
        for instance in instances:
            if self._has_farm_attr(instance):
                cmds.setAttr(instance+".farm", True)


    def _fix_instances_frame_range(self):
        instances = self._get_instances()
        for instance in instances:
            has_animation = self._has_frame_range_attrs(instance)
            if has_animation:
                correct_frame_range = get_frame_range()
                cmds.setAttr(instance+".frameStart", correct_frame_range["frameStart"])
                cmds.setAttr(instance+".frameEnd", correct_frame_range["frameEnd"])
                cmds.setAttr(instance+".handleStart", correct_frame_range["handleStart"])
                cmds.setAttr(instance+".handleEnd", correct_frame_range["handleEnd"])



    def _update_assets_to_latest(self):
        outdated_containers = get_outdated_containers()
        if outdated_containers:
            for container in outdated_containers:
                update_container(container)


    def _add_farm_attr_to_all(self):
        ...

    def _open_last_workfile(self):
        last_workfile = os.environ.get('AVALON_LAST_WORKFILE')
        workdir = os.environ.get('AVALON_WORKDIR')

        cmds.workspace(workdir, o=True )
        cmds.file(last_workfile, o=True, force=True)

    def _prepare_scene(self):
        self._log.info("Preparing scene -> STARTING...")
        self._log.info("Preparing scene -> Updating outdated assets to latest versions...")
        self._update_assets_to_latest()

        self._log.info("Preparing scene -> Enabling instances farm attribute...")
        self._enable_instances_farm_attribute()

        self._log.info("Preparing scene -> Fixing instances frame ranges...")
        self._fix_instances_frame_range()

        self._log.info("Preparing scene -> DONE!")

    def publish_on_farm(self):

        self._open_last_workfile()
        self._prepare_scene()


        def _remote_publish():
            remote_publish(self._log, raise_error=True)

        cmds.evalDeferred(_remote_publish)
