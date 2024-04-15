import json
# import dill as pickle


# def write_profiles(profiles):
#     with open("profiles.pickle", "wb") as f:
#         return pickle.dump(profiles, f)


# def read_profiles():
#     with open("profiles.pickle", "rb") as f:
#         try:
#             return pickle.load(f)
#         except EOFError:
#             write_profiles({})
#             return {}


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


def write_profiles_json(profiles):
    with open("profiles.json", "w", encoding="utf-8") as f:
        return json.dump(profiles, f, indent=4, ensure_ascii=False)


def read_profiles_json():
    with open("profiles.json", "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except EOFError:
            write_profiles_json({})
            return {}
