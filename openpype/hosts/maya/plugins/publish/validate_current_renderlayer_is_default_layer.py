import pyblish.api

from maya import cmds
from openpype.pipeline.publish import context_plugin_should_run


class ValidateCurrentRenderIsDefaultLayer(pyblish.api.ContextPlugin):
    """Validates if the current render layer is the default/master layer."""

    label = "Current Render Layer Is The Default Layer"
    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    families = ["renderlayer"]

    def process(self, context):

        # Workaround bug pyblish-base#250
        if not context_plugin_should_run(self, context):
            return

        current_layer = cmds.editRenderLayerGlobals(query=True, currentRenderLayer=True)
        failed_message = "The current render layer is not the default/master layer. \n"
        assert current_layer == "defaultRenderLayer", failed_message