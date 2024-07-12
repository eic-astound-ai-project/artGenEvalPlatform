from src.utils.text_processor import convert_profile_list2dict
from src.utils.loader_saver import load_json



###################### YES/NO ANSWERS ########################
def metrics_YESNOcalculator(metric_name, metric_template, dialogue, analysis_level, response, text_processor, extra_params={}):
    if (metric_name == "anthropicYesNo"):
        print("")
        profilesAslist = convert_profile_list2dict(metric_template["profiles"], text_processor)
        final_score = YesNoMetrics(response=response, profilesAslist=profilesAslist, text_processor=text_processor, **extra_params)


    else:
        print("Type of metric ", metric_name,
              " not-recognized. Try: ['anthropicYesNo', 'sentiment']")
        final_score = -1
    return final_score


def check_original_profile(subject, codes_json, profilesAslist, text_processor, keyname_features, value2get_feature):
    # Cehck profile to find:
    subject_profile = text_processor.preprocessing_text(codes_json["profile_code"][subject]["value"])
    codes2check = set(codes_json[keyname_features[subject]].keys()).difference(set(["last_idx", "key_id"]))
    value = -1

    for field in list(profilesAslist[subject_profile].keys()):
        # Check if this value is part of the expected keyname_feature
        valueFeature = profilesAslist[subject_profile][field]
        for code in codes2check:
            predefinedValue = codes_json[keyname_features[subject]][code]["value"]
            if(predefinedValue==valueFeature):
                # Get value:
                value = codes_json[keyname_features[subject]][code][value2get_feature[subject]]
                break
    return value


def recovering_YesNo_metrics():
    print("to do")



def YesNoMetrics(response, profilesAslist, text_processor, subjectCodes, concepts2concat4metric, operator2concat4metric,
                 additional_keys2report, keyname_features, value2get_feature, path_filename_codes):

    response_template = load_json(response)
    codes_json = load_json(path_filename_codes)
    response_keys_values = list(response_template["profiles"][0].keys())
    completedProfiles = dict.fromkeys(subjectCodes, {})
    for subject in subjectCodes:
        fields2return = dict.fromkeys(concepts2concat4metric+additional_keys2report, {"score": -1, "reliability": -1})

        # Initialize with the neutral initializer :)

        if (operator2concat4metric == "OR"):
            whole_concept = False
            neutral_element = False
        elif (operator2concat4metric == "AND"):
            whole_concept = True
            neutral_element = True
        else:
            print("NOT RECOGNIZED OPERATOR: ", operator2concat4metric, " . Try: ['OR','AND'] ")

        for concept in concepts2concat4metric+additional_keys2report:
            # Check metrics with both
            key_concept1 = subject+"_"+concept
            not_key_concept1 = subject+"_NOT_"+concept
            ##### 1. RELIABILITY & recovering when some features are lost in the automatic eval #####

            if((not key_concept1 in response_keys_values) and (not_key_concept1 in response_keys_values)):
                reliability = -1
                # Recover Yes version from negative of Not version:
                response_template["profiles"][0][key_concept1] = int(not (response_template["profiles"][0][not_key_concept1]))
            elif (not_key_concept1 in response_keys_values):
                reliability = check_reliability(response_template["profiles"][0][key_concept1],
                                                response_template["profiles"][0][not_key_concept1])
            else:
                reliability = -1
            # Update reliability and sc
            try:
                score = response_template["profiles"][0][key_concept1]
            except KeyError: # In case of errors in the generation > still return a result
                score = neutral_element

            ###### 2. SCORE #####
            dict_score_reliability = {"score":score,
                                      "reliability": int(reliability)}
            fields2return[concept] = dict_score_reliability
            #### WHOLE CONCEPT ####
            if(not(concept in additional_keys2report)):
                if(operator2concat4metric=="OR"):
                    whole_concept = whole_concept or score
                elif(operator2concat4metric=="AND"):
                    whole_concept = whole_concept and score
        fields2return[keyname_features[subject]+"_GENERATED"] = int(whole_concept)

        ## Compare with original profile
        fields2return[keyname_features[subject] + "_ORIGINAL"] = check_original_profile(subject, codes_json, profilesAslist, text_processor, keyname_features, value2get_feature)
        fields2return[keyname_features[subject] + "_MATCH_ORIGINAL_AND_GENERATED"] = (fields2return[keyname_features[subject] + "_ORIGINAL"] == fields2return[keyname_features[subject]+"_GENERATED"])
        completedProfiles[subject] = fields2return
    return completedProfiles


def check_reliability(concept1, notconcept1):
    return (concept1 and not notconcept1)

