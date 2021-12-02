import json


def update_json_file(path, data: dict):
    with open(path, 'w') as json_file:
        json.dump(data, json_file, indent=5)


def read_settings(path):
    with open(path, 'r') as json_file:
        data = json.load(json_file)
    return data
