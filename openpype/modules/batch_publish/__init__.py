""" Addon class definition and Settings definition must be imported here.

If addon class or settings definition won't be here their definition won't
be found by OpenPype discovery.
"""

from .batch_publish_module import (
    BatchPublishSettingsDef,
    BatchPublishModule
)

__all__ = (
    "BatchPublishSettingsDef",
    "BatchPublishModule"
)
