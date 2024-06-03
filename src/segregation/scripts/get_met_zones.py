import argparse
import os
import yaml

import geopandas as gpd
import pandas as pd


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("year", help="Census year.", type=int)

    args = parser.parse_args()

    if args.year == 2018:
        df = pd.read_csv("./data/BASE_SUN_2018.csv", encoding="latin1")

        df_filtered = df[df["CVE_SUN"].str.startswith("M")].copy()
        out = df_filtered.groupby("CVE_SUN")["CVE_MUN"].apply(lambda x: list(x))

    elif args.year == 2024:
        df = gpd.read_file("./data/mpios/mpios_en_metropoli.shp")

        df_filtered = df[
            (df["TIPOMET"] == "Zona metropolitana")
            | (df["TIPOMET"] == "Metrópoli municipal")
        ].copy()
        df_filtered["CVEGEO"] = df_filtered["CVEGEO"].astype(int)
        df_filtered["CVE_ZONA"] = (
            df_filtered["CVE_ZONA"].str.split(".").apply(lambda x: f"M{x[0]}.{x[2]}")
        )

        out = df_filtered.groupby("CVE_ZONA")["CVEGEO"].apply(lambda x: list(x))

    out = out.to_dict()

    if not os.path.isdir("./output"):
        os.makedirs("./output")

    with open("./output/met_zones.yaml", "w") as f:
        yaml.dump(out, f)
