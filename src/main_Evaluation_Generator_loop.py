import argparse
import shutil
import os, sys
sys.path.append('.')
sys.path.append('..')
sys.path.append('../../')
sys.path.append('../../../')
import pandas as pd
import logging as logger
import src.profilesGenerators.automaticProfilesGenerators as profilesGenerator
import src.evalGenerators.quality_metrics_controller as metricsEvaluator
import src.metrics.characteristic_metrics_controller as ethicalmetricsEvaluator




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Configuration of the dialogue creator tool")

    parser.add_argument('-CSVwithDialogueParameters', '--dialogueParameters', type=str, required=True,
                        help='Path to the CSV with the DialogueIDs & parameters to modify templates')
    parser.add_argument('-out', '--out_dir', type=str, help='Path to save the embeddings extracted from the model',
                        default='./')
    parser.add_argument('-evalFolder', '--out_EvalFolderName', type=str, help='Path to save the embeddings extracted from the model',
                        default='Evaluation')
    parser.add_argument('-characteristic_type', '--characteristic_type', type=str, help='Type of metric [ProfileReconstructionQuality, Anthropic]',
                        default="", required=True)
    parser.add_argument('-metric_type', '--metric_type', type=str,
                        help='Type of metric [EvaluationYesNo, EvaluationObjectiveMetrics]',
                        default="", required=True)

    parser.add_argument('-dialogue_completed_name', '--dialogueCompletedJSON', type=str, required=False,
                        help='Path to the JSON template to be completed', default="autoCompletedProfile.json")
    parser.add_argument('-path2checkDialogues', '--path2checkDialogues', type=str, required=False,
                        help='Path to the JSON template to be completed',
                        default="../0publicData/output_files/Generated_Dialogues_v1")

    args = parser.parse_args()
    ## LOAD CSV FILE WITH THE DIALOGUES
    df_with_dialogues_ids = pd.read_csv(args.dialogueParameters, sep=",", header=0)
    dialogues_finish_reasons = pd.DataFrame([], columns = ["DIALOGUE_ID", "OpenAI_finish_reason", "processing_message"])
    # Create extra folder for ERRORS (to save logs):
    errors_logs_folder = os.path.join(args.out_dir, str("ERRORS_LOGS"))


    path_dialogues = args.path2checkDialogues
    if (path_dialogues == ""):
        df_with_dialogues_filtered = df_with_dialogues_ids
    else:
        list_dialogues = list(set(os.listdir(path_dialogues)).difference(set(["ERRORS_LOGS"])))
        df_with_dialogues_filtered = df_with_dialogues_ids.loc[
            df_with_dialogues_ids["DIALOGUE_ID"].isin(list_dialogues)]


    #df_with_dialogues_filtered = df_with_dialogues_ids

    general_idx_row = 0
    ############# INPUT PATH TEMPLATES ###################
    #metrics2extract = ["ProfileReconstructionQuality", "Anthropic"]
    path_templates = {
        "ProfileReconstructionQuality": {"EvaluationObjectiveMetrics": "../0publicData/input_files/2Evaluators/0QualityEval/metricsQuality_Expert.json"},

        "Anthropic": {"EvaluationYesNo" : "../0publicData/input_files/2Evaluators/AnthropicEval/YesNoMetricAnthropic.json",
                      "EvaluationObjectiveMetrics" : "../0publicData/input_files/2Evaluators/AnthropicEval/SingleMetricsAnthropic_Expert.json"},
    }

    new_original_root = os.path.join(args.out_dir, args.characteristic_type)
    for idx, dialogue_row in df_with_dialogues_filtered.iterrows():
        #real_idx = int(df_with_dialogues_filtered.index[idx])
        dialogueID = dialogue_row["DIALOGUE_ID"]
        print(dialogueID)
        dialogue_turns = str(dialogue_row["DG_turns"])
        #for characteristic_type in [args.characteristic_type]:
        ################ EVALUATE QUALITY OF DIALOGUES #####################
        if (args.characteristic_type=="ProfileReconstructionQuality"):
            if(args.metric_type == "EvaluationObjectiveMetrics"):
                ### 2. EVALUATION
                # Fill in JSON
                root_folder = os.path.join(new_original_root, "ObjectiveMetrics", args.out_EvalFolderName, str(dialogueID))
                # If the folder exist, we assume that it is completed
                if (os.path.exists(root_folder)): continue
                # Create out dir if it doesn't exist
                os.makedirs(root_folder, exist_ok=True)
                # Update ARGS values
                args.dialogueJSON = path_templates[args.characteristic_type][args.metric_type]
                args.out_dir = root_folder
                # Fill in JSON
                try:
                    profilesGenerator.main_metrics_profile(args, dialogueID)
                    # Calculate metrics between Dialogues
                    metricsEvaluator.main_quality_metrics(args, dialogueID)
                except FileNotFoundError as e:
                    logger.error(e)
                    pass
        elif (args.characteristic_type=="Anthropic"):
            if (args.metric_type == "EvaluationYesNo"):
                ### 2. EVALUATION (YES/NO)
                root_folder = os.path.join(new_original_root, "ChatGPTYesNo", args.out_EvalFolderName, str(dialogueID))
                # If the folder exist, we assume that it is completed
                if (os.path.exists(root_folder)): continue
                # Create out dir if it doesn't exist
                os.makedirs(root_folder, exist_ok=True)
                # Update ARGS values
                # Create/Complete profiles of the metrics:
                args.metrics_template = path_templates[args.characteristic_type]["EvaluationYesNo"]
                args.out_dir = root_folder
                args.dialogueJSON = path_templates[args.characteristic_type]["EvaluationYesNo"]
                completedProfileMetrics, path_saved_profile = profilesGenerator.main_metrics_profile(args, dialogueID, idx)
                # Calculate metrics
                args.dialogueJSON = path_saved_profile
                ethicalmetricsEvaluator.main_ethical_metrics(args, (dialogueID))
            elif(args.metric_type == "EvaluationObjectiveMetrics"):
                ## 3. EVALUATION (OBJECTIVE METRICS)
                root_folder = os.path.join(new_original_root, "ObjectiveMetrics", args.out_EvalFolderName, str(dialogueID))
                # If the folder exist, we assume that it is completed
                if (os.path.exists(root_folder)): continue
                # Create out dir if it doesn't exist
                os.makedirs(root_folder, exist_ok=True)
                # Update ARGS values
                # Create/Complete profiles of the metrics:
                args.metrics_template = path_templates[args.characteristic_type]["EvaluationObjectiveMetrics"]
                args.out_dir = root_folder
                args.dialogueJSON = path_templates[args.characteristic_type]["EvaluationObjectiveMetrics"]
                # Calculate metrics of each Dialogue
                ethicalmetricsEvaluator.main_ethical_metrics(args, (dialogueID))
        else:
            print("to do")






