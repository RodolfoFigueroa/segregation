from argparse import ArgumentParser


def get_cve_from_args():
    parser = ArgumentParser()
    parser.add_argument(
        "CVE_SUN",
        default=None,
        help="Metropolitan zone identifier from the national urban system (SUN). See met_zones.yaml for a list. If not given, all available files will be processed.",
        nargs="?",
    )
    args = parser.parse_args()
    return args.CVE_SUN


def process_cve(process_output, output_path, *args):
    cve_sun = get_cve_from_args()

    if cve_sun is None:
        for opath in output_path.glob("M*"):
            if opath.name.startswith("m"):  # Windows is case-insensitive
                continue
            print(opath.name)
            process_output(opath, *args)
    else:
        opath = output_path / cve_sun
        assert opath.exists()
        process_output(opath, *args)
