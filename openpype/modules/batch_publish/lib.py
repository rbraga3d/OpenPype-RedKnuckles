from pprint import pprint

from openpype.client import (
    get_projects,
    get_doc_by_filter,
    get_docs_by_filter,

)

def get_project_names():
    names = []
    for project_name in get_projects(fields=["name"]):
        names.append(project_name["name"])
    return names

def get_shots_data(project_name):
    """Organize shot names and their work files into dicts:
    i.e {"name": "SH001",
        "workfiles": [
                        {
                            "name": 'file_name_v001.ma',
                            "path": '/path/to/file_name_v001.ma'
                        },
                        {
                            "name": 'file_name_v002.ma',
                            "path": '/path/to/file_name_v001.ma'
                        }
                    ]}}

    Args:
        project_name (str): Name of project where to look for.

    Returns:
        List: List with dicts containing shot names and their work files data..
    """

    shots_data = []

    # ----- Get animation tasks ----- #
    mongo_filter = {
        "type":"workfile",
        "task_name":"Animation"
        }

    anim_tasks = get_docs_by_filter(project_name, mongo_filter)
    anim_tasks = list(anim_tasks)

    # ----- Get shot assets names----- #
    mongo_filter = {
        "data.entityType": "Shot"
    }

    shot_assets = get_docs_by_filter(project_name, mongo_filter)
    shot_names = [shot_asset["name"] for shot_asset in shot_assets]

    # ----- Put all shot files into their respective dict ----- #
    for shot_name in shot_names:
        shot_struct = {
            "name": "",
            "workfiles": []
        }
        shot_struct["name"] = shot_name

        for task in anim_tasks:
            parent_id = task["parent"]
            parent = get_doc_by_filter(project_name, {"_id":parent_id})
            parent_name = parent["name"]

            file_struct = {
                "name": task["filename"],
                "path": task["files"][0]
            }

            if shot_name == parent_name:
                shot_struct["workfiles"].append(file_struct)

        shots_data.append(shot_struct)

    return shots_data
