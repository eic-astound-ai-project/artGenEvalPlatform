# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 13:31:06 2023

@author: MGM & CLJ
"""

import shutil
from src.API_callers.ChatGPT_Azure_API_caller import *
from src.utils.args_utils import *
from src.utils.loader_saver import save_modelConfig_JSON



def clean_autoProfiles(inputStr):
    # Remove certain charaters
    outStr = inputStr.replace("-", " ").replace("_", " ")
    # First with capital letter:
    outStr = outStr.lower().capitalize()
    return outStr


def complete_profile(profile_name, profile_values, print_key=True):
    prompt = profile_name + ":\n"

    for k, v in profile_values.items():
        if (print_key):
            prompt += k + ": " + clean_autoProfiles(str(v)) + "\n"
        else:
            prompt += v + "\n"
    return prompt


def create_prompt(dialogue_template):
    prompt = dialogue_template['initial_prompt'] + "\n"
    for profile in dialogue_template['profiles']:
        prompt += complete_profile(profile['profile_name'],profile['profile_fields_prompt'], str2bool(profile['print_keys']))
    return prompt




def main(args, json_indent = 4):
    with open(os.path.join(args.out_dir, args.dialogueCompletedJSON), "r") as read_file:
        dialogue_template = json.load(read_file)

    # Create prompt as string
    prompt = create_prompt(dialogue_template)
    print(prompt)
    # API Call - ChatGPT
    #Config model:
    model_config_json = cofigt_chatGPT(dialogue_template['model_config_path'])
    # Adapt prompt to the model
    message = message_creator(dialogue_template['system_role'], prompt)
    #Approx. number of tokens:
    # num_tokens = num_tokens_from_messages(message, model=model_config_json["GPT_MODEL"])
    # print("Num tokens - openAI solution: ", str(num_tokens))
    # Call the model
    response = ChatGPT_API_call(message, model_config_json)

    ########## SAVE ###############
    # Copy configuration
    # Save model config removing API_KEY
    save_modelConfig_JSON(dialogue_template['model_config_path'], os.path.join(args.out_dir, "modelConfig.json"), json_indent)
    #Save prompt/messages
    messages_JSON = json.dumps(message, indent=json_indent)
    with open(os.path.join(args.out_dir, "prompt.json"), "w") as write_file:
        write_file.write(messages_JSON)
    #Save response as JSON
    json_response = json.dumps(response, indent=json_indent)
    with open(os.path.join(args.out_dir, "response.json"), "w") as write_file:
        write_file.write(json_response)










