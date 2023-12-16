import os
import pandas as pd


def read_access_point(dir_path):
    # walk dir and read 'accesspoint.log', store TSV data to pandas dataframe
    data_dict = {}
    root, dirs, files = os.walk(dir_path)

    # iterater all dirs and read files under each dir

    # for root, dirs, files in os.walk(dir_path):
    #     # iterate loor for each dir to read data

    #     print("root:", root)
    #     print("dirs: ", dirs)
    #     print("files", files)
    #     data = []
    #     for file in files:
    #         if file == "accesspoint.log":
    #             with open(os.path.join(root, file), "r") as f:
    #                 for line in f:
    #                     data.append(line.strip().split("\t"))
    #     df = pd.DataFrame(
    #         data,
    #         columns=[
    #             "timestamp",
    #             "access_point",
    #             "status",
    #             "mac_address",
    #             "signal_strength",
    #         ],
    #     )
    #     data_dict[root] = df
    # return data_dict


def calc_statistics(data_dict):
    avg_signal_strength = {}
    for root, df in data_dict.items():
        avg_signal_strength[root] = df["status"].mean()
    return avg_signal_strength


def main():
    data_dict = read_access_point("./2nd_ass/data/")
    print(data_dict)


def test():
    print()


if __name__ == "__main__":
    main()
