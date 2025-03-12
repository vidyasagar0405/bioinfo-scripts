#!/usr/bin/env python3
"""
UCSC Gene Location Retriever

This script takes a gene name as input and retrieves its genomic location (chromosome, start, end)
from the UCSC Genome Browser database.

Usage:
    python ucsc_gene_location.py <gene_name> [--assembly hg38]

Example:
    python ucsc_gene_location.py TP53
    python ucsc_gene_location.py BRCA1 --assembly hg19
"""

import argparse
import sys
import pymysql
import pandas as pd

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
        gene_table = "ncbiRefSeq"
    else:
        raise ValueError(f"Unsupported assembly: {assembly}. Choose either 'hg19' or 'hg38'.")

    # Connect to UCSC MySQL server
    print(f"Connecting to UCSC Genome Browser database ({assembly})...")
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
            print(f"No gene found with symbol '{gene_name}' in {assembly} assembly.")
            return None

        # Create DataFrame with results
        columns = ["gene_symbol", "transcript_id", "chromosome", "start_position",
                  "end_position", "strand", "exon_count", "cds_start", "cds_end"]
        df = pd.DataFrame(results, columns=columns)

        # Add gene length column
        df["gene_length"] = df["end_position"] - df["start_position"] + 1

        return df

    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        # Close the connection
        conn.close()
        print("Database connection closed.")

def format_location(df):
    """Format location data in a human-readable format"""
    if df is None or df.empty:
        return "No location data found."

    # Get the canonical/longest transcript
    transcript = df.iloc[0]

    # Format the location
    strand = "+" if transcript["strand"] == "+" else "-"
    location = (f"Gene: {transcript['gene_symbol']}\n"
                f"Location: {transcript['chromosome']}:{transcript['start_position']}-{transcript['end_position']} ({strand})\n"
                f"Length: {transcript['gene_length']:,} bp\n"
                f"Transcript ID: {transcript['transcript_id']}\n"
                f"Exon count: {transcript['exon_count']}\n"
                f"Coding region: {transcript['cds_start']}-{transcript['cds_end']}")

    return location

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Retrieve gene location information from UCSC Genome Browser.")
    parser.add_argument("gene_name", help="Gene symbol to look up (e.g., TP53, BRCA1)")
    parser.add_argument("--assembly", choices=["hg19", "hg38"], default="hg38",
                        help="Genome assembly to use (default: hg38)")

    # Parse arguments
    args = parser.parse_args()

    # Get gene location
    gene_info = get_gene_location(args.gene_name, args.assembly)

    if gene_info is not None and not gene_info.empty:
        # Print summary for the canonical/longest transcript
        print("\n" + "="*50)
        print(format_location(gene_info))
        print("="*50)

        # Print all transcripts
        if len(gene_info) > 1:
            print(f"\nFound {len(gene_info)} transcripts for {args.gene_name}:")
            print(gene_info.to_string(index=False))
    else:
        print(f"No gene location found for '{args.gene_name}' in {args.assembly} assembly.")
        print("Please check the gene symbol and try again.")

if __name__ == "__main__":
    main()
