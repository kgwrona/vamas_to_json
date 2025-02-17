from vamas import Vamas
import json
import argparse
import sys
import pathlib
import itertools

parser = argparse.ArgumentParser()
parser.add_argument("file", type=pathlib.Path, help="VAMAS (.vms) file to convert")
parser.add_argument("-o", "--out_file", type=pathlib.Path, help="output file path")
parser.add_argument(
    "--raw",
    action="store_true",
    help="Outputs raw list of blocks, rather than grouping by sample name",
)

# Print help if no arguments supplied
if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
    sys.exit(1)

args = parser.parse_args()

if args.file.suffix == ".vms":
    file = args.file
else:
    raise SystemExit("Error: Input is not a .vms file")

if args.out_file:
    if args.out_file.suffix:
        out_file = args.out_file
    else:
        out_file = args.out_file.with_suffix(".json")
else:
    out_file = file.with_suffix(".json")


def parse_vamas(file):
    vms = Vamas(file)
    header = vms.header.__dict__
    blocks = [b.__dict__ for b in vms.blocks]
    return header, blocks


def transform_raw_blocks(blocks):
    d = {}
    result = itertools.groupby(blocks, key=lambda x: x["sample_identifier"])
    for sample, s_group in result:
        scans = itertools.groupby(
            s_group, key=lambda x: x["species_label"]
        )  # block_id or species_label?
        sample_dict = {}
        for scan, sc_group in scans:
            sample_dict[scan] = list(sc_group)[0]
        d[sample] = sample_dict
    return d


def prepare_output():
    if args.raw is False:
        header, blocks = parse_vamas(file)
        blocks_new = transform_raw_blocks(blocks)
        out = {"header": header, "blocks": blocks_new}
    elif args.raw is True:
        out = Vamas(file)
    return out


out = prepare_output()
with open(out_file, "w") as f:
    json.dump(out, f, indent=2, default=lambda o: o.__dict__)
