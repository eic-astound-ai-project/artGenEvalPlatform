import pandas as pd
import numpy as np
from src.preprocessing.ArtemisDataAnalysis import get_top_artists
import random, os
from src.utils.loader_saver import load_json, save_json
import itertools
from itertools import product
from src.utils.args_utils import seed_libs



def createCSV_Artemis(path_artemis_DS, out_df_path_artemis):
    df_artemis_metadata = pd.read_csv(path_artemis_DS, sep=",", header=0)
    df_artemis_metadata["author"] = df_artemis_metadata["painting"].str.split("_", expand=True, n=1)[0]
    df_artemis_metadata["painting_title"] = df_artemis_metadata["painting"].str.split("_", expand=True, n=1)[1]

    # GET MODE OF EMOTIONS
    # group by painting title:
    df_artemis_collapsed = pd.DataFrame([],
                                        columns=list(df_artemis_metadata.columns) + ["mode_emotions", "second_emotions",
                                                                                     "all_emotions", "emotion_consensus"])

    for painting_title, df_painting in df_artemis_metadata.groupby(by="painting_title"):
        if (len(df_painting["art_style"].unique()) > 1 or len(df_painting["author"].unique()) > 1):
            print("Possible error in painting with name: ", painting_title)
            continue

        all_emotions = df_painting["emotion"].value_counts().to_dict()
        all_emotions_reverse = {}
        for k, v in all_emotions.items():
            all_emotions_reverse.setdefault(v, []).append(k)
        sorted_keys = sorted(all_emotions_reverse.keys(), reverse=True)
        primary_emotions = all_emotions_reverse[sorted_keys[0]]
        if (len(all_emotions_reverse) > 1):
            second_emotions = all_emotions_reverse[sorted_keys[1]]
        else:
            second_emotions = []
        # df_artemis_collapsed[]
        df_aux = df_painting.head(n=1)
        df_aux["mode_emotions"] = str(primary_emotions)
        df_aux["second_emotions"] = str(second_emotions)
        df_aux["all_emotions"] = str(all_emotions)
        df_aux["emotion_consensus"] = sorted_keys[0]/len(df_painting)
        df_artemis_collapsed = df_artemis_collapsed.append(df_aux)

    # Save dataset
    df_artemis_collapsed = df_artemis_collapsed.reset_index(drop=True)
    df_artemis_collapsed.to_csv(out_df_path_artemis, sep=";", header=True, index=False)





def get_code(file_codes_json, key_name, code2check):
    # recover codes:
    if (key_name in file_codes_json[code2check].keys()):
        code_author = file_codes_json[code2check][key_name]["code"]
    else:
        # get next value:
        last_val = int(file_codes_json[code2check]["last_idx"])
        file_codes_json[code2check][key_name] = {"code": str(last_val).zfill(6), "value": key_name}
        file_codes_json[code2check]["last_idx"] = str(last_val + 1).zfill(6)
        code_author = str(last_val).zfill(6)
    return code_author, file_codes_json

def get_value(file_codes_json, key_name, code2check):
    # recover values:
    if (key_name in file_codes_json[code2check].keys()):
        value_author = file_codes_json[code2check][key_name]["value"]
    else:
        # get next value:
        print("error??")
        value_author = -1
    return value_author




######################## EXCLUSIVE FOR VERSION 0 BEHAVIOUR ###########################
def select_artworksv0(df_top_artists,df_artemis_metadata, list_emotions_artemis, out_path, ntop_artists=100,
                      N_artworks2select=24):
    # Select list of most popular artists
    top_artists = list(df_top_artists["author"])[0:ntop_artists]

    # Order by consensus:
    df_artemis_sortedbyConsensus = df_artemis_metadata.sort_values(by="emotion_consensus", ascending=False)
    df_artemis_sortedbyConsensus = df_artemis_sortedbyConsensus.reset_index(drop=True)

    # Select artworks
    selected_artworks = pd.DataFrame([], columns=df_artemis_sortedbyConsensus.columns)
    count_emotions_uniform_distribut = dict.fromkeys(list_emotions_artemis, 0)
    for i, row in df_artemis_sortedbyConsensus.iterrows():
        mode_emot = random.choice(eval(row["mode_emotions"]))
        author = row["author"]
        # Restrictions/Requirements v0
        # 0. Maximum number of artworks = 20 (aprox)
        # 1. Balance in emotions (ignoring 'something else' emotion)
        # 2. artist is in list of top artists(the most popular in this DS)
        if (len(selected_artworks) == N_artworks2select): break
        if (not (mode_emot in list_emotions_artemis)): continue
        if ((count_emotions_uniform_distribut[mode_emot] < max_artworks_per_emotion)
                and (author in top_artists)):
            selected_artworks = selected_artworks.append(row)
            # Upate
            count_emotions_uniform_distribut[mode_emot] += 1
    # Save final selected artworks
    selected_artworks = selected_artworks.reset_index()
    selected_artworks.to_csv(out_path, sep=";", header=True, index=False)
    return selected_artworks



def complete_profile_paintingv0(df2complete, profile, selectedArtworks, file_codes, initial_code = "", human_code = "HP"):
    prefix = "PP_"
    new_cols_values = list(profile["values"].values())
    pre_res = [prefix + s for s in new_cols_values]
    df2complete[list(profile["values"].keys())] = selectedArtworks[list(profile["values"].keys())]
    df2complete.columns = pre_res
    df2complete["DIALOGUE_ID_aux"] = initial_code
    df2complete[human_code+"_emotion_code"] = ""
    new_df = pd.DataFrame([])
    for i, row in df2complete.iterrows():
        emotion_mode = random.choice(eval(row["PP_mode_emotions"]))
        possible_second_emot = random.choice(eval(row["PP_mode_emotions"]) + eval(row["PP_second_emotions"]) + ["neutral"])
        row["PP_mode_emotions"] = eval(row["PP_mode_emotions"])[0]
        for human_emotion in list(set(["neutral", emotion_mode, possible_second_emot])):
            df2complete.at[i,"PP_emotion_code"] = emotion_mode
            df2complete.at[i,human_code+"_emotion_code"] = human_emotion

            # CODES
            artwork_name = row["PP_artwork_code"]
            author_name = row["PP_author_code"]
            artStyle_name = row["PP_artStyle_code"]

            code_author, file_codes = get_code(file_codes, author_name, "author_code")
            code_artwork, file_codes = get_code(file_codes, artwork_name, "artwork_code")
            code_artStyle, file_codes = get_code(file_codes, artStyle_name, "artStyle_code")
            code_HP_emotion, file_codes = get_code(file_codes, human_emotion, "emotion_code")

            df2complete.at[i,"DIALOGUE_ID_aux"] = "PP--"+file_codes["artwork_code"]["key_id"]+code_artwork+"_"+\
                                              "PP--"+file_codes["author_code"]["key_id"]+code_author+ "_"+\
                                              "PP--"+file_codes["artStyle_code"]["key_id"] + code_artStyle+"_"+ \
                                              human_code+"--"+file_codes["emotion_code"]["key_id"] + code_HP_emotion+"_"

            new_df = new_df.append(pd.DataFrame([row.values], columns=row.keys()))
    new_df = new_df.reset_index(drop=True)
    return new_df, file_codes



def complete_profile_chatbotv0(df2complete, profile, codes_json, role_extra_code = "_0", chatbot_code = "CP", human_code = "HP"):
    list_values = []
    keys = []
    for dict_kv in profile["values"]:
        list_values.append(dict_kv["values"])
        keys.append(dict_kv["key_code"])
    combination_values = pd.DataFrame(list(product(*list_values)), columns=keys)
    combination_values["role_code"] = combination_values["goal_code"]+role_extra_code
    combination_values["DIALOGUE_ID_otherProfiles"] = ""
    # Get each code
    for i, row in combination_values.iterrows():
        # Chatbot
        #if("anthropic_code" in list(row.keys())):
        code_antrophic, codes_json = get_code(codes_json, row["anthropic_code"], "anthropic_code")
        code_goal, codes_json = get_code(codes_json, row["goal_code"], "goal_code")
        # Human
        code_toxic, codes_json = get_code(codes_json, row["toxicity_code"], "toxicity_code")
        code_bias, codes_json = get_code(codes_json, row["bias_code"], "bias_code")
        code_role, codes_json = get_code(codes_json, row["role_code"], "role_code")

        # Chatbot
        combination_values.at[i, "goal_code"] = get_value(codes_json, row["goal_code"], "goal_code")
        combination_values.at[i, "anthropic_code"] = get_value(codes_json, row["anthropic_code"], "anthropic_code")
        # Human
        combination_values.at[i, "toxicity_code"] = get_value(codes_json, row["toxicity_code"], "toxicity_code")
        combination_values.at[i, "bias_code"] = get_value(codes_json, row["bias_code"], "bias_code")
        combination_values.at[i, "role_code"] = get_value(codes_json, row["role_code"], "role_code")

        combination_values.at[i, "DIALOGUE_ID_otherProfiles"] = chatbot_code+"--" + codes_json["anthropic_code"]["key_id"] + code_antrophic + "_" + \
                                           chatbot_code+"--" + codes_json["goal_code"]["key_id"] + code_goal + "_" + \
                                           human_code+"--" + codes_json["toxicity_code"]["key_id"] + code_toxic + "_" + \
                                           human_code+"--" + codes_json["bias_code"]["key_id"] + code_bias + "_" + \
                                           human_code+"--" + codes_json["role_code"]["key_id"] + code_role + "_"

    # Create all the combinations of each row
    new_df = pd.DataFrame([])
    for i, row in df2complete.iterrows():
        for j,rowAnthrGoal in combination_values.iterrows():
            # Chatbot
            row[chatbot_code+"_anthropic_code"] = rowAnthrGoal["anthropic_code"]
            row[chatbot_code+"_goal_code"] = rowAnthrGoal["goal_code"]
            # Human
            row[human_code+"_toxicity_code"] = rowAnthrGoal["toxicity_code"]
            row[human_code+"_bias_code"] = rowAnthrGoal["bias_code"]
            row[human_code+"_role_code"] = rowAnthrGoal["role_code"]
            # Update Dialogue ID:
            row["DIALOGUE_ID"] = row["DIALOGUE_ID_aux"]+rowAnthrGoal["DIALOGUE_ID_otherProfiles"]
            new_df = new_df.append(pd.DataFrame([row.values], columns=row.keys()))
    new_df = new_df.reset_index(drop=True)
    return new_df, codes_json



def complete_profile_human():
    print("to do")



if __name__ == '__main__':
    ######################## START PARAMETERS INITIALIZATION#################################################
    version = "v1"
    previous_version = "v0"
    # Previous versin of file code
    file_codes_path = "../../../0publicData/input_files/0parameter_files/taxonomies_codes/v0/filename_codes_v0.json"
    #### ARTEMIS RELATED ####
    path_artemis_DS = "../../../data/ARTEMIS/artemis_dataset_release_"+version+".csv"
    in_df_path_artemis = "../../../data/ARTEMIS/artemis_dataset_collapsed_CLJ.csv"
    out_df_path_artists_artWorks = "../../../data/ARTEMIS/artemis_dataset_artist_artworks"+version+".csv"

    out_df_versionx_selectedArtemisArtworks = "../../../data/ARTEMIS/artemis_artworks_perVersion/"+version+"/artemis_selecetedArtworks"+version+".csv"
    os.makedirs("../../../data/ARTEMIS/artemis_artworks_perVersion/"+version, exist_ok=True)
    max_artworks_per_emotion = 25 ## * num emotions
    ### TEMPLATES CODES ###
    ### OUTPUT OF GENERATED CSV FILE WITH THE PROFILES:
    out_path_version0_completedProfiles = "../../../0publicData/input_files/0parameter_files/versions/"+version+"/csvWithDialoguesCodesProfiles"+version+".csv"
    os.makedirs("../../../0publicData/input_files/0parameter_files/versions/"+version, exist_ok=True)
    random_seed = 2020
    chatbot_code = "EX"
    human_code = "US"

    ### SPECIFIC PARAMETERS FOR THE VERSION ###
    ntop_artists = 500
    list_emotions_artemis = ['excitement','amusement','disgust','awe','contentment','sadness','fear','anger'] # 'something else',
    art_styles = ["Post Impressionism","Expressionism","Impressionism"
    ,"Northern Renaissance","Realism","Romanticism","Symbolism"
    ,"Art Nouveau Modern","Naive Art Primitivism","Baroque","Rococo"
    ,"Abstract Expressionism","Cubism","Color Field Painting","Pop Art"
    ,"Pointillism","Early Renaissance","Ukiyo e","Mannerism Late Renaissance"
    ,"High Renaissance","Fauvism","Minimalism","Action painting"
    ,"Contemporary Realism","Synthetic Cubism","New Realism"
    ,"Analytical Cubism"] # 27 artstyles
    # 8 emotions

    N_artworks2select = len(list_emotions_artemis)*max_artworks_per_emotion # 8 emotions in artemis * number of artwork per emotion
    #version = int(version.replace("v", ""))
    turns_uniform_distrib = {"low":15, "high":20}
    ##
    # Create combinations of other_profiles - matching with codes in:
    #  '../0publicData/input_files/DialogueGeneration/parameter_files/filename_codes.json'
    # Profiles from lists:
    anthropic_chatb = {"key_code":"anthropic_code",
                "values": ["no_anthropic", "anthropic"]}
    goals_chatb = {"key_code":"goal_code",
             "values": ["ToD", "Descriptive_Informative"]}
    toxicity_human = {"key_code":"toxicity_code",
                "values": ["no_toxic", "toxic"]}
    bias_human = {"key_code":"bias_code",
            "values":["no_bias"]} #"female_chauv", "male_chauv"


    # Profiles with non-regular processing:
    human_emotion_values = {"key_code": "emotion_code",
                            "csvFields":["mode_emotions", "second_emotions"],
                            "extra_values":["neutral"]}

    painting_profile = {"key_code": "painting_profile",
                        "values": {"painting_title":"artwork_code",
                                   "author": "author_code",
                                   "all_emotions": "all_emotions",
                                   "mode_emotions": "mode_emotions",
                                   "second_emotions": "second_emotions",
                                   "art_style": "artStyle_code"}}

    chatbot_human_profile = {"key_code": "chatbot_profile",
                        "values": [anthropic_chatb,goals_chatb, toxicity_human, bias_human] # bias
                       }
    # human_profile = {"key_code": "human_profile",
    #                    "values": [toxicity, bias]
    #                    }

    ########################END PARAMETERS INITIALIZATION#################################################


    ############# CODE STARTS BELOW #############

    ######### OPEN/PREPARE FILES ############################################
    # Prepare CSV collapsing emotions
    #createCSV_Artemis(path_artemis_DS, in_df_path_artemis)
    seed_libs(random_seed)
    df_artemis_metadata = pd.read_csv(in_df_path_artemis, sep=";", header=0)

    #Create CSV with top artists
    df_artist_nartworks = get_top_artists(df_artemis_metadata, ntop_artists)
    df_artist_nartworks.to_csv(out_df_path_artists_artWorks, sep=";", header=True, index=False)
    df_top_artists = pd.read_csv(out_df_path_artists_artWorks, sep=";", header=0)

    ########################### VERSIONS ##############################
    # Select Artemis Artworks - vx
    # selected_artworks = select_artworksv0(df_top_artists, df_artemis_metadata, list_emotions_artemis,
    #                                       out_df_versionx_selectedArtemisArtworks,
    #                                       ntop_artists=ntop_artists,
    #                                       N_artworks2select=N_artworks2select)
    selected_artworks = pd.read_csv(out_df_versionx_selectedArtemisArtworks, sep=";", header=0)
    ######################### CREATE GENERAL CSV OF EACH VERSION ######################

    ######## START GENERATING DIALOGUES PARAMETERS/COMBINATORIA #########
    # expected_n_dialogues = N_artworks2select*len(anthropic["values"])*\
    #               len(goals["values"])*len(toxicity["values"])*len(bias["values"])*\
    #               (len(human_emotion_values["csvFields"])+len(human_emotion_values["extra_values"]))
    # print("EXPECTED DIALOGUES: ", str(expected_n_dialogues))
    # OTHER PARAMETERS.


    file_codes = load_json(file_codes_path)
    df_final = pd.DataFrame([])
    df_final,file_codes = complete_profile_paintingv0(df_final, painting_profile, selected_artworks, file_codes, initial_code=version, human_code = human_code)
    df_final, file_codes = complete_profile_chatbotv0(df_final, chatbot_human_profile, file_codes, chatbot_code = chatbot_code, human_code = human_code)
    real_n_dialogues = len(df_final)
    turns_uniform_distrib["size"] = real_n_dialogues
    n_turns_list = np.random.randint(**turns_uniform_distrib)
    random_art_styles = np.random.randint(low=0, high=len(art_styles), size=real_n_dialogues)
    name_art_styles = [art_styles[i] for i in random_art_styles]
    print("FINAL DIALOGUES: ", str(real_n_dialogues))
    df_final[human_code+"_artStyle_code"] = name_art_styles
    df_final["DG_turns"] = n_turns_list
    # Save file_codes
    save_json(json_data=file_codes, path2save=file_codes_path.replace(previous_version, version), json_indent=4)
    # Save list of artworks:
    df_final.to_csv(out_path_version0_completedProfiles, header=True, index=False)
    print("LENGTH = # DIALOGUES: ", str(len(df_final)))





