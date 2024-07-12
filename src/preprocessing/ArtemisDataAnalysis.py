import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import collections

def plot_hist(x_axis_vals, y_axis, title="", N=50):
    print("to do")
    x = range(0, N)
    fig = plt.figure(figsize=(30, 10))
    plt.bar(x, y_axis[0:N])
    plt.xticks(x, x_axis_vals[0:N], rotation=90)
    plt.title(title)
    plt.grid()
    plt.tight_layout()
    plt.show()


def get_top_artists(df_artemis_metadata,TOP_N=50):
    authors_df = pd.DataFrame([], columns=["author", "nPaintings", "artWorks"])
    total_paintings = 0
    for author_name in df_artemis_metadata["author"].unique():
        count_paintings_artist = df_artemis_metadata.loc[(df_artemis_metadata["author"] == author_name)][
            "painting_title"].unique()
        # author_dict[author_name] = len(count_paintings_artist)
        authors_df = authors_df.append(
            pd.DataFrame([[author_name, len(count_paintings_artist), str(list(count_paintings_artist))]], columns=["author", "nPaintings", "artWorks"]))
        total_paintings += len(count_paintings_artist)

    authors_df = authors_df.sort_values(by="nPaintings", ascending=False)
    authors_df = authors_df.reset_index(drop=True)
    plot_hist(authors_df["author"].values, authors_df["nPaintings"].values, title="Authors", N=TOP_N)
    return authors_df

def get_data_analysis_Artemis(df_path, df_genre_path, df_styles_path, df_wclasses_path, TOP_N = 50):
    df_artemis_metadata = pd.read_csv(df_path, sep=",", header=0)
    df_genre = pd.read_csv(df_genre_path, sep=",", header=0)
    df_styles = pd.read_csv(df_styles_path, sep=",", header=0)
    df_classes = pd.read_csv(df_wclasses_path, sep=",", header=0)

    df_classes["painting"] = df_classes["file"].str.split("/", expand=True, n=1)[1].str.split(".", expand=True)[0]
    df_classes["painting_title"] = df_classes["painting"].str.split("_", expand=True, n=1)[1]
    df_artemis_metadata["genre"] = "unk"

    df_artemis_metadata["author"] = df_artemis_metadata["painting"].str.split("_", expand=True, n=1)[0]
    df_artemis_metadata["painting_title"] = df_artemis_metadata["painting"].str.split("_", expand=True, n=1)[1]

    # group_by_paint_title = df_artemis_metadata.groupby(by = ["painting_title","author"])
    # distribution_authors = group_by_paint_title.size().groupby(level=1).max()
    # classes = np.load(df_classes_npy)
    genres_numbers = df_classes["genre"].unique()
    genres_names = df_genre[df_genre['ID'].isin(genres_numbers)]
    # Add genres in Artemis
    # for idx, row in df_artemis_metadata.iterrows():
    #     try:
    #         genre_of_painting_numb = df_classes.loc[df_classes["painting"]==row["painting"], "genre"].values[0]
    #         genre_name_idx = eval(genres_names.loc[genres_names["ID"]==genre_of_painting_numb, "art_style"].values[0])
    #         df_artemis_metadata.at[idx, 'genre'] = genre_name_idx
    #     except IndexError:
    #         print("Problems with picture: ", row["painting"])
    # #Save new Artemis with genre:
    # df_artemis_metadata.to_csv(out_df_path_artemis, sep=",", header=True, index=False)

    # N. Artworks of each painter (in total 1,119 artists) // 80.031 artworks
    authors_df = pd.DataFrame([], columns=["author", "nPaintings"])
    total_paintings = 0
    for author_name in df_artemis_metadata["author"].unique():
        count_paintings_artist = df_artemis_metadata.loc[(df_artemis_metadata["author"] == author_name)][
            "painting_title"].unique()
        # author_dict[author_name] = len(count_paintings_artist)
        authors_df = authors_df.append(
            pd.DataFrame([[author_name, len(count_paintings_artist)]], columns=["author", "nPaintings"]))
        total_paintings += len(count_paintings_artist)

    authors_df = authors_df.sort_values(by="nPaintings", ascending=False)
    authors_df = authors_df.reset_index(drop=True)

    plot_hist(authors_df["author"].values, authors_df["nPaintings"].values, title="Authors", N=TOP_N)

    # N. Artworks of each painting STYLE (in total 27 art-style)
    style_dict = {}
    genre_dict = {}
    for paint_title in df_artemis_metadata["painting_title"].unique():
        paintingStyle = \
        df_artemis_metadata.loc[(df_artemis_metadata["painting_title"] == paint_title)]["art_style"].unique()[0]
        # For art-style
        if (paintingStyle in style_dict.keys()):
            style_dict[paintingStyle] += 1
        else:
            style_dict[paintingStyle] = 1
        paintingGenre = \
        df_artemis_metadata.loc[(df_artemis_metadata["painting_title"] == paint_title)]["genre"].unique()[0]
        # For genre
        if (paintingGenre in genre_dict.keys()):
            genre_dict[paintingGenre] += 1
        else:
            genre_dict[paintingGenre] = 1

    # Styles processing:
    style_df = pd.DataFrame([])
    style_df["style"] = style_dict.keys()
    style_df["nPaintings"] = style_dict.values()

    style_df = style_df.sort_values(by="nPaintings", ascending=False)
    style_df = style_df.reset_index(drop=True)

    plot_hist(style_df["style"].values, style_df["nPaintings"].values, title="Style", N=27)
    # Genre processing:
    genre_df = pd.DataFrame([])
    genre_df["style"] = genre_dict.keys()
    genre_df["nPaintings"] = genre_dict.values()

    genre_df = genre_df.sort_values(by="nPaintings", ascending=False)
    genre_df = genre_df.reset_index(drop=True)

    plot_hist(genre_df["style"].values, genre_df["nPaintings"].values, title="Genre", N=11)
    genre_df = pd.DataFrame.from_dict(genre_dict)

def get_data_analysis_Artemis_v2(df_path, df_genre_path, df_styles_path, df_wclasses_path, TOP_N = 50):
    print("to do")


if __name__ == '__main__':
    # ARTEMIS V1
    df_path = "../../data/ARTEMIS/artemis_dataset_release_v0.csv"
    out_df_path_artemis = "../../data/ARTEMIS/artemis_dataset_release_v0_withGenre.csv"
    df_genre_path = "../../data/ARTEMIS/genre_codes.csv"
    df_styles_path = "../../data/ARTEMIS/artist_codes.csv"
    df_wclasses_path = "../../data/ARTEMIS/wclasses.csv"
    df_classes_npy = "../../data/ARTEMIS/classes.npy"
    #get_data_analysis_Artemis(df_path, df_genre_path, df_styles_path, df_wclasses_path, TOP_N=50)

    # ARTEMIS V2
    df_path = "../../data/ARTEMIS/V2/Contrastive.csv"

    df_artemis_metadata = pd.read_csv(df_path, sep=",", header=0)
    df_artemis_metadata["author"] = df_artemis_metadata["painting"].str.split("_", expand=True, n=1)[0]
    df_artemis_metadata["painting_title"] = df_artemis_metadata["painting"].str.split("_", expand=True, n=1)[1]

    print("to do")

    # get_data_analysis_Artemis(df_path, df_genre_path, df_styles_path, df_wclasses_path, TOP_N=50)











