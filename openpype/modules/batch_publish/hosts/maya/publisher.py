import os
import socket

# from pymel.core import * # Same as maya.standalone.initialize() but
#                          # with more funcionalities when running mayapy
#                          # More detailes on:
#                          # https://help.autodesk.com/cloudhelp/2017/ENU/Maya-Tech-Docs/PyMel/standalone.html

import maya.cmds as cmds

import pyblish.api

from openpype.lib import Logger
from openpype.pipeline.publish.lib import remote_publish
from openpype.hosts.maya.api.lib import get_frame_range
from openpype.pipeline.load import (
    get_outdated_containers,
    update_container
)

from ...constants import(
    PUBLISH_FAILED,
    PUBLISH_SUCCESS
)


class Publisher:

    def __init__(self):

        self._log = Logger.get_logger(__name__)
        self._register_callbacks()
        self._socket_client = None


    def _init_callbacks_client(self):
        host = socket.gethostbyname("localhost")
        port = 9999

        socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_client.connect((host, port))

        self._socket_client = socket_client



    def send_message_to_server(self, message, log=False):
        #TODO: Refactor - Convert to send_data_to_server
        msg = message.encode()
        self._socket_client.sendall(msg)

        if log:
            self._log.info(message)


    def _register_callbacks(self):
        pyblish.api.register_callback("published", self._on_published)
        pyblish.api.register_callback("publish_error", self._on_publish_error)


    def _on_published(self, context):
        self._log.info("Published! Sent to farm.")
        self.send_message_to_server(PUBLISH_SUCCESS)
        pyblish.api.deregister_all_callbacks()

    def _on_publish_error(self, context, error_message):
        print("ERROR_MESSAGE = ", error_message)
        msg_error = "{} - {}".format(PUBLISH_FAILED, error_message)
        self.send_message_to_server(msg_error)

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

    def _set_project(self):
        workdir = os.environ.get('AVALON_WORKDIR')
        cmds.workspace(workdir, o=True )

    def _prepare_scene(self):
        msg = "Preparing scene -> STARTING..."
        self.send_message_to_server(msg)

        msg = "Preparing scene -> Updating outdated assets to latest versions..."
        self.send_message_to_server(msg)
        self._update_assets_to_latest()

        msg = "Preparing scene -> Enabling instances farm attribute..."
        self.send_message_to_server(msg)
        self._enable_instances_farm_attribute()

        msg = "Preparing scene -> Fixing instances frame ranges..."
        self.send_message_to_server(msg)
        self._fix_instances_frame_range()


    def publish_on_farm(self):
        self._init_callbacks_client()
        self._set_project()
        self._prepare_scene()


        msg = "Running validations...\n"
        self.send_message_to_server(msg)

        def _remote_publish():
            remote_publish(self._log, raise_error=True)

        # Run remote publish
        cmds.evalDeferred(_remote_publish)
