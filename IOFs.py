import json
import dill as pickle


def write_profiles(profiles):
    with open("profiles.pickle", "wb") as f:
        return pickle.dump(profiles, f)


def read_profiles():
    with open("profiles.pickle", "rb") as f:
        try:
            return pickle.load(f)
        except EOFError:
            write_profiles({})
            return {}


def write_interactions(interactions):
    with open("interactions.json", "w", encoding="utf-8") as f:
        return json.dump(interactions, f, indent=4)


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
