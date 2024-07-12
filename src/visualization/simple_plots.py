import os.path

import pandas as pd
import matplotlib.pyplot as plt
import src.utils.loader_saver as load_saver
import numpy as np
# Check plotnine

def common_boxplot(data, xy_cols, rotation=0):
    fig1, ax1 = plt.subplots()
    ax1.set_title(xy_cols["title"])
    ax1.boxplot(data, positions=list(sorted(list(xy_cols['labels'].keys()))))
    ax1.set_xticks(list(xy_cols["labels"].keys()))
    ax1.set_xticklabels(list(xy_cols["labels"].values()), rotation=rotation)
    ax1.set_ylabel(xy_cols["y_title"])
    plt.tight_layout()
    return fig1,ax1

def violin_plot(data, xy_cols, rotation=0):
    fig1, ax1 = plt.subplots()
    ax1.set_title(xy_cols["title"])
    ax1.violinplot(data, positions=list(sorted(list(xy_cols['labels'].keys()))),
                   showmeans=True, showextrema=True)
    ax1.set_xticks(list(xy_cols["labels"].keys()))
    ax1.set_xticklabels(list(xy_cols["labels"].values()), rotation=rotation)
    ax1.set_ylabel(xy_cols["y_title"])
    plt.tight_layout()
    return fig1, ax1

def create_boxplots_YesNo(df, xy_cols):
    # Divide df in differnet values of X
    data = []
    df = df.astype({xy_cols["x"]: int})
    for values_data in list(sorted(list(xy_cols['labels'].keys()))):
        y = df.loc[df[xy_cols["x"]]==values_data][xy_cols["y"]].values
        y = y[~np.isnan(y)]
        data.append(y)
    common_boxplot(data, xy_cols)
    plt.show()


def create_boxplot_plusScatter(df, xy_cols, typeBoxplot="boxplot"):
    data = []
    df = df.astype({xy_cols["x"]: int})
    color_scatter = []
    x_scatter = []
    y_scatter = []
    x = 0
    for values_data in list(sorted(list(xy_cols['labels'].keys()))):
        indexes_y = list(df.loc[df[xy_cols["x"]] == values_data][xy_cols["y"]].index)
        # Data for boxplots
        y = df.iloc[indexes_y][xy_cols["y"]]
        y = y[~np.isnan(y)]
        data.append(y)
        # Data for scatter plot
        color_scatter+=list(df.iloc[list(y.index)][xy_cols["var_scatter"]].replace(xy_cols["color_scatter"]).values)
        x_scatter += [x]*len(y)
        y_scatter += list(y.values)
        x+=1
    if(typeBoxplot=="boxplot"):
        fig, ax = common_boxplot(data, xy_cols)
    elif(typeBoxplot=="violin"):
        fig,ax = violin_plot(data, xy_cols)
    else:
        fig, ax = common_boxplot(data, xy_cols)

    # Add scatter plot

    df_scatter = pd.DataFrame([])
    df_scatter["x"] = x_scatter
    df_scatter["y"] = y_scatter
    df_scatter["color"] = color_scatter
    for color in set(color_scatter):
        print("todo")
        df_color = df_scatter.loc[df_scatter["color"]==color]
        ax.scatter(df_color["x"], df_color["y"], c=color, label=xy_cols["label_scatter"][color])
    ax.legend()
    plt.show()


def create_boxplot_quality(df, xy_cols, rotation=30, save_path=""):
    data = []
    for value_data in list(sorted(list(xy_cols['labels'].keys()))):
        y = df[xy_cols['y'].replace("<field>", xy_cols['labels'][value_data])]
        y = y[~np.isnan(y)]
        data.append(y)
    common_boxplot(data, xy_cols, rotation=rotation)
    if(save_path==""):
        plt.show()
    else:
        plt.savefig(save_path)
        plt.close()



def create_histograms_YesNo(df, xy_cols, width = 0.20, division=2):
    print("")
    #fig = plt.subplots(figsize=(10, 7))

    simple_df = df[[xy_cols["x"],xy_cols["y"]]]
    cross_tab = pd.crosstab(simple_df[xy_cols["x"]], simple_df[xy_cols["y"]], margins=True)

    # Check that all the columns exist:
    if(len(cross_tab.columns)-1 < len(xy_cols["labels_y"])):
        # Add columns no included:
        for col_i in list(xy_cols["labels_y"].keys()):
            try:
                check = cross_tab[col_i]
            except KeyError:
                cross_tab.insert(col_i, col_i, np.zeros(len(cross_tab)))

    x_order_values = [xy_cols["labels_x"][i] for i in cross_tab.index.values[0:-1]]
    y_order_values = [xy_cols["labels_y"][i] for i in cross_tab.columns.values[0:-1]]
    df_to_plot = {}
    for index in range(len(y_order_values)):
        y_val = y_order_values[index]
        df_to_plot[y_val] = (cross_tab[index].values[0:-1])

    x = np.arange(len(x_order_values))  # the label locations
    multiplier = 1/len(x_order_values)
    fig, ax = plt.subplots(layout='constrained')
    for attribute, measurement in df_to_plot.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=2)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(" # Number of dialogues ")
    ax.set_xlabel(" -- Initial Anthropic Value in Profile -- ")
    ax.set_title(xy_cols["title"])
    ax.set_xticks(x + width, x_order_values)
    ax.legend(loc='upper left', ncols=len(y_order_values))
    ax.set_ylim(0, int((len(simple_df)/division)+(0.1*len(simple_df))))
    #ax.set_xticklabels(list(xy_cols["labels"].values()))
    plt.tight_layout()
    plt.show()




if __name__ == '__main__':
    ### PARAMETERS ###
    path_metrics = "../../0publicData/output_files/Metrics_v1/summaryMetrics.csv"
    path_profiles = "../../0publicData/input_files/0parameter_files/versions/v1/csvWithDialoguesCodesProfilesv1.csv"
    codes_json = "../../0publicData/input_files/0parameter_files/taxonomies_codes/v1/filename_codes_v1.json"
    profiles_df = pd.read_csv(path_profiles)
    codes_dict = load_saver.load_json(codes_json)
    df_metrics = pd.read_csv(path_metrics, sep=",", header=0)
    merged_df = pd.merge(profiles_df, df_metrics, on='DIALOGUE_ID')
    typeBoxplot = "violin"
    characteristic = "anthropic" # anthropic
    expertorChatbot = "EX_" # EX_  US_
    userOrcahtbot = "Expert" # Expert User
    statistic_val = "_avg" # _avg _max _min _std
    extra_info = "_YN_Evaluation"
    extra_info_OM = "_OM_Evaluation"
    n_assesments_in_characteristics = 2
    y_characteristics = {"anthropic": {"chatGPT_metrics":["EMOT_0_score"+extra_info, "OPINIONS_0_score"+extra_info],
                                       "y_title_chatgpt": [userOrcahtbot+" Express Emotions", userOrcahtbot+" Giving Opinions/Having preferences"],
                                       "y_labels_chatgpt": [{0: "No-Emot.", 1: "Yes-Emot."},
                                                            {0: "No-Opin./Pref.", 1: "Yes-Opin./Pref."}],

                                       "objective_metrics": ["sentiment", "subjectivity"],
                                       "y_title_objective_metrics":["Valence: [-1 to +1] : -1 negative, 0 neutral, and +1 positive", "Subjectivity: [0 to 1] - 1 stands for subjective and 0 for objective"]
                                       }
    }
    ### PARAMETERS ###



    ################### PLOTS BELOW ############################
    for idx in range(n_assesments_in_characteristics):
        # ChatGPT
        xy_boxplot_emot = {
                           "x":  expertorChatbot+characteristic+"_code_ORIGINAL"+extra_info,
                           "y":   expertorChatbot+y_characteristics[characteristic]["chatGPT_metrics"][idx],
                           "title":  y_characteristics[characteristic]["y_title_chatgpt"][idx],
                           "labels_y": y_characteristics[characteristic]["y_labels_chatgpt"][idx],
                           "labels_x": {0: "No-"+characteristic, 1: characteristic},
                       }
        create_histograms_YesNo(merged_df, xy_boxplot_emot)
        # Objective metrics:
        # xy_boxplot_emot = {"x": expertorChatbot + characteristic + "_code_ORIGINAL"+extra_info,
        #                    "y": y_characteristics[characteristic]["objective_metrics"][idx]+"_" + userOrcahtbot + statistic_val+extra_info_OM,
        #                    "labels": {0: "No-" + characteristic, 1: characteristic},
        #                    "title": userOrcahtbot +" "+ y_characteristics[characteristic]["objective_metrics"][idx] +" (" + statistic_val + ")",
        #                    "y_title": y_characteristics[characteristic]["y_title_objective_metrics"][idx],
        #                    "var_scatter": expertorChatbot + characteristic + "_code_GENERATED"+extra_info,
        #                    "color_scatter": {0.0: "b", 1.0: "r"},
        #                    "label_scatter": {"b": "No-" + characteristic + "-ChatGPT",
        #                                      "r": "Yes-" + characteristic + "-ChatGPT"},
        #                    }
        # create_boxplot_plusScatter(merged_df, xy_boxplot_emot, typeBoxplot=typeBoxplot)


    # ChatGPT summary:
    xy_boxplot_emot = {"x":  expertorChatbot+characteristic+"_code_ORIGINAL"+extra_info,
                       "y":  expertorChatbot+characteristic+"_code_GENERATED"+extra_info,
                       "title": userOrcahtbot+ " "+characteristic+" ("+y_characteristics[characteristic]["y_labels_chatgpt"][0][1]+" OR "
                                +y_characteristics[characteristic]["y_labels_chatgpt"][1][1]+")",
                       "labels_y": {0: "No-"+characteristic, 1: characteristic},
                       "labels_x": {0: "No-"+characteristic, 1: characteristic},
                       }
    create_histograms_YesNo(merged_df, xy_boxplot_emot)


    # ################ ProfileReconstructionQuality ##########################
    # #Select metric rows
    save_path = "/home/cristinalunaj/PycharmProjects/ASTOUND_DS2/0publicData/output_files/Metrics_v1/PLOTS/ProfileQuality"
    fields_per_profile = {
        "Painting_profile":["Painting_title", "Artist_name", "Typical_triggered_emotion_in_viewers", "Artistic_movement_or_school"],
        "User_profile": ["User_emotion", "User_role", "User_characteristic_1", "User_characteristic_2", "User_preferred_artistic_movement"],
        "Expert_profile": ["Expert_characteristic", "Expert_goal"]
    }
    # metircs = ["WER", "BLEU-1", "BLEU-4", "JaccardSim","accuracy", "levhensteinDist", "semanticSim"]

    for metric in ["WER", "BLEU-1", "BLEU-4", "JaccardSim","accuracy", "levhensteinDist", "semanticSim"]:
        wer_metrics = merged_df.loc[:, merged_df.columns.str.startswith(metric+'_')]
        for profile in ["Painting_profile", "User_profile", "Expert_profile"]:
            xy_boxplot_WER = {"x": fields_per_profile[profile],
                              "y": metric+"_"+profile+"--<field>",
                              "labels": dict(zip(range(len(fields_per_profile[profile])), fields_per_profile[profile])),
                              "title": metric+" - "+profile,
                              "y_title": metric}
            path2save = os.path.join(save_path, profile+"-"+metric+".png")
            create_boxplot_quality(wer_metrics, xy_boxplot_WER, rotation=90, save_path=path2save)
            # save plot:


