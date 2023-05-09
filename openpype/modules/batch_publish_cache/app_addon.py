from pprint import pprint

from openpype.client import (
    get_projects,
    get_project,
    get_assets,
)

for project in get_projects(fields=['name']):
    pprint(project)
