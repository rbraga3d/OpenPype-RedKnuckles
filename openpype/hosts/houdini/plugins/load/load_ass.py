import os

import clique
from openpype.pipeline import (
    load,
    get_representation_path,
)

from openpype.hosts.houdini.api import pipeline


class AssLoader(load.LoaderPlugin):
    """Load .ass with Arnold Procedural"""

    families = ["ass"]
    label = "Load Arnold Procedural"
    representations = ["ass"]
    order = -10
    icon = "code-fork"
    color = "orange"

    def load(self, context, name=None, namespace=None, data=None):

        import hou

        # Get the root node
        obj = hou.node("/obj")

        # Define node name
        namespace = namespace if namespace else context["asset"]["name"]
        node_name = "{}_{}".format(namespace, name) if namespace else name

        # Create a new geo node
        procedural = obj.createNode("arnold::procedural", node_name=node_name)

        procedural.setParms(
            {
                "ar_filename": self.format_path(
                    self.fname, context["representation"])
            })

        nodes = [procedural]
        self[:] = nodes

        return pipeline.containerise(
            node_name,
            namespace,
            nodes,
            context,
            self.__class__.__name__,
            suffix="",
        )

    def update(self, container, representation):

        # Update the file path
        file_path = get_representation_path(representation)
        file_path = self.format_path(file_path, representation)

        procedural = container["node"]
        procedural.setParms({"ar_filename": file_path})

        # Update attribute
        procedural.setParms({"representation": str(representation["_id"])})

    def remove(self, container):

        node = container["node"]
        node.destroy()

    @staticmethod
    def format_path(path, representation):
        """Format file path correctly for single bgeo or bgeo sequence."""
        if not os.path.exists(path):
            raise RuntimeError("Path does not exist: %s" % path)

        is_sequence = bool(representation["context"].get("frame"))
        # The path is either a single file or sequence in a folder.
        if not is_sequence:
            filename = path
        else:
            filename = re.sub(r"(.*)\.(\d+)\.(ass.*)", "\\1.$F4.\\3", path)

            filename = os.path.join(path, filename)

        filename = os.path.normpath(filename)
        filename = filename.replace("\\", "/")

        return filename