import os.path

import numpy as np
import pandas as pd
import string

import copy
# METRICS:


from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from src.metrics.CharactersiticMetrics import CharacteristicMetric
from src.utils.text_processor import extreme_processing
import math
from transformers import AutoTokenizer, AutoModelWithLMHead
import torch




class SubjectivityAnthropicMetric(CharacteristicMetric):
    def __init__(self, model_name = "subjectivity", loaded_model=None):
        super().__init__("subjectivity", ["single"], ["word", "utterance", "dialogue_from_utterances"], "")
        self.model = loaded_model
        print("   - Subjectivity: [0 to 1] - 1 stands for subjective and 0 for objective")
        self.utterances_scores = {}

    def process_and_call_metric_single(self, inputDialogue, analysis_level):
        final_results_metric = {}
        for subject in inputDialogue.keys():
            subjectUtterances = inputDialogue[subject]
            final_results_metric[subject] = {}
            aux_dict_scores = {}
            if (analysis_level == "word"):
                for idx_utterance in range(0, len(subjectUtterances)):
                    utterance = subjectUtterances[idx_utterance]
                    word_scores = {}
                    for word in utterance:
                        score_word = self.call_metric(word, "single")
                        word_scores[word] = score_word
                    aux_dict_scores[idx_utterance] = word_scores
            elif(analysis_level=="utterance"):
                for idx_utterance in range(0, len(subjectUtterances)):
                    utterance = subjectUtterances[idx_utterance]
                    score_utterance = self.call_metric(utterance, "single")
                    aux_dict_scores[idx_utterance] = {utterance:score_utterance}
            elif (analysis_level == "dialogue_from_utterances"):
                # Calculate avg std over utterances:
                if (not subject in self.utterances_scores.keys()):
                    # Extract results at utterance level
                    results_aux = self.process_and_call_metric_single(inputDialogue, "utterance")
                    self.utterances_scores = results_aux
                    aux_dict_scores = self.calculate_dialogue_metrics_from_utterances(subject)
                else:
                    aux_dict_scores = self.calculate_dialogue_metrics_from_utterances(subject)
            final_results_metric[subject] = aux_dict_scores
        return final_results_metric

    def calculate_dialogue_metrics_from_utterances(self, subject):
        subject_utterances = self.utterances_scores[subject]
        utterance_metrics = []
        aux_dict_scores = {}
        for idx_utterance in range(0, len(list(subject_utterances.values()))):
            utterance_metrics.append((list(list(subject_utterances.values())[idx_utterance].values())[0]))
        utterance_metrics = list(filter(None, utterance_metrics))
        for metric_name in ["avg", "std", "min", "max", "listValues"]:
            aux_dict_scores[metric_name] = self.statistics_calculator(metric_name, utterance_metrics)
        return aux_dict_scores

    def call_metric(self, inputText: list, selectedBehaviour: str):
        if (selectedBehaviour in self.singleOrDual):
            if (selectedBehaviour == "single"):
                return self.call_metric_single(inputText)

    def call_metric_single(self, inputText: list):
        testimonial = TextBlob(inputText)
        return testimonial.sentiment.subjectivity




class SentimentAnthropicMetric(CharacteristicMetric):
    def __init__(self, model_name="sentiment", loaded_model=None, data_access_key="compound"):
        super().__init__("sentiment", ["single"], ["word", "utterance", "dialogue_from_utterances"], "")
        print("   - Valence: [-1 to +1] : -1 stands for negative and +1 for positive valence")
        self.model = loaded_model
        self.data_access_key = data_access_key
        self.model = SentimentIntensityAnalyzer()
        self.utterances_scores = {}

    def process_and_call_metric_single(self, inputDialogue, analysis_level):
        final_results_metric = {}
        for subject in inputDialogue.keys():
            subjectUtterances = inputDialogue[subject]
            final_results_metric[subject] = {}
            aux_dict_scores = {}
            if (analysis_level == "word"):
                for idx_utterance in range(0, len(subjectUtterances)):
                    utterance = subjectUtterances[idx_utterance]
                    word_scores = {}
                    for word in utterance:
                        score_word = self.call_metric(word, "single")
                        word_scores[word] = score_word
                    aux_dict_scores[idx_utterance] = word_scores
            elif (analysis_level == "utterance"):
                for idx_utterance in range(0, len(subjectUtterances)):
                    utterance = subjectUtterances[idx_utterance]
                    score_utterance = self.call_metric(utterance, "single")
                    aux_dict_scores[idx_utterance] = {utterance: score_utterance}
            elif (analysis_level == "dialogue_from_utterances"):
                # Calculate avg std over utterances:
                if (not subject in self.utterances_scores.keys()):
                    # Extract results at utterance level
                    results_aux = self.process_and_call_metric_single(inputDialogue, "utterance")
                    self.utterances_scores = results_aux
                    aux_dict_scores = self.calculate_dialogue_metrics_from_utterances(subject)
                else:
                    aux_dict_scores = self.calculate_dialogue_metrics_from_utterances(subject)
            final_results_metric[subject] = aux_dict_scores
        return final_results_metric


    def calculate_dialogue_metrics_from_utterances(self, subject):
        subject_utterances = self.utterances_scores[subject]
        utterance_metrics = []
        aux_dict_scores = {}
        for idx_utterance in range(0, len(list(subject_utterances.values()))):
            utterance_metrics.append((list(list(subject_utterances.values())[idx_utterance].values())[0]))
        utterance_metrics = list(filter(None, utterance_metrics))
        for metric_name in ["avg", "std", "min", "max", "listValues"]:
            aux_dict_scores[metric_name] = self.statistics_calculator(metric_name, utterance_metrics)
        return aux_dict_scores

    def call_metric(self, inputText: list, selectedBehaviour: str):
        if (selectedBehaviour in self.singleOrDual):
            if (selectedBehaviour == "single"):
                return self.call_metric_single(inputText)


    def call_metric_single(self, inputText: list):
        # TextBlob(sentence).sentiment.polarity
        results = self.model.polarity_scores(inputText)[self.data_access_key]
        return results




class EmotionsAnthropicMetric(CharacteristicMetric):
    # Works only with Transformers 3.5.0
    def __init__(self, model_name = "mrm8488/t5-base-finetuned-emotion", loaded_model=None, loaded_tokenizer = None,
                 class_labels = ['joy', 'sadness', 'love', 'anger', 'fear', 'surprise'], th = 0.0):
        super().__init__("emotions_torch_t5", ["single"], ["word", "utterance", "dialogue_from_utterances"], "")
        self.model = loaded_model
        self.model_name = model_name
        self.tokenizer = loaded_tokenizer
        print("   - Emotion ("+model_name+"): [0 to 1 - softmax of emotions: "+str(class_labels)+"]")
        self.utterances_scores = {}
        self.class_labels = class_labels
        self.th = th

    def process_and_call_metric_single(self, inputDialogue, analysis_level):
        final_results_metric = {}
        for subject in inputDialogue.keys():
            subjectUtterances = inputDialogue[subject]
            final_results_metric[subject] = {}
            aux_dict_scores = {}
            if (analysis_level == "word"):
                for idx_utterance in range(0, len(subjectUtterances)):
                    utterance = subjectUtterances[idx_utterance]
                    word_scores = {}
                    for word in utterance:
                        score_word = self.call_metric(word, "single")
                        word_scores[word] = score_word
                    aux_dict_scores[idx_utterance] = word_scores
            elif(analysis_level=="utterance"):
                for idx_utterance in range(0, len(subjectUtterances)):
                    utterance = subjectUtterances[idx_utterance]
                    score_utterance = self.call_metric(utterance, "single")
                    aux_dict_scores[idx_utterance] = {utterance:score_utterance}
            elif (analysis_level == "dialogue_from_utterances"):
                # Calculate avg std over utterances:
                if (not subject in self.utterances_scores.keys()):
                    # Extract results at utterance level
                    results_aux = self.process_and_call_metric_single(inputDialogue, "utterance")
                    self.utterances_scores = results_aux
                    aux_dict_scores = self.calculate_dialogue_metrics_from_utterances(subject)
                else:
                    aux_dict_scores = self.calculate_dialogue_metrics_from_utterances(subject)
            final_results_metric[subject] = aux_dict_scores
        return final_results_metric

    def calculate_dialogue_metrics_from_utterances(self, subject):
        subject_utterances = self.utterances_scores[subject]
        empty_dict_valences = {}
        for c in self.class_labels:
            empty_dict_valences[c] = list()

        utterance_metrics = copy.deepcopy(empty_dict_valences)
        aux_dict_scores = dict.fromkeys(["avg", "std", "min", "max", "listValues"], copy.deepcopy(empty_dict_valences))
        for idx_utterance in range(0, len(list(subject_utterances.values()))):
            for valence_metric in self.class_labels:
                score = subject_utterances[idx_utterance][list(subject_utterances[idx_utterance].keys())[0]][valence_metric]
                utterance_metrics[valence_metric].append(score)

        # Extract statstics and remove nulls:
        for metric_name in ["avg", "std", "min", "max", "listValues"]:
            aux_dict = {}
            for valence_label in list(utterance_metrics.keys()):
                utterance_metrics[valence_label] = list(filter(None, utterance_metrics[valence_label]))
                aux_dict[valence_label] = self.statistics_calculator(metric_name, utterance_metrics[valence_label])
            aux_dict_scores[metric_name] = copy.deepcopy(aux_dict)
        return aux_dict_scores


    def call_metric(self, inputText: list, selectedBehaviour: str):
            if (selectedBehaviour in self.singleOrDual):
                if (selectedBehaviour == "single"):
                    return self.call_metric_single(inputText)

    def call_metric_single(self, inputText: list):
        if (self.model == None):
            tokenizer = AutoTokenizer.from_pretrained(self.model_name, return_tensors="pt")
            model = AutoModelWithLMHead.from_pretrained(self.model_name)
            self.tokenizer = tokenizer
            self.model = model
        else:
            model = self.model
            tokenizer = self.tokenizer
        # Extract emotion:
        labels = dict()
        for c in self.class_labels:
            labels[c] = list()

        class_ids = torch.LongTensor(tokenizer(list(labels), padding=True).input_ids)

        input_ids = tokenizer.encode(inputText + '</s>', return_tensors='pt')
        output = model.generate(input_ids=input_ids, return_dict_in_generate=True, output_scores=True,
                                min_length=class_ids.shape[1] + 1, max_length=class_ids.shape[1] + 1,
                                do_sample=False)

        # Get label without scores:
        # dec = [tokenizer.decode(ids) for ids in output["sequences"]]
        # label_aux = dec[0]

        # Scores & label
        scores = torch.stack(output.scores, dim=1).to("cpu")
        scores[:, :, tokenizer.all_special_ids] = torch.nan
        score_of_labels = scores.gather(dim=2, index=class_ids.T.expand(1, -1, -1))
        probabilities = score_of_labels.nanmean(dim=1).softmax(1)
        for p, c in zip(probabilities[0], self.class_labels):
            labels[c].append(p)
        response = self._parse_labels_response_list(labels)
        response = self._filter_labels_response_list(response)

        return response[0]




def anthropic_metrics_calculatorSingle(metric_name, dialogue, analysis_level, extra_params={}):
    if (metric_name == "subjectivity"):
        subjectivity = SubjectivityAnthropicMetric(**extra_params)
        final_score = subjectivity.process_and_call_metric_single(dialogue, analysis_level)
    elif (metric_name == "sentiment"):
        sentiment = SentimentAnthropicMetric(**extra_params)
        final_score = sentiment.process_and_call_metric_single(dialogue, analysis_level)
    elif (metric_name == "emotions_torch_t5"):
        emotionsProcessor = EmotionsAnthropicMetric(**extra_params)
        final_score = emotionsProcessor.process_and_call_metric_single(dialogue, analysis_level)
    else:
        print("Type of metric ", metric_name,
              " not-recognized. Try: ['subjectivity', 'sentiment']")
        final_score = -1
    return final_score




if __name__ == '__main__':
    subjective_sentence = "Ah, I know that painting! It's a beautiful piece. What emotions does it evoke in you?"
    subjective_sentence2 = "I hate artworks that have dogs on them"
    factual_sentence = "Post-Impressionism was a movement that emerged in the late 19th century, and it focused on the use of color and form to express emotions and ideas."
    factual_sentence2 = "banana"
    factual_sentence3 = "the flower is the seed-bearing part of a plant, consisting of reproductive organs (stamens and carpels) that are typically surrounded by a brightly coloured corolla (petals) and a green calyx (sepals)"
    #pos_analysis(datasets['ArtEmis'], group_cols=['painting', 'art_style'])
