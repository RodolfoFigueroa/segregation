import re

import geopandas as gpd

from pathlib import Path
from segregation.scripts.common import get_cve_from_args


def main():
    cve = get_cve_from_args()

    cent_path = Path("./centrality")
    income_path = Path("./income")

    if cve is None:
        for path in income_path.glob("M*"):
            cve = path.stem

            centrality_paths = list((cent_path / cve).glob("*"))
            first_cent_path = centrality_paths.pop()
            first_cent_frame = gpd.read_file(first_cent_path)

            for centrality_path in centrality_paths:
                frame = gpd.read_file(centrality_path)
                frame = frame.drop(columns=["is_significant"])
                first_cent_frame = first_cent_frame.sjoin(
                    frame, how="inner", predicate="contains"
                )
                first_cent_frame = first_cent_frame.drop(columns=["index_right"])

            income_frame = gpd.read_file(path)
            out = first_cent_frame.sjoin(
                income_frame, how="inner", predicate="contains"
            )
            out = out.drop(columns=["index_right"])
            # out = out[["cvegeo"]]
            print(out)

    else:
        pass
