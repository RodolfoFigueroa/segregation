import yaml

import geopandas as gpd
import numpy as np
import pandas as pd

from pathlib import Path
from segregation.plots import get_missing_agebs
from segregation.scripts.common import process_cve


def process_output(opath, data_path, income_path, met_zones):
    cve = opath.name
    met_zone_codes = met_zones[cve]

    df_income = gpd.read_file(opath / "income_quantiles.gpkg")
    df_income["income_pc"] = df_income["income_pc"] * 4 / 19.24 / 1000

    df_missing = get_missing_agebs(met_zone_codes, data_path, df_income)
    df_missing.columns = ["cvegeo", "geometry"]
    df_missing["income_pc"] = np.nan

    df_income_combined = df_income.copy()[["cvegeo", "income_pc", "geometry"]]
    df_income_combined = pd.concat([df_income_combined, df_missing])
    df_income_combined = df_income_combined.reset_index(drop=True)
    df_income_combined.to_file(income_path / f"{cve}.gpkg")


def main():
    data_path = Path("./data")
    output_path = Path("./output")

    income_path = Path("./income")
    income_path.mkdir(exist_ok=True)

    with open("./output/met_zones.yaml", "r") as f:
        met_zones = yaml.safe_load(f)

    process_cve(process_output, output_path, data_path, income_path, met_zones)
