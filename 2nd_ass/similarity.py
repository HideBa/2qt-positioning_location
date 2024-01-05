import os

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.manifold import MDS
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
import plotly.graph_objects as go


def read_access_point(dir_path, ssid="eduroam"):
    data_dict = {}
    for root, _, files in os.walk(dir_path):
        if "accesspoint.txt" in files:
            with open(os.path.join(root, "accesspoint.txt"), "r") as f:
                df = pd.read_csv(f, delimiter="\t")
                df.columns = [to_snake_case(col) for col in df.columns]
                df.rename(columns={df.columns[0]: "timestamp"}, inplace=True)
                try:
                    df.drop(
                        [
                            "vendor",
                            "connected_ap",
                            "quality",
                            "station_count",
                            "frequency",
                            "position",
                            "access_point_name",
                            "info",
                            "adapter",
                        ],
                        axis=1,
                        inplace=True,
                    )
                except KeyError:
                    print("invalid file")
                    continue
                filtered_df = df[df["ssid"].str.contains(ssid, na=False)]
                data_dict[root.split("/")[-1]] = filtered_df
    return data_dict


def to_snake_case(s):
    return s.lower().replace(" ", "_")


def calc_statistics_each_macaddress(data_dict):
    avg_signal_strength = {}
    for room_name, df in data_dict.items():
        avg_signal_strength[room_name] = df.groupby("mac_address")[
            "signal_strength"
        ].mean()
    return avg_signal_strength


def calculate_cosine_similarity(fingerprint_dict):
    mac_address = set()
    for df in fingerprint_dict.values():
        mac_address.update(df.index)
    mac_address = sorted(mac_address)

    for room_name, df in fingerprint_dict.items():
        fingerprint_dict[room_name] = df.reindex(mac_address).fillna(0)

    vectors = {room_name: df.values for room_name, df in fingerprint_dict.items()}
    room_names = list(fingerprint_dict.keys())
    matrix = cosine_similarity([vectors[room] for room in room_names])

    similarity_df = pd.DataFrame(matrix, index=room_names, columns=room_names)
    return similarity_df


def calculate_knn_similarity(fingerprint_dict):
    mac_address = set()
    for df in fingerprint_dict.values():
        mac_address.update(df.index)
    mac_address = sorted(mac_address)

    for room_name, df in fingerprint_dict.items():
        fingerprint_dict[room_name] = df.reindex(mac_address).fillna(0)

    vectors = {room_name: df.values for room_name, df in fingerprint_dict.items()}
    room_names = list(fingerprint_dict.keys())
    X = [vectors[room] for room in room_names]

    print("X shape: ", len(X), len(X[0]))
    # Calculate KNN similarity
    nbrs = NearestNeighbors(metric="cosine", algorithm="brute")
    nbrs.fit(X)
    distances, indices = nbrs.kneighbors(X)

    similarity_matrix = 1 - distances
    similarity_df = pd.DataFrame(
        similarity_matrix, index=room_names, columns=room_names
    )
    return similarity_df


def sort_by_similarity(similarity_series, top_n=10):
    sorted_similarities = similarity_series.sort_values(ascending=False)
    sorted_similarities = sorted_similarities.drop(
        sorted_similarities.index[0]
    )  # exclude itself
    return sorted_similarities.head(top_n)


def find_similar_room(room_name, data_dir="./2nd_ass/data", outdir="./2nd_ass/result"):
    data_dict = read_access_point(data_dir)
    signal_strength_stat = calc_statistics_each_macaddress(data_dict)
    similarity_df = calculate_cosine_similarity(signal_strength_stat)
    # knn_similarity_df = calculate_knn_similarity(signal_strength_stat)

    fig_sim = plot_similarity_heatmap(similarity_df)
    fig_3d = plot_3d_room_positions(similarity_df)
    # fig_3d_interactive = plot_3d_room_positions_interactive(similarity_df)
    # fig_3d_interactive.show()
    sorted_similarity = sort_by_similarity(similarity_df[room_name])
    # fig_table = plot_similarity_table(sorted_similarity, room_name)

    # fig_table_knn = plot_similarity_table(
    #     sort_by_similarity(knn_similarity_df[room_name]), room_name
    # )
    # snapshot_rooms = [
    #     "shot_coffee_corner",
    #     "shot_geolab",
    #     "shot_hallm",
    #     "shot_stairway_hallu",
    #     "hallr",
    # ]
    # for room in snapshot_rooms:
    #     sorted_similarity = sort_by_similarity(similarity_df[room])
    #     fig_table = plot_similarity_table(sorted_similarity, room)
    #     save_figures([[room, fig_table]], outdir)
    save_figures(
        [
            ["similarity", fig_sim],
            ["3dmap", fig_3d],
            # ["table", fig_table],
            # ["table_knn", fig_table_knn],
        ],
        outdir,
    )

    return sorted_similarity


def plot_similarity_table(similarity_series, roomname):
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.axis("off")
    ax.table(
        cellText=similarity_series.round(2).values.reshape(-1, 1),
        colLabels=["Similarity"],
        rowLabels=similarity_series.index,
        loc="center",
        cellLoc="center",
        colWidths=[0.2],
        cellColours=plt.cm.RdYlGn(similarity_series.values.reshape(-1, 1)),
    )
    plt.title("Similarity Table (room: {})".format(roomname), loc="left")
    return fig


def plot_similarity_heatmap(
    similarity_df,
    title="Wifi fingerprint similarity",
):
    fig = plt.figure(figsize=(20, 16))
    sns.heatmap(
        similarity_df,
        cmap="rocket",
    )
    plt.title(title)
    plt.xlabel("Rooms")
    plt.ylabel("Rooms")
    # plt.savefig("{}/heatmap.png".format(outdir))
    return fig


def plot_3d_room_positions(similarity_df):
    distance_matrix = 1 - similarity_df

    mds = MDS(n_components=3, dissimilarity="precomputed", random_state=42)
    coords = mds.fit_transform(distance_matrix)

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(coords[:, 0], coords[:, 1], coords[:, 2])

    for (x, y, z), room in zip(coords, similarity_df.index):
        ax.text(x, y, z, room)

    plt.title("Room Position based on WiFi Fingerprint Similarity")
    # plt.savefig("{}/3dmap.png".format(outdir))
    return fig


def plot_3d_room_positions_interactive(similarity_df):
    distance_matrix = 1 - similarity_df

    mds = MDS(n_components=3, dissimilarity="precomputed", random_state=42)
    coords = mds.fit_transform(distance_matrix)

    # Create a Plotly figure
    fig = go.Figure()

    # Add 3D scatter plot
    fig.add_trace(
        go.Scatter3d(
            x=coords[:, 0],
            y=coords[:, 1],
            z=coords[:, 2],
            name="Estimated relative distance of rooms",
            mode="markers+text",  # Combine scatter and text in one trace
            text=similarity_df.index,  # Text labels
            marker=dict(size=5, opacity=0.8),
        ),
    )

    # Update layout for a better view
    fig.update_layout(
        title="Room Position based on WiFi Fingerprint Similarity",
        scene=dict(xaxis_title="X Axis", yaxis_title="Y Axis", zaxis_title="Z Axis"),
        margin=dict(l=0, r=0, b=0, t=0),  # Adjust margins
    )

    return fig


def save_figures(figs, outdir):
    for [fname, fig] in figs:
        fig.savefig("{}/{}.png".format(outdir, fname))


def main():
    similarity = find_similar_room("hallr", "./2nd_ass/data", outdir="./2nd_ass/result")
    print(similarity)


if __name__ == "__main__":
    main()
