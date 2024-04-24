import json

from over_classes import JSONDataAdapter


def write_interactions(interactions: dict):
    with open("interactions.json", "w", encoding="utf-8") as f:
        json.dump(interactions, f, indent=4)


def read_interactions():
    with open("interactions.json", "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            data_copy = {}
            for key, val in data.items():
                data_copy[int(key)] = val
            return data_copy
        except EOFError:
            write_interactions({})
            return {}


def write_profiles_json(profiles: dict):
    with open("profiles.json", "w", encoding="utf-8") as f:
        json.dump(JSONDataAdapter.to_json(profiles), f, indent=4, ensure_ascii=False)


def read_profiles_json():
    with open("profiles.json", "r", encoding="utf-8") as f:
        try:
            return JSONDataAdapter.from_json(json.load(f))
        except EOFError:
            write_profiles_json({})
            return {}
