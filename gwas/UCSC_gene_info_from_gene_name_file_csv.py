#!/usr/bin/env python3
"""
UCSC Gene Location Retriever (Batch Version)

This script takes a CSV file containing gene names and retrieves genomic location information
(chromosome, start, end, etc.) from the UCSC Genome Browser database, then outputs the results
to a new CSV file.

Usage:
    python ucsc_gene_batch.py <input_csv> <output_csv> [--assembly hg38] [--gene_col gene_name]

Example:
    python ucsc_gene_batch.py gene_list.csv gene_locations.csv
    python ucsc_gene_batch.py gene_list.csv gene_locations.csv --assembly hg19 --gene_col symbol
"""

import argparse
import sys
import pymysql
import pandas as pd
import time
from tqdm import tqdm  # For progress bar (optional, install with pip install tqdm)

def get_gene_location(gene_name, assembly="hg38"):
    """
    Retrieve gene location information from UCSC Genome Browser database.

    Parameters:
    -----------
    gene_name : str
        The gene symbol to look up (e.g., "TP53", "BRCA1")
    assembly : str
        Genome assembly to use, either "hg38" (default) or "hg19"

    Returns:
    --------
    pandas.DataFrame
        DataFrame containing gene location information
    """
    # Define UCSC database settings based on assembly
    if assembly == "hg19":
        db = "hg19"
        gene_table = "refGene"
    elif assembly == "hg38":
        db = "hg38"
        # gene_table = "ncbiRefSeq"
        # gene_table = "refGene"
        # gene_table = "knownGene"  # Using knownGene instead of refGene
        gene_table = "wgEncodeGencodeBasicV41"  # Using GENCODE v41 instead of ncbiRefSeq
    else:
        raise ValueError(f"Unsupported assembly: {assembly}. Choose either 'hg19' or 'hg38'.")

    # Connect to UCSC MySQL server
    conn = pymysql.connect(
        host="genome-mysql.soe.ucsc.edu",
        user="genomep",
        password="password",  # This is the actual public password for read-only access
        database=db
    )

    try:
        # Create a cursor
        cursor = conn.cursor()

        # Query for gene location
        query = f"""
        SELECT
            g.name2 as gene_symbol,
            g.name as transcript_id,
            g.chrom as chromosome,
            g.txStart + 1 as start_position,  # UCSC is 0-based, convert to 1-based
            g.txEnd as end_position,
            g.strand,
            g.exonCount,
            g.cdsStart + 1 as cds_start,
            g.cdsEnd as cds_end
        FROM
            {gene_table} g
        WHERE
            g.name2 = %s
        ORDER BY
            g.txEnd - g.txStart DESC
        """

        # Execute the query with gene name parameter
        cursor.execute(query, (gene_name,))

        # Fetch results
        results = cursor.fetchall()

        if not results:
            return None

        # Create DataFrame with results
        columns = ["gene_symbol", "transcript_id", "chromosome", "start_position",
                  "end_position", "strand", "exon_count", "cds_start", "cds_end"]
        df = pd.DataFrame(results, columns=columns)

        # Add gene length column
        df["gene_length"] = df["end_position"] - df["start_position"] + 1

        return df

    except Exception as e:
        print(f"Error retrieving {gene_name}: {e}")
        return None

    finally:
        # Close the connection
        conn.close()

def batch_process_genes(input_file, output_file, assembly="hg38", gene_column="gene_name"):
    """
    Process a batch of genes from a CSV file and output results to a new CSV file.

    Parameters:
    -----------
    input_file : str
        Path to input CSV file containing gene names
    output_file : str
        Path to output CSV file to write results
    assembly : str
        Genome assembly to use
    gene_column : str
        Name of the column in input CSV that contains gene names
    """
    try:
        # Read input CSV file
        print(f"Reading gene list from {input_file}...")
        gene_df = pd.read_csv(input_file)

        if gene_column not in gene_df.columns:
            raise ValueError(f"Column '{gene_column}' not found in input file. Available columns: {', '.join(gene_df.columns)}")

        # Extract gene list
        gene_list = gene_df[gene_column].unique().tolist()
        print(f"Found {len(gene_list)} unique genes to process.")

        # Initialize results dataframe
        all_results = []

        # Process each gene with a progress bar
        print(f"Retrieving gene locations from UCSC Genome Browser ({assembly})...")
        for gene in tqdm(gene_list, desc="Processing genes"):
            # Get gene info
            gene_info = get_gene_location(gene, assembly)

            if gene_info is not None and not gene_info.empty:
                # Add the canonical/longest transcript to results
                canonical = gene_info.iloc[0].to_dict()
                all_results.append(canonical)
            else:
                # Add a row with gene name but empty data for genes not found
                all_results.append({
                    "gene_symbol": gene,
                    "transcript_id": None,
                    "chromosome": None,
                    "start_position": None,
                    "end_position": None,
                    "strand": None,
                    "exon_count": None,
                    "cds_start": None,
                    "cds_end": None,
                    "gene_length": None
                })

            # Add a small delay to avoid overwhelming the UCSC server
            time.sleep(0.1)

        # Convert results to DataFrame
        results_df = pd.DataFrame(all_results)

        # Save to CSV
        results_df.to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")
        print(f"Retrieved location data for {len(results_df[results_df['chromosome'].notna()])} out of {len(gene_list)} genes.")

    except Exception as e:
        print(f"Error during batch processing: {e}")
        sys.exit(1)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Batch retrieve gene location information from UCSC Genome Browser.")
    parser.add_argument("input_csv", help="CSV file containing list of gene names")
    parser.add_argument("output_csv", help="Output CSV file to write results")
    parser.add_argument("--assembly", choices=["hg19", "hg38"], default="hg38",
                        help="Genome assembly to use (default: hg38)")
    parser.add_argument("--gene_col", default="gene_name",
                        help="Column name in input CSV containing gene names (default: gene_name)")

    # Parse arguments
    args = parser.parse_args()

    # Process batch of genes
    batch_process_genes(args.input_csv, args.output_csv, args.assembly, args.gene_col)

if __name__ == "__main__":
    main()
