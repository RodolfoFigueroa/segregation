import re

import geopandas as gpd

from pathlib import Path
from segregation.scripts.common import get_cve_from_args


def extract_q_k(path):
    res = re.search(r"q_(\d+)\.k_(\d+)\.gpkg", path.name)
    return int(res[1]), int(res[2])


def process_output(opath, cent_path, out_path):
    cve = opath.stem

    centrality_paths = list((cent_path / cve).glob("*"))
    first_cent_path = centrality_paths.pop()
    q, k = extract_q_k(first_cent_path)

    first_cent_frame = gpd.read_file(first_cent_path)
    first_cent_frame = first_cent_frame.rename(
        columns={"is_significant": f"significant_q_{q}_k_{k}"}
    )

    for centrality_path in centrality_paths:
        q, k = extract_q_k(centrality_path)

        frame = gpd.read_file(centrality_path)
        frame = frame.drop(columns=["geometry"])
        frame = frame.rename(columns={"is_significant": f"significant_q_{q}_k_{k}"})

        first_cent_frame = first_cent_frame.merge(frame, how="inner", on="cvegeo")

    income_frame = gpd.read_file(opath)
    income_frame = income_frame.drop(columns=["geometry"])
    out = first_cent_frame.merge(income_frame, how="inner", on="cvegeo")
    out.to_file(out_path / f"{cve}.gpkg")


def main():
    cve = get_cve_from_args()

    cent_path = Path("./centrality")
    income_path = Path("./income")

    output_path = Path("./merged")
    output_path.mkdir(exist_ok=True)

    if cve is None:
        for opath in income_path.glob("M*"):
            process_output(opath, cent_path, output_path)
    else:
        opath = income_path / f"{cve}.gpkg"
        process_output(opath, cent_path, output_path)
