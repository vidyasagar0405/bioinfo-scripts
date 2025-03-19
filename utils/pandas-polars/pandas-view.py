#!/usr/bin/env python3
"""
This script extracts and prints values from a specified column in a CSV/TSV file.

Usage:
    python script.py -i <input_file> -c <column_name> [-d <delimiter>]

Arguments:
    -i, --input      Path to the input file (required)
    -c, --column     Column name to extract values from (required)
    -d, --delimiter  Delimiter used in the file (default: tab)

Example:
    python script.py -i data.tsv -c gene_id -d ","
"""

import pandas as pd
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Extract and print values from a specified column in a CSV/TSV file."
    )
    parser.add_argument("-i", "--input", required=True, help="Path to the input file")
    parser.add_argument(
        "-c", "--column", required=True, help="Column name to extract values from"
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        default="\t",
        help="Delimiter used in the file (default: tab)",
    )

    args = parser.parse_args()

    df = pd.read_csv(args.input, sep=args.delimiter, comment="#")

    if args.column not in df.columns:
        raise ValueError(f"Column '{args.column}' not found in the input file.")

    for value in df[args.column]:
        print(value)


if __name__ == "__main__":
    main()
