

from src.utils.loader_saver import load_json, save_json
from src.utils.text_processor import Text_processor, str_parser, splitWords
import re, os, shutil
import numpy as np
import copy
from src.metrics.anthropic_metrics import anthropic_metrics_calculatorSingle
from src.metrics.chatGPT_autoEval_metrics import metrics_YESNOcalculator




class DialogueProcessor:
    def __init__(self, dialogue_path, params_text_processor_path, dialogue_analysis_level, response_processor_path, keywordsSubjects=["Chatbot", "Human", "All"], dialogues_utterances_bySubjects=None):
        self.response_structure_json = load_json(response_processor_path)
        # Initialize text processor
        text_processor_params = load_json(params_text_processor_path)
        self.textProcessor = Text_processor(**text_processor_params["text_processor_params"])
        self.keywordsSubjects = keywordsSubjects
        self.dialogue_utterances_bySubjects = dialogues_utterances_bySubjects
        self.dialogue_analysis_level = dialogue_analysis_level
        self.dialogue = self.load_dialogue(dialogue_path)


    def get_dialogue_utterances_bySubjects(self):
        return self.dialogue_utterances_bySubjects

    def load_dialogue(self, dialogue_path):
        response = load_json(dialogue_path)
        for field2access in self.response_structure_json["content"]:
            response = response[field2access]
        return response

    def prepare_data(self):
        # Process dialogue/Filter words:
        processed_dialogue = self.textProcessor.preprocessing_text(self.dialogue)
        # Split dialogue per subjects:
        self.dialogue_utterances_bySubjects = self.parse_dialogue_byParticipants_byUtterance(self.dialogue)
        # Process according to the analysis level:
        analisys_level_dict = self.process_by_analysis_levels()
        return analisys_level_dict

    def parse_dialogue_byParticipants_byUtterance(self, dialogue: str):
        participants_utterances_dict = {"All":[]}
        for subj in set(self.keywordsSubjects).difference(["All"]):
            p = re.compile(r'(?<=' + subj + '[: -,])(.*)')
            participants_utterances_dict[subj] = p.findall(dialogue)
        # Check what to do with All to take the whole dialogue .. :)
        if(not "All" in self.keywordsSubjects):
            del participants_utterances_dict["All"]
        else:
            dialogue_fragments = dialogue.split("\n")
            participants_utterances_dict["All"] = dialogue_fragments
        return participants_utterances_dict

    def process_by_analysis_levels(self):
        analisys_level_dict = {}
        if (self.dialogue_analysis_level == "word"):
            # get words from lists
            for subject in self.keywordsSubjects:
                analisys_level_dict[subject] = {}
                aux_dict = {}
                for utterance_idx in range(len(self.dialogue_utterances_bySubjects[subject])):
                    sentence = self.dialogue_utterances_bySubjects[subject][utterance_idx]
                    sentence_words = str_parser(sentence.strip(), parser=" ")
                    aux_dict[utterance_idx] = sentence_words
                analisys_level_dict[subject] = aux_dict
        elif (self.dialogue_analysis_level == "utterance"):
            analisys_level_dict = self.dialogue_utterances_bySubjects
        elif (self.dialogue_analysis_level == "dialogue"):
            print("by now > same processing than utternace")
            analisys_level_dict = self.dialogue_utterances_bySubjects
        elif (self.dialogue_analysis_level == "dialogue_from_utterances"):
            print("by now > same processing than utternace")
            analisys_level_dict = self.dialogue_utterances_bySubjects
        else:
            print("ELSE > same processing than utternace")
            analisys_level_dict = self.dialogue_utterances_bySubjects
        return analisys_level_dict


###############################################



def main_ethical_metrics(args, dialogueID, json_indent=4):
    # Load dialogue & add ID
    metrics_json_template = load_json(args.dialogueJSON)
    metrics_json_template["dialogue_ID"] = dialogueID

    #Create text processor for all the sentences:
    text_processor_params = load_json(metrics_json_template["params_text_processor_path"])
    common_text_processor = Text_processor(**text_processor_params["text_processor_params"])

    # Update values:
    metrics_json_template["in_folder_ChatGPT_generated_dialogues"] = metrics_json_template[
        "in_folder_ChatGPT_generated_dialogues"].replace("dialogue_ID", dialogueID)
    if("in_folder_ChatGPT_generated_YesNoMetrics" in metrics_json_template):
        metrics_json_template["in_folder_ChatGPT_generated_YesNoMetrics"] = metrics_json_template[
            "in_folder_ChatGPT_generated_YesNoMetrics"].replace("dialogue_ID", dialogueID)

    # Processed Dialogue:
    dict_with_all_metrics = {}
    for analysis_level in metrics_json_template["metrics_analysis_level"]:
        dilogue_processor = DialogueProcessor(metrics_json_template["in_folder_ChatGPT_generated_dialogues"],
                          metrics_json_template["params_text_processor_path"], analysis_level,
                          metrics_json_template["response_parser_params"],keywordsSubjects=metrics_json_template["metrics_analyzed_subjects"],
                          dialogues_utterances_bySubjects=None)

        dialogueAsDict = dilogue_processor.prepare_data()
        # Calculate metrics:
        for metric_idx in range(len(metrics_json_template["metrics_profile"])):
            # Get information about the profiles to calculate the metric
            metric = metrics_json_template["metrics_profile"][metric_idx]
            print(">>>>> EVALUATING ", metric["metric_name"], " <<<<<")


            if (metrics_json_template["type_metrics"] == "anthropic"):
                metric_scores = anthropic_metrics_calculatorSingle(metric["metric_name"],
                                                                 dialogueAsDict, analysis_level=analysis_level,
                                                                 extra_params=metric["metric_parameters"])

            elif (metrics_json_template["type_metrics"] == "anthropicYesNo"):
                metric_scores = metrics_YESNOcalculator(metric["metric_name"],metric,
                                                                 dialogueAsDict, analysis_level=analysis_level,
                                                                 response = metrics_json_template["in_folder_ChatGPT_generated_YesNoMetrics"],
                                                                 text_processor = common_text_processor,
                                                                 extra_params=metric["metric_parameters"])

            if(not metric["metric_name"] in dict_with_all_metrics.keys()):
                dict_with_all_metrics[metric["metric_name"]] = {}
            dict_with_all_metrics[metric["metric_name"]][analysis_level] = metric_scores
            print("to do")

    try:
        shutil.copy(metrics_json_template["in_folder_ChatGPT_generated_dialogues"],
                    os.path.join(args.out_dir, dialogueID+"_Dialogue.json"))
    except IsADirectoryError:
        pass
    save_json(dict_with_all_metrics, os.path.join(args.out_dir, dialogueID+"_"+metrics_json_template["type_metrics"]+"_metrics.json"), json_indent)




