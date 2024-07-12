import argparse
import shutil
import os, sys
sys.path.append('.')
sys.path.append('..')
sys.path.append('../../')
sys.path.append('../../../')
import pandas as pd
import logging as logger
import ast
import numpy as np





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Configuration of the dialogue creator tool")

    parser.add_argument('-in_metrics_csv', '--in_metrics_csv', type=str, required=True,
                        help='Path to the CSV with the extracted metrics')
    parser.add_argument('-out', '--out_csv', type=str, help='Path to save the final decision csv for the characteristic',
                        default='../0publicData/output_files/Metrics/FinalDecisionsAnthropicMetrics.csv', required=True)
    parser.add_argument('-grount_truth_column', '--grount_truth_column', type=str, help='Column to ge the original request of the profile, used as ground truth',
                        default='', required=True)
    parser.add_argument('-LLM_columns', '--LLM_columns', type=str, help='Columns extracted from the LLM to include [EX_anthropic_code_GENERATED_EvaluationGPT35,EX_anthropic_code_GENERATED_EvaluationGPT4]',
                        default="", required=True)
    parser.add_argument('-objectiveMetrics_thresholds', '--objectiveMetrics_thresholds', type=str,
                        help='Thresholds to consider for the objective metrics {"subjectivity_Expert_avg":0.6}',
                        default="", required=True)
    parser.add_argument('-metrics_order', '--metrics_order', type=str,
                        help='Order in which the mismatches will be checked {0:"EX_anthropic_code_GENERATED_EvaluationGPT35", 1:"subjectivity_Expert_avg"}',
                        default="", required=True)

    parser.add_argument('-min_matches_metricsAndProfile', '--min_matches_metricsAndProfile', type=int, required=False,
                        help='minimum number of matches of the metrics with the profile/ground truth for considering that the characterisitc appears in the dialogue', default=1)
    parser.add_argument('-final_decision_column', '--final_decision_column', type=str, required=False,
                        help='Name of the column with the final decision of the specific column of the characteristic',
                        default='EX_finalDecisionAnthropic')

    args = parser.parse_args()
    ## LOAD CSV FILE WITH THE DIALOGUES
    df_metrics = pd.read_csv(args.in_metrics_csv, sep=",", header=0)
    df_final = pd.DataFrame([])

    df_final["DIALOGUE_ID"] = df_metrics["DIALOGUE_ID"]
    df_final[args.grount_truth_column] = df_metrics[args.grount_truth_column]


    # Compare ground truth with Yes/No metrics automatically generated by LLMs:
    for LLM_metric in ast.literal_eval(args.LLM_columns):
        df_final[LLM_metric] = df_metrics[LLM_metric]
        df_final[LLM_metric+"_matchProfile"] = (df_final[LLM_metric]==df_final[args.grount_truth_column])#.map({True: 'True', False: 'False'})

    # Compare ground truth with objective metrics with their thresholds
    thresholds_objective_metrics = ast.literal_eval(args.objectiveMetrics_thresholds)
    for objective_metric_key in thresholds_objective_metrics.keys():
        objective_metric_th = thresholds_objective_metrics[objective_metric_key]
        df_final[objective_metric_key] = df_metrics[objective_metric_key]
        # Appply Threshold: Over th -> characteristic=1, lower than th -> characteristic=0
        df_final[objective_metric_key+"_afterTh"] = np.where(df_final[objective_metric_key] >= objective_metric_th, True, False)
        # Final match with the ground truth
        df_final[objective_metric_key + "_matchProfile"] = (df_final[objective_metric_key]==df_final[args.grount_truth_column])

    # Evaluate number of success following the order of metrics as the evaluation pipeline:
    order_metrics_toEval = ast.literal_eval(args.metrics_order)
    accumulated_success = 0
    recovered_errors = 0
    errors_list = df_final["DIALOGUE_ID"].values()
    df_final[args.final_decision_column] = False
    df_final["counter_success"] = 0
    metric_index = ">"
    for metric_position in sorted(order_metrics_toEval.keys()):
        print("..")
        n_success = len(df_final[order_metrics_toEval[metric_position] + "_matchProfile"] == True)
        n_errors = len(df_final[order_metrics_toEval[metric_position] + "_matchProfile"] == False)
        df_final.loc[df_final[order_metrics_toEval[metric_position] + "_matchProfile"] == True, "counter_sucess"] +=1
        print(metric_index, " METRIC POSITION: ", str(metric_position), " - Metric Name: ", order_metrics_toEval[metric_position])
        print(" # Total Success: ", str(n_success), " - # Total Errors: ", str(n_errors))

        df_sub_errors = df_final.loc[df_final["DIALOGUE_ID"] in errors_list]
        n_success_recovered = len(df_sub_errors[order_metrics_toEval[metric_position] + "_matchProfile"] == True)
        n_errors_remaining = len(df_sub_errors[order_metrics_toEval[metric_position] + "_matchProfile"] == False)
        errors_list = df_sub_errors[df_sub_errors[order_metrics_toEval[metric_position] + "_matchProfile"] == False, "DIALOGUE_ID"].values
        print(" # Recovered Success (Recovered from previous metric): ", str(n_success_recovered), " - # Remaining Errors ( Not Recovered from previous metric): ", str(n_errors_remaining))
        print(" ---------------- ")


    # Give final decision of the characteristic
    df_final[args.final_decision_column] = np.where(df_final["counter_success"] >= args.min_matches_metricsAndProfile, True, False)




