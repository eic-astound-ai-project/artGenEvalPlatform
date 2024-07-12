import argparse
import shutil
import os, sys
sys.path.append('.')
sys.path.append('..')
sys.path.append('../../')
sys.path.append('../../../')
import json
import os.path
from src.utils.text_processor import str_parser
import src.metrics.quality_metrics as qualEval
from src.utils.text_processor import Text_processor
from src.utils.loader_saver import load_json
import pandas as pd
from src.utils.args_utils import str2bool



def main(args, root_folder, dialogueID, isYesNoresponse=False):
    with open(args.dialogueJSON, "r") as read_file:
        dialogue_template = json.load(read_file)

    with open(os.path.join(root_folder, "response.json"), "r") as read_file:
        response_template = json.load(read_file)
    # File with the structure of the responses of ChatGPT
    with open(dialogue_template["response_structure_path"], "r") as read_file:
        response_structure_json = json.load(read_file)
    response = response_template
    # Access recursively to the fields of the answer under content
    if("content" in list(response_structure_json.keys())):
        for field2access in response_structure_json["content"]:
            response = response[field2access]
        if(isYesNoresponse):
            # Get profiles:
            profiles = dialogue_template["profiles"]
            responseJSON = YesNoresponse2profile(response, profiles)
        else:
            responseJSON = response2profile(response)
    else:
        responseJSON = {"profiles": []}

    # Complete automatically the profiles
    responseJSON["dialogue_ID"] = dialogueID
    # Save final json with the completed profiles
    dialogue_template_asString = json.dumps(responseJSON, indent=4)
    with open(os.path.join(args.out_dir, "responseAsProfile.json"), "w") as write_file:
        write_file.write(dialogue_template_asString)
    return response_template



def response2profile(response):
    response_JSON = {"profiles": []}
    # Split profiles:
    profiles = str_parser(response, parser="\n\n")
    for profile in profiles:
        # Split profile on its fields
        profile_fields = str_parser(profile, parser="\n")
        profile_name = profile_fields[0]
        new_profile = complete_profile(profile_name, profile_fields)
        response_JSON["profiles"].append(new_profile)
    return response_JSON
    # Last check to evaluate if fields are the same


def complete_profile(profile_name, profile_fields, initial_index = 1):
    profile_fields2complete = {}
    profile_fields = list(filter(None, profile_fields))
    # Split fields in key:value
    for profile_fielKV in profile_fields[initial_index::]:
        key_value = str_parser(profile_fielKV, parser=":")
        if(len(key_value)>=2):
            value = key_value[1].strip().replace("\"", "")
            # check whether value is not empty:
            if(not value==""):
                profile_fields2complete[key_value[0]] = key_value[1].strip().replace("\"", "")

    # Save new profile
    new_profile = {
        "profile_name": profile_name,
        "profile_fields_prompt": profile_fields2complete
    }
    return new_profile



def YesNoresponse2profile(response, originalProfiles, short_answer=True):
    common_text_processor = Text_processor({ "- ": "",
      "-": " ",
      "_": " ",
      ":": "",
      "*": "",
      "'": " "}, lowercase=True)
    response_JSON = {"profiles": []}
    # We know that there is a single profile:
    profile_name = "Statements:"
    originalFields = {}
    for idx in range(len(originalProfiles)):
        if(originalProfiles[idx]["profile_name"]==profile_name):
            originalFields = originalProfiles[idx]["profile_fields_prompt"]
    inverse_originalFields = {common_text_processor.preprocessing_text(v): k for k, v in originalFields.items()}

    # Get original dialogue
    # Split profile on its fields
    profile_fields = str_parser(response, parser="\n")
    new_profile = complete_profile(profile_name, profile_fields, initial_index=0)
    # Replace keys by keywords in original profile
    final_profile = {}
    for profile_key in list(new_profile["profile_fields_prompt"].keys()):
        # Check similarities between original & generated
        value = new_profile["profile_fields_prompt"][profile_key]
        processed_profile_key = common_text_processor.preprocessing_text(profile_key)
        if(processed_profile_key in inverse_originalFields.keys()):
            final_profile[inverse_originalFields[processed_profile_key]] = int(eval(value.split(".")[0]))
            del inverse_originalFields[processed_profile_key]
        else: # Check the most similar
            top_profile, top_similar_value = "", -1
            for originalStatement in list(inverse_originalFields.keys()):
                # Calculate distance between sentences:
                score = qualEval.metrics_calculator("JaccardSim", originalStatement, processed_profile_key)
                if(score>top_similar_value):
                    top_profile = originalStatement
                    top_similar_value = score
            try:
                final_profile[inverse_originalFields[top_profile]] = int(eval(value.split(".")[0]))
                del inverse_originalFields[top_profile]
            except SyntaxError:
                print("debug - value: ", value)
                pass
    # Match generated profiles with original profiles:
    response_JSON["profiles"].append(final_profile)
    return response_JSON



def isFull_responseAsProfile(path_response_as_profile):
    response_json = load_json(path_response_as_profile)
    if(len(response_json["profiles"][0])>0):
        return True
    else:
        return False

def check_finish_reasons(root_path, response_structure, response_name = "response.json"):
    dialogues_finish_reasons = pd.DataFrame([], columns=["DIALOGUE_ID", "finish_reason", "N_files", "isResponseCorrect"])
    for dialogue in os.listdir(root_path):
        if(dialogue == "ERRORS_LOGS"):continue
        n_files = len(os.listdir(os.path.join(root_path, dialogue)))
        path_response = os.path.join(root_path, dialogue, response_name)
        if(os.path.exists(path_response)):
            response_json = load_json(path_response)
            for response_item in response_structure:
                response_json = response_json[response_item]
            path_response_as_profile = os.path.join(root_path, dialogue, "responseAsProfile.json")
            if(os.path.exists(path_response_as_profile)):
                isCorrect = isFull_responseAsProfile(path_response_as_profile)
            else:
                isCorrect = False
            dialogues_finish_reasons = dialogues_finish_reasons.append(pd.DataFrame([[dialogue, response_json, n_files, isCorrect]], columns=["DIALOGUE_ID", "finish_reason", "N_files", "isResponseCorrect"]))
        else:
            print("FileNotFoundError: [Errno 2] No such file or directory: ", path_response)
            dialogues_finish_reasons = dialogues_finish_reasons.append(
                pd.DataFrame([[dialogue, "unk", 0, False]], columns=["DIALOGUE_ID", "finish_reason", "N_files", "isResponseCorrect"]))
    return dialogues_finish_reasons



def check_complete_eval(root_path):
    dialogues_finish_reasons = pd.DataFrame([], columns=["DIALOGUE_ID", "finish_reason", "N_files"])
    for dialogue in os.listdir(root_path):
        if (dialogue == "ERRORS_LOGS"): continue
        n_files = len(os.listdir(os.path.join(root_path, dialogue)))
        dialogues_finish_reasons = dialogues_finish_reasons.append(
            pd.DataFrame([[dialogue, "stop", n_files]], columns=["DIALOGUE_ID", "finish_reason", "N_files"]))
    return dialogues_finish_reasons



def clean_files(df_errors, root_path_files, maintain_content_filter=True, remove_folders=True):
    mode_n_files = df_errors["N_files"].mode()[0]
    print("MODE NUMBER OF FILES DETECTED: ", str(mode_n_files))

    possible_files_with_errors = df_errors.loc[df_errors["N_files"]<mode_n_files]
    if("isResponseCorrect" in df_errors.columns):
        print("----------- QUALITY ERRORS ------------")
        possible_files_with_errors_Asprofile = df_errors.loc[df_errors["isResponseCorrect"]==False]
        print("Possible Errors quality: ", possible_files_with_errors_Asprofile[["DIALOGUE_ID","finish_reason","isResponseCorrect"]].to_string())
        possible_files_with_errors = possible_files_with_errors.append(possible_files_with_errors_Asprofile)


    # Check files with 'content_filter' (or other finish reasons different from 'stop'):
    nonStop_responses = df_errors.loc[df_errors["finish_reason"]!="stop"]
    if(maintain_content_filter):
        print("----------- STOP REASONS ------------")
        # Add those with content fitler:
        for finish_reason in list(nonStop_responses["finish_reason"].unique()):
            df_finish_reason =  nonStop_responses.loc[nonStop_responses["finish_reason"] == finish_reason]
            print(finish_reason, df_finish_reason[["DIALOGUE_ID","finish_reason","isResponseCorrect"]].to_string())
        #possible_files_with_errors = possible_files_with_errors.append(nonStop_responses)

    # Remove duplicate files:
    possible_files_with_errors = possible_files_with_errors.drop_duplicates()
    print("Possible files 2 rm: ", str(len(possible_files_with_errors)))
    # Remove files in folder
    for i, row in possible_files_with_errors.iterrows():
        print("FOLDER: ", os.path.join(root_path_files, row["DIALOGUE_ID"]))
        if(remove_folders):
            # Save a copy in errors
            try:
                shutil.move(os.path.join(root_path_files, row["DIALOGUE_ID"]), os.path.join(root_path_files, "ERRORS_LOGS"))
                print(">> REMOVING ...")
                #shutil.rmtree(os.path.join(root_path_files, row["DIALOGUE_ID"]))
                print("------")
            except shutil.Error:
                shutil.rmtree(os.path.join(root_path_files, row["DIALOGUE_ID"]))





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Configuration of the dialogue creator tool")
    parser.add_argument('-GeneratedEvalPath', '--root_path', type=str, required=True,
                        help='Path to the folder of automatically generated dialogues or automaticaly generated evaluations by LLM models')
    parser.add_argument('-removeFolders', '--remove_folders', type=str, help='True if we want to clean the directory of LLM answers with incorrect formats',
                        default="False")
    parser.add_argument('-type_of_check', '--type_of_check', type=str,
                        help='Type of analysis to do: "Generation" when you create dialogues or the Yes/No statements; "Evaluation" when you evaluate the answers to Yes/No ',
                        default="Generation")

    args = parser.parse_args()
    response_structure = ["choices", 0, "finish_reason"]

    path_error_logs = os.path.join(args.root_path, "ERRORS_LOGS")
    if("Generation" in args.root_path or "dialogueTests" in args.root_path or "GeneratedDialogues" in args.root_path or args.type_of_check == "Generation"):
        print("Checking as 'Generation' type")
        df_errors = check_finish_reasons(args.root_path, response_structure, response_name="response.json")
    elif("Evaluation" in args.root_path or args.type_of_check == "Evaluation"):
        print("Checking as 'Evaluation' type")
        df_errors = check_complete_eval(args.root_path)
        #check_complete_eval
    else:
        print("Error")

    os.makedirs(path_error_logs, exist_ok=True)
    df_errors.to_csv(os.path.join(path_error_logs, "error_logs_secondCheck.csv"), sep=";", header=True)
    print(" >>> >>> N FILES DETECTED: ", len(df_errors), " <<< <<< ")
    # Create filters:
    clean_files(df_errors, args.root_path, remove_folders=str2bool(args.remove_folders))





