import argparse
import shutil
import os, sys
sys.path.append('.')
sys.path.append('..')
sys.path.append('../../')
sys.path.append('../../../')
import pandas as pd
import src.profilesGenerators.automaticProfilesGenerators as profilesGenerator
import src.API_callers.promtps_generator as dialogueGenerator
import src.utils.response2profileJSON as response2JSON
import logging as logger
from src.utils.args_utils import exception_handler
from src.utils.args_utils import str2bool

def main(args, df_with_dialogues_filtered):
    # Create extra folder for ERRORS (to save logs):
    errors_logs_folder = os.path.join(args.out_dir, str("ERRORS_LOGS"))
    os.makedirs(errors_logs_folder, exist_ok=True)
    dialogues_finish_reasons = pd.DataFrame([], columns=["DIALOGUE_ID", "OpenAI_finish_reason", "processing_message"])
    general_idx_row = 0
    original_root = args.out_dir
    finish_reason, processing_message = "NULL", "NULL"
    for idx, dialogue_row in df_with_dialogues_filtered.iterrows():
        # real_idx = int(df_with_dialogues_filtered.index[idx])
        dialogueID = dialogue_row["DIALOGUE_ID"]
        print(dialogueID)

        dialogue_turns = str(dialogue_row["DG_turns"])

        root_folder = os.path.join(original_root, str(dialogueID))
        # If the folder exist, we assume that it is completed
        if (os.path.exists(root_folder)): continue
        # Create out dir if it doesn't exist
        os.makedirs(root_folder, exist_ok=True)
        # Update output folder with each dialogueID
        args.out_dir = root_folder
        # Call automatic prompts generator
        profilesGenerator.main_profiles(args, dialogueID, idx, dialogue_turns,
                                        update_turns_inProfile=str2bool(args.update_turns_inProfile))
        continueProcessing = True
        processing_message = "OK"
        try:
            # Call API caller to generate dialogues
            dialogueGenerator.main(args)
            # Visualize JSON response
            responseInJSON = response2JSON.main(args, root_folder, dialogueID, str2bool(args.YesNoResponse))
            finish_reason = responseInJSON["choices"][0]["finish_reason"]

        except Exception as e:
            continueProcessing, processing_message = exception_handler(e, dialogueID, "", logger)
            finish_reason = "OpenAI_ERROR"
            # Move created folder to errors (if that folder didn't exist before):
            if(not os.path.exists(os.path.join(errors_logs_folder, str(dialogueID)))):
                shutil.copytree(root_folder, os.path.join(errors_logs_folder, str(dialogueID)))
        finally:
            if (not continueProcessing):
                # Save logs file & finish process
                dialogues_finish_reasons.to_csv(os.path.join(errors_logs_folder, "error_logs_generation.csv"), sep=";",
                                                header=True, index=False)
                break
            # Check response code
            dialogues_finish_reasons = dialogues_finish_reasons.append(
                pd.DataFrame([[dialogueID, finish_reason, processing_message]],
                             columns=["DIALOGUE_ID", "OpenAI_finish_reason", "processing_message"]))

    # Save logs file & finish process
    dialogues_finish_reasons.to_csv(os.path.join(errors_logs_folder, "error_logs_generation.csv"), sep=";", header=True,
                                    index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Configuration of the dialogue creator tool")
    parser.add_argument('-dialogue_template_path', '--dialogueJSON', type=str, required=True,
                        help='Path to the JSON template to be completed')
    parser.add_argument('-CSVwithDialogueParameters', '--dialogueParameters', type=str, required=True,
                        help='Path to the CSV with the DialogueIDs & parameters to modify templates')
    parser.add_argument('-out', '--out_dir', type=str, help='Path to save the embeddings extracted from the model',
                        default='./')
    parser.add_argument('-dialogue_completed_name', '--dialogueCompletedJSON', type=str, required=False,
                        help='Path to the JSON template to be completed', default="completedDialogue.json")
    parser.add_argument('-update_turns_inProfile', '--update_turns_inProfile', type=str, help='Whether to update turns in profile',
                        default='./')
    parser.add_argument('-isYesNoResponse', '--YesNoResponse', type=str, help='True if it is a True/False response',
                        default="False")
    parser.add_argument('-path2checkDialogues', '--path2checkDialogues', type=str, required=False,
                        help='Path to the JSON template to be completed',
                        default="../0publicData/output_files/Generated_Dialogues_v1")


    args = parser.parse_args()
    ## LOAD CSV FILE WITH THE DIALOGUES
    df_with_dialogues_ids = pd.read_csv(args.dialogueParameters, sep=",", header=0)



    # Check existing dialogues:
    # path_dialogues "" first time; if generated path_dialogues = "../Generation" after removing dirty dialogues (empty, content filter...)
    path_dialogues = args.path2checkDialogues
    if(path_dialogues==""):
        df_with_dialogues_filtered = df_with_dialogues_ids
    else:
        list_dialogues = list(set(os.listdir(path_dialogues)).difference(set(["ERRORS_LOGS"])))
        df_with_dialogues_filtered = df_with_dialogues_ids.loc[
            df_with_dialogues_ids["DIALOGUE_ID"].isin(list_dialogues)]


    main(args, df_with_dialogues_filtered)

