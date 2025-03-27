#!/usr/bin/env python3

"""
This script extracts and prints values from a specified column in a CSV/TSV file.
Usage:
    python script.py -i <input_file> -c <column_name> [-d <delimiter>] [--unique] [--count] [--sort]
Arguments:
    -i, --input      Path to the input file (required)
    -c, --column     Column name to extract values from (required)
    -d, --delimiter  Delimiter used in the file (default: tab)
    -u, --unique     Print only unique values
    -n, --count      Show counts for each unique value
    -s, --sort       Sort the output (by count when --count is used, alphabetically otherwise)
Example:
    python script.py -i data.tsv -c gene_id -d "," --unique --count --sort
"""

import polars as pl
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
    parser.add_argument(
        "-u",
        "--unique",
        action="store_true",
        help="Print only unique values"
    )
    parser.add_argument(
        "-n",
        "--count",
        action="store_true",
        help="Show counts for each unique value"
    )
    parser.add_argument(
        "-s",
        "--sort",
        action="store_true",
        help="Sort the output"
    )
    args = parser.parse_args()

    # Create a lazy frame with better null handling
    lf = pl.scan_csv(
        args.input,
        separator=args.delimiter,
        comment_prefix="#",
        null_values=["", "NA", "N/A", "null", "NULL", "None", "NaN", "Not provided"]
    )

    # Check if column exists by collecting schema (recommended approach)
    schema = lf.collect_schema()
    if args.column not in schema:
        raise ValueError(f"Column '{args.column}' not found in the input file.")

    # Base query to select the column
    query = lf.select(pl.col(args.column))

    if args.unique or args.count:
        if args.count:
        # Count frequency of each value with null handling
            query = (
                lf.select(
                    pl.when(pl.col(args.column).is_null())
                    .then(pl.lit("NULL"))
                    .otherwise(pl.col(args.column))
                    .alias("value")
                )
                .group_by("value")
                .agg(pl.len().alias("count"))
            )

            if args.sort:
                # Sort by count (descending)
                query = query.sort("count", descending=True)
            elif args.sort:
                # Sort alphabetically if only unique is requested
                query = query.sort("value")
        else:
            # Just get unique values
            query = query.unique()
            if args.sort:
                # Sort alphabetically
                query = query.sort(args.column)

    # Execute the query
    result = query.collect()

    # Print the results
    if args.count:
        total_rows = 0
        for row in result.iter_rows():
            value = row[0]
            count = row[1]
            total_rows += count
            print(f"{value}\t{count}")

        if args.count:
            print(f"\nTotal rows: {total_rows}")
    else:
        for value in result[args.column]:
            # Handle null/None values
            print(value if value is not None else "NULL")

if __name__ == "__main__":
    main()
