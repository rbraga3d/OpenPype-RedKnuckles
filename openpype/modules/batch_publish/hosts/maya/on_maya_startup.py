"""
This file script will be called after mayabatch is loaded.
It is passed as a -command argument to the maya executable.
"""


import maya.cmds as cmds
from openpype.modules.batch_publish.hosts.maya import Publisher
publisher = Publisher()
cmds.evalDeferred(publisher.publish_on_farm)
