import json
import os.path

import pandas as pd
import random
import copy
from pathlib import PurePath

def autoCompletion_autoCSV(profile_dict, rowOfCSV=-1):
    df_csv = pd.read_csv(profile_dict['profile_auto_path_csv'])
    if(rowOfCSV==-1):
        row2extractInfo = profile_dict['csv_row']
    else:
        row2extractInfo = rowOfCSV
    data2obtain = df_csv.iloc[row2extractInfo].to_dict()
    #Complete the json
    for field in profile_dict['profile_fields_prompt']:
        # Check if it is completed (if it has information different from "" > not update
        if(profile_dict['profile_fields_prompt'][field]==""): # empty
            profile_dict['profile_fields_prompt'][field] = data2obtain[profile_dict['profile_auto_PromptFields_csvFields'][field]]
    return profile_dict


def get_values_autoControlRandList(json_info_name, df_json):
    typeField = df_json[json_info_name]["type"]
    if(typeField=="range"):
        value = random.randrange(df_json[json_info_name]["min"], df_json[json_info_name]["max"], df_json[json_info_name]["step"])
    elif(typeField=="list"):
        value = random.choice(df_json[json_info_name]["values"])
    else:
        print("type of field not recognised. Try one of these: [range, list]")
    return value



def autoCompletion_autoControlRandList(profile_dict):
    # Read the json with info about the random values from which making the selection
    with open(profile_dict['profile_auto_path_csv'], "r") as read_file:
        df_json = json.load(read_file)
    # Complete the json of the profile
    for field in profile_dict['profile_fields_prompt']:
        # Check if it is completed (if it has infor different from "" > not update
        if (profile_dict['profile_fields_prompt'][field] == ""):  # empty
            json_info_name = profile_dict['profile_auto_PromptFields_csvFields'][field]
            valueOftheField = get_values_autoControlRandList(json_info_name, df_json)
            # Fill in profile field
            profile_dict['profile_fields_prompt'][field] = valueOftheField
    return profile_dict

def check_autoCompletion_manual(profile_dict):
    # Complete the json of the profile
    fields2check = []
    for field in profile_dict['profile_fields_prompt']:
        if (profile_dict['profile_fields_prompt'][field] == ""):  # empty
            fields2check+=[field]
    #Final message:
    if(len(fields2check)<=0):
        print("    > All the fields seems correctly completed! :)")
    else:
        print("    > Some fields are not correctly completed. Check fields: ")
        print("    > ",fields2check)



def autoCompletion_dialogueResponseJSON(profile_dict, dialogue_ID):
    # Read the json with the generated dialogue by ChatGPT
    if("dialogue_ID" in profile_dict['profile_auto_path_csv']):
        profile_dict['profile_auto_path_csv'] = profile_dict['profile_auto_path_csv'].replace("dialogue_ID", str(dialogue_ID))
    else: # Replace last folder name by the name of the dialogueID
        dialogue_parts = list(PurePath(profile_dict['profile_auto_path_csv']).parts)
        dialogue_parts[-2] = str(dialogue_ID)
        profile_dict['profile_auto_path_csv'] = os.path.join(*dialogue_parts)

    with open(profile_dict['profile_auto_path_csv'], "r") as read_file:
        df_json = json.load(read_file)

    # Extract dialogue from response file:
    for field in profile_dict['profile_fields_prompt']:
        if(field=="content"):
            with open(profile_dict['profile_auto_PromptFields_csvFields']["content"], "r") as read_file:
                response_structure_json = json.load(read_file)
            response = df_json
            # Access recursively to the fields of the answer
            for field2access in response_structure_json["content"]:
                response = response[field2access]
            profile_dict['profile_fields_prompt']["content"] = response
    return profile_dict


def autoCompletion_copyAllEmptyProfiles(dialogue_profiles, profile_idx, default_value = "", new_profile_completion = "empty"):
    profile_dict = dialogue_profiles[profile_idx]
    # Read the json with info about the random values from which making the selection
    with open(profile_dict['profile_auto_path_csv'], "r") as read_file:
        df_json = json.load(read_file)

    #Remove previous profile & add new automatic profiles
    # 1. Remove current profile
    del dialogue_profiles[profile_idx]
    # 2. Add new profiles
    for profile in df_json["profiles"]:
        profile["profile_fields_prompt"] = dict.fromkeys(profile["profile_fields_prompt"], default_value)
        profile["profile_fields_completion"] = new_profile_completion
        dialogue_profiles.append(profile)
    return dialogue_profiles


def autoCompletion_metricsAutoCompleteAll(profile_dict, default_value = "", new_profile_completion = "empty"):
    profile_name = profile_dict["profile_name"]
    # Read the json with info about the random values from which making the selection
    with open(profile_dict['profile_auto_path_csv'], "r") as read_file:
        df_json = json.load(read_file)
    # 1. Complete profile fields with default values
    for profile in df_json["profiles"]:
        if(profile["profile_name"] == profile_name):
            profile_dict['profile_fields_prompt'] = dict.fromkeys(profile["profile_fields_prompt"], default_value)
            profile_dict["profile_fields_completion"] = new_profile_completion
            break
    return profile_dict




def profiles_auto_completion(dialogue_template, general_row=-1):
    # Create a copy of the original template:
    dialogue_template_copy = copy.deepcopy(dialogue_template)
    # Complete automatically the profiles
    for profile2complete_idx in range(len(dialogue_template["profiles"])):
        # Check type of auto-completion
        profile2complete = dialogue_template_copy["profiles"][profile2complete_idx]
        # Auto-completions for basic dialogue generations
        if (profile2complete['profile_fields_completion'] == 'autoCSV'):
            _ = autoCompletion_autoCSV(profile2complete, general_row)
        elif (profile2complete['profile_fields_completion'] == 'manual' or profile2complete['profile_fields_completion'] == 'metrics_manual'):
            print("Manual config of field: ", profile2complete['profile_name'])
            check_autoCompletion_manual(profile2complete)
        elif (profile2complete['profile_fields_completion'] == 'autoControlRandList'):
            _ = autoCompletion_autoControlRandList(profile2complete)
        # Auto-completions for quality checks
        elif (profile2complete['profile_fields_completion'] == 'dialogueResponseJSON'):
            dialogueID = dialogue_template["dialogue_ID"]
            _ = autoCompletion_dialogueResponseJSON(profile2complete, dialogueID)
        elif (profile2complete['profile_fields_completion'] == 'copyAllEmptyProfiles'):
            _ = autoCompletion_copyAllEmptyProfiles(dialogue_template_copy["profiles"], profile2complete_idx)
        elif (profile2complete['profile_fields_completion'] == 'empty'):
            pass
        elif (profile2complete['profile_fields_completion'] == 'metrics_autoCompleteAll'):
            _ = autoCompletion_metricsAutoCompleteAll(profile2complete, default_value=0,
                                                  new_profile_completion="metrics_manual")
        else:
            print("Type of auto-completion ", profile2complete['profile_fields_completion'],
                  " not-recognized. Try: 'autoCSV' or 'manual'")
    return dialogue_template_copy


def update_turns(dialogue_template, n_turns):
    dialogue_template["DG_turns"] = n_turns
    dialogue_template["initial_prompt"] = dialogue_template["initial_prompt"].replace("10 turns", str(n_turns)+" turns")
    return dialogue_template











############### PROCESSING PROFILES/TEMPLATES #############

def common_profiles_completion(args, dialogueID, general_csv_row=-1, n_turns=10, update_turns_inProfile=False):
    with open(args.dialogueJSON, "r") as read_file:
        dialogue_template = json.load(read_file)

    # Update the number of turns
    if (update_turns_inProfile):
        dialogue_template = update_turns(dialogue_template, n_turns)

        # Update the ID of the dialogue
    dialogue_template["dialogue_ID"] = dialogueID

    # Update the rows to read (when necessary for "autoCSV" processings)
    if (general_csv_row != -1):
        dialogue_template["general_csv_row"] = general_csv_row

    return dialogue_template


def main_metrics_profile(args, dialogueID, general_csv_row=-1, n_turns=10, update_turns_inProfile=False):
    dialogue_template = common_profiles_completion(args, dialogueID, general_csv_row=general_csv_row, n_turns=n_turns,
                                                   update_turns_inProfile=update_turns_inProfile)

    #Create copy to complete fields
    general_row = dialogue_template["general_csv_row"]
    new_dialogue_copy = copy.deepcopy(dialogue_template)
    new_dialogue_copy["metrics_profile"] = []
    # Complete automatically the profiles
    for metric_profile in dialogue_template["metrics_profile"]:
        metrics_dialogue_template = profiles_auto_completion(metric_profile, general_row)
        new_dialogue_copy["metrics_profile"].append(metrics_dialogue_template)
    # Save final json with the completed profiles
    new_dialogue_copy["dialogue_ID"] = dialogueID
    dialogue_template_asString = json.dumps(new_dialogue_copy, indent=4)
    with open(os.path.join(args.out_dir, args.dialogueCompletedJSON), "w") as write_file:
        write_file.write(dialogue_template_asString)
    return new_dialogue_copy, os.path.join(args.out_dir, args.dialogueCompletedJSON)

def main_profiles(args, dialogueID, general_csv_row = -1, n_turns=10, update_turns_inProfile = False):
    dialogue_template = common_profiles_completion(args, dialogueID, general_csv_row=general_csv_row, n_turns=n_turns,
                                                   update_turns_inProfile=update_turns_inProfile)

    # Complete the rest of the profiles according to the type of processing)
    general_row = dialogue_template["general_csv_row"]
    dialogue_template_copy = profiles_auto_completion(dialogue_template, general_row)

    # Save final json with the completed profiles
    dialogue_template_asString = json.dumps(dialogue_template_copy, indent=4)
    with open(os.path.join(args.out_dir, args.dialogueCompletedJSON), "w") as write_file:
        write_file.write(dialogue_template_asString)







