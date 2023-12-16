from matplotlib.ticker import ScalarFormatter
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def plot(title, df):
    plt.figure(figsize=(10, 5))  # Set the figure size

    # Plot PDOP
    plt.plot(df.index, df["PDOP"], label="PDOP")

    # Plot HDOP
    plt.plot(df.index, df["HDOP"], label="HDOP")

    # Plot VDOP
    plt.plot(df.index, df["VDOP"], label="VDOP")

    # Optionally, set the x and y axes labels and plot title
    plt.xlabel("Time")

    plt.ylabel("DOP Value")
    plt.title(title + "PDOP, HDOP, and VDOP Over Time")
    # plt.yticks(np.arange(0, float(df.max().max()), step=1))
    # Show the legend
    plt.legend()

    plt.gca().invert_yaxis()

    # Display the plot
    # plt.show()
    plt.savefig("_".join(title.split()) + ".png")
    print("run!!!!!!")


def visualize_dop(title, fpath):
    # Read the CSV file
    data = None
    with open(fpath, "r") as f:
        data = f.readlines()

    """
    Example of data in the CSV file:
    $GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,35.2,35.0,3.7*37
    $GPGSV,3,1,12,01,45,045,50,02,45,045,50,03,45,045,50,04,45,045,50*7c
    $GPGSV,3,2,12,05,45,045,50,06,45,045,50,07,45,045,50,08,45,045,50*77
    $GPGSV,3,3,12,09,45,045,50,10,45,045,50,11,45,045,50,12,45,045,50*71
    $GPRMC,122416.89,A,5159.9704,N,422.6192,E,-1.9,144.6,251123,0.0,E,A*18
    $GPVTG,144.6,T,0.0,M,-1.9,N,-3.6,K*44
    """
    # Filter the GPGSA sentences
    gpgsa_rows = [row for row in data if row.startswith("$GPGSA")]

    gpgsa_csv = [row.split(",") for row in gpgsa_rows]
    df = pd.DataFrame(gpgsa_csv)
    pod_df = df.apply(
        lambda row: [row[15], row[16], row[17].split("*")[0]],
        axis=1,
        result_type="expand",
    )
    pod_df.columns = ["PDOP", "HDOP", "VDOP"]
    pod_df["PDOP"].astype(float)
    pod_df["HDOP"].astype(float)
    pod_df["VDOP"].astype(float)
    pod_list = pod_df["VDOP"].tolist()
    pod_num_list = [float(elem) for elem in pod_list]
    mean = np.mean(pod_num_list)
    median = np.median(pod_num_list)
    std = np.std(pod_num_list)
    print("mean", mean)
    print("median", median)
    print("std", std)
    plot(title, pod_df)
    # calc_statistics(title, pod_df)


def visualize_satellite_num(title, files, times):
    """
    Example of data in the CSV file:
    $GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,35.
    """
    satellites_in_view_list = []
    for f in files:
        # Read the CSV file
        data = None
        with open(f, "r") as f:
            data = f.readlines()
        gpgsv_rows = [row for row in data if row.startswith("$GPGSV")]
        gpgsv_line = gpgsv_rows[0]
        satellites_in_view = int(gpgsv_line.split(",")[3])
        satellites_in_view_list.append(satellites_in_view)

    plt.figure(figsize=(10, 5))  # Set the figure size

    fig, ax = plt.subplots()
    ax.bar(times, satellites_in_view_list)
    ax.set_xlabel("Time")
    ax.set_ylabel("Number of Satellites in View")
    plt.savefig("_".join(title.split()) + ".png")


def visualize_lat_log(title, files):
    """
    Example of data in the CSV file:
    $GPGGA,122416.89,5159.9704,N,422.6192,E,1,04,2.8,35.2,M,35.0,M,,*5B
    """
    lat_list = []
    lng_list = []
    for f in files:
        # Read the CSV file
        data = None
        with open(f, "r") as f:
            data = f.readlines()
        gpgga_rows = [row for row in data if row.startswith("$GPGGA")]
        for row in gpgga_rows:
            lat_dms, lat_dir = row.split(",")[2], row.split(",")[3]
            lng_dms, lng_dir = row.split(",")[4], row.split(",")[5]
            lat = dms_to_decimal(lat_dms[:2], lat_dms[2:], lat_dir)
            lng = dms_to_decimal(lng_dms[:3], lng_dms[3:], lng_dir)
            lat_list.append(lat)
            lng_list.append(lng)

    lat_list = [round(elem, 4) for elem in lat_list]
    lng_list = [round(elem, 4) for elem in lng_list]
    plt.figure(figsize=(10, 5))  # Set the figure size

    plt.scatter(lat_list, lng_list, marker="o", label="Lat Lng plot")
    plt.xlabel("Latitude (degrees)")
    plt.ylabel("Longitude (degrees)")
    ax = plt.gca()
    ax.xaxis.set_major_formatter(ScalarFormatter(useOffset=False))

    plt.legend()
    plt.savefig("_".join(title.split()) + ".png")


# def calc_statistics(title, df):
# print("df", df["PDOP"].mean())
# mean = df["PDOP"].mean()
# median = df["PDOP"].median()
# std = df["PDOP"].std()
# min = df["PDOP"].min()
# max = df["PDOP"].max()

# data = {
#     "Mean": mean,
#     "Median": median,
#     "Standard Deviation": std,
#     "Minimum": min,
#     "Maximum": max,
# }
# fig, ax = plt.subplots()
# ax.axis("off")
# ax.axis("tight")
# ax.table(cellText=data.values(), colLabels=data.keys(), loc="center")
# fig.tight_layout()
# plt.savefig("test" + ".png")
# plt.savefig("_".join(title.split()) + ".png")


def main():
    files = [
        # ["Open Sky 3pm", "./1st_ass/nmea_open_nov29_3pm.csv"],
        # ["Blocked line-of-sight 3pm", "./1st_ass/nmea_bk_nov29_3pm.csv"],
        ["indoor", "./1st_ass/archive/nmea_indoor_nov25_6pm.csv"],
        ["indoor2", "./1st_ass/archive/nmea_indoor_nov25_1pm.csv"],
    ]
    for title, fpath in files:
        visualize_dop(title, fpath)
    visualize_lat_log("Lat Lng plot", [elem[1] for elem in files])


def dms_to_decimal(degrees, minutes, direction):
    decimal = float(degrees) + float(minutes) / 60
    if direction in ["S", "W"]:
        decimal = -decimal
    return decimal


if __name__ == "__main__":
    main()
