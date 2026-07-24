import json
from os import path


def export_to_json(data: dict, filename: str, overwrite: bool = False) -> None:
    if not overwrite and path.exists(filename):
        raise FileExistsError(f"File {filename} already exists")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def import_from_json(filename: str) -> dict:
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def get_property_values_from_leaves(
    tree: dict, children_property: str, property: str, result=None
) -> dict:
    if result is None:
        result = {}

    for key, value in tree.items():
        if not isinstance(value, dict):
            continue

        children = value.get(children_property, {})

        if isinstance(children, dict) and children:
            get_property_values_from_leaves(
                children, children_property, property, result
            )
        else:
            prop_value = value.get(property)
            if prop_value is not None:
                result[key] = prop_value

    return result
