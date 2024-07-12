
import os, json, shutil
from src.utils.loader_saver import load_json
from src.utils.text_processor import Text_processor, convert_profile_list2dict
from src.metrics.quality_metrics import metrics_calculator
import numpy as np
import copy


def main_quality_metrics(args, dialogueID, json_indent=4):
    # Load dialogue & add ID
    metrics_json_template = load_json(os.path.join(args.out_dir, args.dialogueCompletedJSON))
    metrics_json_template["dialogue_ID"] = dialogueID

    #Create text processor for all the sentences:
    text_processor_params = load_json(metrics_json_template["params_text_processor_path"])
    common_text_processor = Text_processor(**text_processor_params["text_processor_params"])

    # Update values:
    metrics_json_template["in_folder_ChatGPT_generated_dialogues"] = metrics_json_template[
        "in_folder_ChatGPT_generated_dialogues"].replace("dialogue_ID", dialogueID)
    metrics_json_template["in_folder_ChatGPT_eval_generated_profiles"] = metrics_json_template[
        "in_folder_ChatGPT_eval_generated_profiles"].replace("dialogue_ID", dialogueID)

    json_reference_dialogue = load_json(metrics_json_template["in_folder_ChatGPT_generated_dialogues"])
    json_generated_dialogue = load_json(metrics_json_template["in_folder_ChatGPT_eval_generated_profiles"])

    # Create a copy of the original template:
    metrics_json_template_copy = copy.deepcopy(metrics_json_template)

    # Dict with the things to do for preprocessing texts:
    reference_dialogue_profilesDict = convert_profile_list2dict(json_reference_dialogue["profiles"], common_text_processor)
    generated_dialogue_profilesDict = convert_profile_list2dict(json_generated_dialogue["profiles"], common_text_processor)

    for metric_idx in range(len(metrics_json_template["metrics_profile"])):
        # Get information about the profiles to calculate the metric
        metric = metrics_json_template["metrics_profile"][metric_idx]
        print(">>>>> EVALUATING ", metric["metrics_name"], " <<<<<")
        metric_profiles = {}
        for profile_idx in range(len(metric["profiles"])):
            profile = metric["profiles"][profile_idx]
            profile_name = common_text_processor.preprocessing_text(profile["profile_name"])
            reference_profile_fields = reference_dialogue_profilesDict[profile_name]
            generated_profile_fields = generated_dialogue_profilesDict[profile_name]
            accumulative_metric_scores = []
            dict_profile_field_with_scores = {}
            for profile_field_name in profile["profile_fields_prompt"]:
                # Get ground truth field value
                profile_field_id = common_text_processor.preprocessing_text(profile_field_name)
                reference_value_field = common_text_processor.preprocessing_text(reference_profile_fields[profile_field_id])
                # Get generated answer
                try:
                    generated_value_field = common_text_processor.preprocessing_text(generated_profile_fields[profile_field_id])
                except KeyError:
                    generated_value_field = ""
                print("REFERENCE FIELD:", reference_value_field)
                print("GENERATED FIELD:", generated_value_field)
                # Calculate metrics comparing reference sentence/value & generated sentence/value
                metric_score = metrics_calculator(metric["metrics_name"], reference_value_field, generated_value_field,
                                                  extra_params=metric["metric_parameters"])
                #metrics_json_template["metrics_profile"][metric_idx]["profile_fields_prompt"][profile_field_name] = metric_score
                dict_profile_field_with_scores[profile_field_name] = float(np.around(metric_score, decimals=metrics_json_template["round_decimals"]))
                accumulative_metric_scores.append(metric_score)
            # Update JSON with metrics
            metrics_json_template_copy["metrics_profile"][metric_idx]["profiles"][profile_idx]["profile_fields_prompt"] = dict_profile_field_with_scores
            # Check whether it is necessary to calculate metrics at global level:
            if (("metric_global" in metric) and (bool(metric["metric_global"]))):
                if ("avg" in metric["metric_global"]):
                    metrics_json_template_copy["metrics_profile"][metric_idx]["metric_global"]["avg"] = float(np.around(np.mean(accumulative_metric_scores), decimals=metrics_json_template["round_decimals"]))
                if ("std" in metric["metric_global"]):
                    metrics_json_template_copy["metrics_profile"][metric_idx]["metric_global"]["std"] = float(np.around(np.std(accumulative_metric_scores),decimals=metrics_json_template["round_decimals"]))


    ########### SAVE ###############
    # Copy compared dialogues
    shutil.copy(metrics_json_template["in_folder_ChatGPT_generated_dialogues"], os.path.join(args.out_dir, "completedDialogue.json"))
    shutil.copy(metrics_json_template["in_folder_ChatGPT_eval_generated_profiles"], os.path.join(args.out_dir, "responseAsProfile.json"))

    # Save prompt/messages
    qualityMetrics_JSON = json.dumps(metrics_json_template_copy, indent=json_indent)
    with open(os.path.join(args.out_dir, "ProfileReconstructionQuality_metrics.json"), "w") as write_file:
        write_file.write(qualityMetrics_JSON)
