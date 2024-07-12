import json


def load_json(path_json):
    with open(path_json, "r") as read_file:
        json_data = json.load(read_file)
    return json_data


def save_json(json_data, path2save, json_indent=4):
    messages_JSON = json.dumps(json_data, indent=json_indent)
    with open(path2save, "w") as write_file:
        write_file.write(messages_JSON)

def save_modelConfig_JSON(in_path_model, out_path_model, json_indent):
    modelJSON = load_json(in_path_model)
    # Remove API_KEY
    del modelJSON["API_KEY"]
    # Save JSON in new path
    save_json(modelJSON, out_path_model, json_indent)