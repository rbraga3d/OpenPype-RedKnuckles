"""Addon definition is located here.

Import of python packages that may not be available should not be imported
in global space here until are required or used.
- Qt related imports
- imports of Python 3 packages
    - we still support Python 2 hosts where addon definition should available
"""

import os
import click

from openpype.modules import (
    JsonFilesSettingsDef,
    OpenPypeAddOn,
    ModulesManager,
    IPluginPaths,
    ITrayAction
)



class BatchPublishSettingsDef(JsonFilesSettingsDef):

    schema_prefix = "batch_publish_addon"

    def get_settings_root_path(self):
        return os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "settings"
        )


class BatchPublishModule(OpenPypeAddOn, IPluginPaths, ITrayAction):

    label = "Batch Publish (beta)"
    name = "batch_publish_addon"

    def initialize(self, settings):
        """Initialization of addon."""

        # Enabled by settings
        self.enabled = True

        # Prepare variables that can be used or set afterwards
        self._connected_modules = None
        # UI which must not be created at this time
        self._dialog = None

    def tray_init(self):
        """Implementation of abstract method for `ITrayAction`.

        We're definitely  in tray tool so we can pre create dialog.
        """

        self._create_dialog()

    def _create_dialog(self):
        # Don't recreate dialog if already exists
        if self._dialog is not None:
            return

        from .widgets import BatchPublishDialog

        self._dialog = BatchPublishDialog()

    def show_dialog(self):
        """Show dialog with connected modules.

        This can be called from anywhere but can also crash in headless mode.
        There is no way to prevent addon to do invalid operations if he's
        not handling them.
        """
        # Make sure dialog is created
        self._create_dialog()
        # Show dialog
        self._dialog.open()

    def get_connected_modules(self):
        """Custom implementation of addon."""
        names = set()
        if self._connected_modules is not None:
            for module in self._connected_modules:
                names.add(module.name)
        return names

    def on_action_trigger(self):
        """Implementation of abstract method for `ITrayAction`."""
        self.show_dialog()

    def get_plugin_paths(self):
        """Implementation of abstract method for `IPluginPaths`."""
        current_dir = os.path.dirname(os.path.abspath(__file__))

        return {
            "publish": [os.path.join(current_dir, "plugins", "publish")]
        }

    def cli(self, click_group):
        click_group.add_command(cli_main)


@click.group(BatchPublishModule.name, help="Example addon dynamic cli commands.")
def cli_main():
    pass


@cli_main.command()
def nothing():
    """Does nothing but print a message."""
    print("You've triggered \"nothing\" command.")


@cli_main.command()
def show_dialog():
    """Show ExampleAddon dialog.

    We don't have access to addon directly through cli so we have to create
    it again.
    """
    from openpype.tools.utils.lib import qt_app_context

    manager = ModulesManager()
    batch_publish_addon = manager.modules_by_name[BatchPublishModule.name]
    with qt_app_context():
        batch_publish_addon.show_dialog()
