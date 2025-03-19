#!/usr/bin/env python3
"""
This script checks for duplicate rows in a CSV/TSV file.
Usage:
    python check_duplicates.py -i <input_file> [-d <delimiter>] [--subset COLUMNS] [--show]
Arguments:
    -i, --input      Path to the input file (required)
    -d, --delimiter  Delimiter used in the file (default: tab)
    --subset         Comma-separated list of column names to check for duplicates (default: all columns)
    --show           Show the duplicate rows (limited to first 20 by default)
    --limit          Maximum number of duplicate rows to show (default: 20)
Example:
    python check_duplicates.py -i data.csv -d "," --subset id,name,date --show --limit 10
"""
import polars as pl
import argparse
import time


def main():
    parser = argparse.ArgumentParser(
        description="Check for duplicate rows in a CSV/TSV file."
    )
    parser.add_argument("-i", "--input", required=True, help="Path to the input file")
    parser.add_argument(
        "-d",
        "--delimiter",
        default="\t",
        help="Delimiter used in the file (default: tab)",
    )
    parser.add_argument(
        "--subset",
        help="Comma-separated list of column names to check for duplicates (default: all columns)",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show the duplicate rows",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of duplicate rows to show (default: 20)",
    )
    args = parser.parse_args()

    print(f"Checking for duplicates in {args.input}...")
    start_time = time.time()

    # Create a lazy frame
    lf = pl.scan_csv(
        args.input,
        separator=args.delimiter,
        null_values=["", "NA", "N/A", "null", "NULL", "None", "NaN", "Not provided"]
    )

    # Get schema for column verification
    schema = lf.collect_schema()

    # Determine which columns to check for duplicates
    if args.subset:
        subset_cols = [col.strip() for col in args.subset.split(',')]
        # Verify all columns exist
        for col in subset_cols:
            if col not in schema:
                raise ValueError(f"Column '{col}' not found in the input file.")
    else:
        subset_cols = list(schema.keys())

    print(f"Checking for duplicates based on {len(subset_cols)} columns: {', '.join(subset_cols)}")

    # First, count total rows
    total_rows = lf.select(pl.count()).collect().item()

    # Get count of unique combinations
    unique_rows = lf.select(subset_cols).unique().select(pl.count()).collect().item()

    # Calculate duplicates
    duplicate_count = total_rows - unique_rows

    # Calculate execution time
    elapsed_time = time.time() - start_time

    # Print results
    print(f"\nTotal rows: {total_rows}")
    print(f"Unique rows (based on selected columns): {unique_rows}")
    print(f"Duplicate rows: {duplicate_count} ({(duplicate_count/total_rows*100):.2f}% of total)")
    print(f"Analysis completed in {elapsed_time:.2f} seconds")

    # Show duplicate rows if requested
    if args.show and duplicate_count > 0:
        print(f"\nShowing up to {args.limit} duplicate rows:")

        # Find rows that appear more than once
        dup_rows = (
            lf.select(subset_cols)
            .group_by(subset_cols)
            .agg(pl.count().alias("freq"))
            .filter(pl.col("freq") > 1)
            .sort("freq", descending=True)
            .limit(args.limit)
        )

        # Execute the query and print results
        duplicates = dup_rows.collect()

        # Print in a formatted way
        for row in duplicates.iter_rows(named=True):
            freq = row.pop("freq")
            row_str = ", ".join(f"{k}: {v}" for k, v in row.items())
            print(f"Appears {freq} times: {row_str}")

        if duplicate_count > args.limit:
            print(f"... and {duplicate_count - args.limit} more duplicate patterns")


if __name__ == "__main__":
    main()
