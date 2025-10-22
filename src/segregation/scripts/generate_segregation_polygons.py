import os
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import xarray as xr

from segregation.plots import get_significant_mask
from segregation.scripts.common import process_cve


def process_output(opath, cent_path):
    cve = opath.name

    out_dir = cent_path / cve
    out_dir.mkdir(exist_ok=True)

    dummy_parquet = pd.read_parquet(opath / "bs_results.parquet" / "part.0.parquet")
    columns = dummy_parquet.columns
    del dummy_parquet

    C_ds = xr.open_dataset(opath / "centrality_index.nc")
    pop_income_start = gpd.read_file(opath / "income_quantiles.gpkg")

    pop_income = pop_income_start.copy()

    for q, k in [(1, 5), (1, 100), (5, 5), (5, 100)]:
        k = min(k, C_ds.k_neighbors.max().item())

        prefix = f"cent_idx.q_{q}.k_{k}."
        wanted_cols = [col for col in columns if col.startswith(prefix)]

        parquet_files = os.listdir(opath / "bs_results.parquet")
        n_samples = len(parquet_files)
        bs_array = np.empty((n_samples, len(wanted_cols)), dtype=float)
        for i, name in enumerate(parquet_files):
            fpath = opath / "bs_results.parquet" / name
            parquet = pq.read_table(fpath, columns=wanted_cols)
            parquet = np.asarray(parquet)
            parquet = parquet.squeeze()
            bs_array[i, :] = parquet

        col_name = f"local_centralization_q_{q}_k_{k}"
        pop_income[col_name] = C_ds["centrality"].sel(income_quantile=q, k_neighbors=k)

        out_df = pop_income[[col_name, "cvegeo", "geometry"]].copy()

        out_df["is_significant"] = get_significant_mask(bs_array)
        out_df.to_file(out_dir / f"q_{q}.k_{k}.gpkg")


def main():
    output_path = Path("./output")

    cent_path = Path("./centrality")
    cent_path.mkdir(exist_ok=True)

    process_cve(process_output, output_path, cent_path)
