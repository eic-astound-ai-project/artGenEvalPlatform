import abc
import numpy as np
class CharacteristicMetric(metaclass=abc.ABCMeta):
    def __init__(self, metric_name, singleOrDual, analysis_levels, data_access_key):
        """

        :param metric_name:
        :param singleOrDual:
        :param analysis_levels: List including all the different analysis levels that the metric accepts [word, utterance, dialogue]
        :param expected_input_type:
        """
        self.metric_name = metric_name
        self.singleOrDual = singleOrDual
        self.analysis_levels = analysis_levels
        self.data_access_key = data_access_key
        self.result = None
        self.th = None

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'call_metric_single') and
                callable(subclass.call_metric_single) or
                NotImplemented)

    @abc.abstractmethod
    def call_metric_single(self, inputText: list):
        """Calculate metric score from input text"""
        raise NotImplementedError

    def get_analysis_levels(self):
        return self.analysis_levels

    def _parse_labels_response_list(self, res):
        return [dict(zip(res, vals)) for vals in zip(*res.values())]

    def _filter_labels_response_list(self, res):
        return [{k: float(v) for k, v in d.items() if v > self.th} for d in res]

    def get_data_access_key(self):
        return self.data_access_key

    def statistics_calculator(self,statistic, list_values):
        if(len(list_values)<=0):
            return np.nan

        if (statistic == "avg"):
            result = np.mean(list_values)
        elif (statistic == "std"):
            result = np.std(list_values)
        elif (statistic == "min"):
            result = np.min(list_values)
        elif (statistic == "max"):
            result = np.max(list_values)
        else:
            result = list_values
        return result
