import pyblish.api

from maya import cmds
from openpype.pipeline.publish import context_plugin_should_run


class ValidateCurrentRenderIsDefaultLayer(pyblish.api.ContextPlugin):
    """Validate if current render layer is the default/master layer"""

    label = "Current Render Layer Is The Default Layer"
    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    families = ["renderlayer"]

    def process(self, context):

        # Workaround bug pyblish-base#250
        if not context_plugin_should_run(self, context):
            return

        current_layer = cmds.editRenderLayerGlobals(query=True, currentRenderLayer=True)
        
        #assert current_layer == "defaultLayer", 