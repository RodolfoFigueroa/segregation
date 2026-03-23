import argparse
import logging
import os
import time
from pathlib import Path

import yaml

from segregation.bootstrap import get_bs_samples
from segregation.plots import make_all

logger = logging.getLogger()


def check_positive(value):
    try:
        value = int(value)
        if value < 0:
            err = f"{value} is not a positive integer."
            raise argparse.ArgumentTypeError(err)
    except ValueError:
        err = f"{value} is not a positive integer."
        raise argparse.ArgumentTypeError(err)
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Estimate segregation indices using IPF with bootstraping confidence intervals.",
    )
    parser.add_argument(
        "CVE_MET",
        help="Metropolitan zone identifier.",
    )
    parser.add_argument(
        "-n",
        "--n_samples",
        type=check_positive,
        default=0,
        help="Number of bootstrap samples to use, defaults to 0 for no bootstraping.",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Make plots for the respective state. Assumes output files have been created.",
    )
    parser.add_argument(
        "--time",
        action="store_true",
        help="Print total execution time.",
    )
    parser.add_argument(
        "--seed",
        default=123456,
        type=int,
        help="Seed for random number generation.",
    )

    args = parser.parse_args()

    if args.n_samples > 10_000:
        err = f"Number of samples {args.n_samples} is too large. Maximum allowed is 10,000."
        raise ValueError(err)

    msg = (
        f"Initiating estimation for metropolitan zone {args.CVE_MET}"
        f" with {args.n_samples} samples."
    )
    logger.info(msg)

    # Load met_zones

    if not os.path.exists("./output/met_zones.yaml"):
        err = "met_zones.yaml not found. Run get_met_zones.py first."
        raise ValueError(err)

    with open("./output/met_zones.yaml") as f:
        met_zones = yaml.safe_load(f)
    met_zone_codes = met_zones[args.CVE_SUN]

    opath = Path(f"./output/{args.CVE_SUN}/")
    if not opath.exists():
        opath.mkdir(parents=True, exist_ok=True)
    ipath = Path("./data/")

    if args.plot:
        make_all(met_zone_codes, opath, ipath)
    else:
        start_time = time.time()
        get_bs_samples(
            args.n_samples,
            met_zone_codes,
            opath=opath,
            data_path=ipath,
            q=5,
            k_list=[5, 100],
            seed=args.seed,
        )
        stop_time = time.time()

        if args.time:
            print(f"Total time: {stop_time - start_time}")
