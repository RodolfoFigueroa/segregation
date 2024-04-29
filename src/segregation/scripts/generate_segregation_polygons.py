import os

import geopandas as gpd
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import xarray as xr

from pathlib import Path
from segregation.plots import get_not_significant_mask


combs = [
    (1, 5),
    (1, 100),
    (5, 5),
    (5, 100)
]

output_path = Path("./output")

cent_path = Path("./centrality")
cent_path.mkdir(exist_ok=True)


for opath in output_path.glob("M*"):
    if opath.name.startswith("m"): # Windows is case-insensitive
        continue

    cve = opath.name
    print(cve)

    out_dir = cent_path / cve
    out_dir.mkdir(exist_ok=True)

    dummy_parquet = pd.read_parquet(opath / "bs_results.parquet" / "part.0.parquet")
    columns = dummy_parquet.columns
    del dummy_parquet            
            
            
    C_ds = xr.open_dataset(opath / 'centrality_index.nc')
    res_bs = pd.read_parquet(opath / 'bs_results.parquet/').reset_index(drop=True)
    pop_income_start = gpd.read_file(opath / 'income_quantiles.gpkg')

    pop_income = pop_income_start.copy()


    for q, k in combs:
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

        col_name = f'local_centralization_q_{q}_k_{k}'
        pop_income[col_name] = C_ds['centrality'].sel(income_quantile=q, k_neighbors=k)

        out_df = pop_income[[col_name, "geometry"]].copy()

        out_df["is_significant"] = ~get_not_significant_mask(bs_array)
        out_df.to_file(out_dir / f"q_{q}.k_{k}.gpkg")
    break