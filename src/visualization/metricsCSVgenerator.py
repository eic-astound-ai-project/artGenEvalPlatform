import argparse
import os
import pandas as pd
from src.utils.loader_saver import load_json
import logging as logger
import ast



# python src/main_DialoguesGenerator.py --dialogueJSON 0publicData/input_files/DialogueGeneration/dialogue.json --dialogueCompletedJSON completedDialogue.json --out_dir 0publicData/output_files/dialogueTests --dialogueID 0


def fill_csv_profile(profile_directory, dialogues_list):
    df = pd.DataFrame()
    for i in range(len(dialogues_list)):
        df.loc[i, 'DIALOGUE_ID'] = dialogues_list[i]

        try:
            profile_json = load_json(
                os.path.join(profile_directory , dialogues_list[i],"ProfileReconstructionQuality_metrics.json"))

            metrics_dics = profile_json.get("metrics_profile")

            for j in range(len(metrics_dics)):
                current_metric_dict = metrics_dics[j]
                metric_name = current_metric_dict.get("metrics_name")

                for key, value in current_metric_dict.get("metric_global").items():
                    df.loc[i, metric_name + "_" + key] = value

                profiles = current_metric_dict.get("profiles")

                for k in range(len(profiles)):
                    current_profile_dict = profiles[k]
                    profile_name = current_profile_dict.get("profile_name").replace(" ", "_")

                    for key, value in current_profile_dict.get("profile_fields_prompt").items():
                        key = key.replace("- ", "").replace(" ", "_")
                        df.loc[i, metric_name + "_" + profile_name + "--" + key] = value
        except FileNotFoundError as e:
            logger.error(e)
            df.loc[i, 1:-1] = None

    return df


def fill_csv_yesno_anthropic(anthropic_yesno_directory, dialogues_list, keyword="anthropic", extra_info = ""):
    df = pd.DataFrame()
    for i in range(len(dialogues_list)):
        df.loc[i, 'DIALOGUE_ID'] = dialogues_list[i]
        try:
            users_dict = load_json(os.path.join(anthropic_yesno_directory ,dialogues_list[i] ,dialogues_list[
                i] + "_"+keyword+"YesNo_metrics.json")).get(keyword+"YesNo").get("dialogue_from_utterances") #_from_utterances

            for user, value_dict in users_dict.items():
                for key, value in value_dict.items():
                    if isinstance(value, dict):
                        df.loc[i, user + "_" + key + "_score"+extra_info] = value.get("score")
                    else:
                        df.loc[i, user + "_" + key+extra_info] = value
        except FileNotFoundError as e:
            logger.error(e)
            df.loc[i, 1:-1] = None
            pass
        except AttributeError as e:
            logger.error(e)
            print(" ERROR ",dialogues_list[i])
            df.loc[i, 1:-1] = None
            pass
    return df


def fill_csv_objectiveMetrics(objective_metrics_directory, dialogues_list, keyword="anthropic", extra_info = ""):
    df = pd.DataFrame()
    for i in range(len(dialogues_list)):
        df.loc[i, 'DIALOGUE_ID'] = dialogues_list[i]
        try:
            char_dict = load_json(os.path.join(
                objective_metrics_directory , dialogues_list[i] , dialogues_list[i] + "_"+keyword+"_metrics.json"))
            for metric_name, metric_analysis in char_dict.items():
                for user, user_metric_values in metric_analysis.get("dialogue_from_utterances").items():
                    for statistic, statistic_val in user_metric_values.items():
                        if(statistic=="listValues"): continue
                        # Proces other statistics: max, min, avg ...
                        if isinstance(statistic_val, float):
                            df.loc[i, metric_name + "_" + user + "_" + statistic+extra_info] = statistic_val
                        elif isinstance(statistic_val, dict): # In some cases, metrics can have sub-types, hence we have to extract metrics from each sub-type
                            for key_subcharacteristic in statistic_val.keys():
                                df.loc[i, metric_name + '.'+key_subcharacteristic+ "._" + user + "_" + statistic+extra_info] = statistic_val[key_subcharacteristic]
        except FileNotFoundError as e:
            logger.error(e)
            df.loc[i, 1:-1] = None
            pass

    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="CSV Metrics Generator")
    parser.add_argument('-metricsDirectory', type=str, help='Root directory of the metrics', required=True)
    parser.add_argument('-out', '--out_csv', type=str, help='Path to save the embeddings extracted from the model',
                        default='./')
    parser.add_argument('-path_profile', '--path_profile', type=str, help='Path with the metrics of the recovered profile',
                        default='../0publicData/output_files/Metrics/ProfileReconstructionQuality/ObjectiveMetrics/Evaluation')
    parser.add_argument('-evalFoldersYesNo', '--out_EvalFolderNames_YesNoMetrics', type=str,
                        help='Path to save the embeddings extracted from the model',
                        default='["EvaluationGPT4", "EvaluationGPT35"]')
    parser.add_argument('-evalFoldersObjectiveMetrics', '--out_EvalFolderNames_ObjectiveMetrics', type=str,
                        help='Path to save the embeddings extracted from the model',
                        default='["Evaluation"]')
    parser.add_argument('-characteristic_types', '--characteristic_types', type=str,
                        help='Type of metrics ["Anthropic"]',
                        default="", required=True,)
    # .../ASTOUND_DS/0publicData/input_files/dialogue.json"

    args = parser.parse_args()
    directory = str(args.metricsDirectory)
    #profile_directory = os.path.join(directory, "ProfileReconstructionQuality","ObjectiveMetrics","Evaluation")

    dialogues_list = list(set(os.listdir(args.path_profile)).difference(set(["ERRORS_LOGS"]))) # profile_directory
    merged_df = fill_csv_profile(args.path_profile, dialogues_list)
    for ethic in ast.literal_eval(args.characteristic_types):
        # Append LLM evaluations (Yes/No):
        for LLM_eval in ast.literal_eval(args.out_EvalFolderNames_YesNoMetrics):
            path_yesno_directory = os.path.join(directory, ethic,"ChatGPTYesNo", LLM_eval)#"EvaluationGPT35"
            df2 = fill_csv_yesno_anthropic(path_yesno_directory, dialogues_list, keyword=ethic.lower(), extra_info="_YN_"+LLM_eval)
            merged_df = pd.merge(merged_df, df2, on='DIALOGUE_ID')
        # Append objective metrics:
        for objectiveMetrics_eval in ast.literal_eval(args.out_EvalFolderNames_ObjectiveMetrics):
            path_metric_directory = os.path.join(directory, ethic, "ObjectiveMetrics", objectiveMetrics_eval) # "Evaluation"
            df3 = fill_csv_objectiveMetrics(path_metric_directory, dialogues_list, keyword=ethic.lower(),extra_info="_OM_"+objectiveMetrics_eval)
            merged_df = pd.merge(merged_df, df3, on='DIALOGUE_ID')

    merged_df.to_csv(args.out_csv, index=False)






