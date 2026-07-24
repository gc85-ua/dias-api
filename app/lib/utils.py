import json
from difflib import SequenceMatcher
from os import path
from typing import Any


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


def calculate_similarity(a: str, b: str):
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()


def fuzzy_match_from_dict(
    term: str, dictionary: dict[str, Any], threshold: float = 0.6
) -> dict[str, Any]:

    result = {"best_match": None, "best_match_value": None, "highest_similarity": 0.0}

    for key, value in dictionary.items():
        similarity = calculate_similarity(term, key)

        if "/" in key:
            segments = key.split("/")
            segments_similarity = [
                calculate_similarity(term, segment) for segment in segments
            ]
            similarity = max(similarity, *segments_similarity)

        if similarity > result["highest_similarity"]:
            result["highest_similarity"] = similarity
            result["best_match"] = key
            result["best_match_value"] = value

    if result["highest_similarity"] < threshold:
        # if the threshold is not met, value is considered not found, but we leave the best match for reference
        result["best_match_value"] = None

    return result
