#!/usr/bin/env python

import os
import requests
import time
import argparse

# Color codes for messages (useful for terminal output)
GREEN = '\033[0;32m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color

def success(message):
    print(f"{GREEN}{message}{NC}")

def failure(message):
    print(f"{RED}{message}{NC}")

# Step 1: Download gene list from KEGG
def download_gene_list(output_file, url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(output_file, 'w') as f:
            f.write(response.text)
        success(f"Gene list retrieved successfully: {output_file}")
    except requests.RequestException as e:
        failure(f"Failed to retrieve gene list: {e}")
        exit(1)

# Step 2: Download each gene's nucleotide sequence
def download_gene_sequences(input_file, org):
    try:
        with open(input_file, 'r') as f:
            gene_ids = [line.split('\t')[1].strip() for line in f]

        total_genes = len(gene_ids)
        for index, gene_id in enumerate(gene_ids, start=1):
            url = f"https://rest.kegg.jp/get/{gene_id}/ntseq"
            try:
                response = requests.get(url)
                response.raise_for_status()
                with open(f"{org}_{gene_id}.fa", 'w') as gene_file:
                    gene_file.write(response.text)
                success(f"[{index}/{total_genes}] Retrieved {gene_id} gene ntseq")
                time.sleep(0.4)  # To avoid overwhelming the server
            except requests.RequestException as e:
                failure(f"[{index}/{total_genes}] Failed to retrieve {gene_id}: {e}")
    except FileNotFoundError:
        failure(f"{input_file} not found. Cannot proceed with gene sequence retrieval.")
        exit(1)

# Step 3: Concatenate all .fa files into a single file and clean up
def concatenate_sequences(input_file, output_file, org):
    success("Concatenating retrieved gene sequences")
    with open(output_file, 'w') as out_file:
        for gene_id in open(input_file, 'r'):
            gene_id = gene_id.split('\t')[1].strip()
            gene_file = f"{org}_{gene_id}.fa"
            if os.path.exists(gene_file):
                with open(gene_file, 'r') as gf:
                    out_file.write(gf.read())
                os.remove(gene_file)
            else:
                failure(f"File {gene_file} not found, skipping...")
    success(f"All gene sequences saved to {output_file}")

# Main CLI tool
def main():
    parser = argparse.ArgumentParser(description="Retrieve KEGG gene sequences by pathway or module.")
    parser.add_argument("--org", required=True, help="Organism code (e.g., hsa or rsz)")
    parser.add_argument("--pathway", help="Pathway ID (e.g., rsz00592)")
    parser.add_argument("--module", help="Module ID (e.g., rsz_M00113)")
    parser.add_argument("--output", help="Output file for concatenated sequences")
    args = parser.parse_args()


    if args.pathway:
        gene_list_url = f"https://rest.kegg.jp/link/{args.org}/{args.pathway}"
        gene_list_file = f"{args.pathway}_genes_id.tsv"

        download_gene_list(gene_list_file, gene_list_url)

    elif args.module:
        gene_list_url = f"https://rest.kegg.jp/link/{args.org}/module"
        gene_list_file_raw = f"{args.org}_modules.tsv"
        gene_list_file = f"{args.org}_{args.module}_genes.tsv"

        download_gene_list(gene_list_file_raw, gene_list_url)

        # Filter genes belonging to the specified module
        with open(gene_list_file_raw, 'r') as infile, open(gene_list_file, 'w') as filtered_file:
            gene_ids = infile.readlines()
            for gene_id in gene_ids:
                if args.module in gene_id:
                    filtered_file.write(gene_id.strip()+ '\n')

    else:
        parser.error("Either --pathway or --module must be specified.")

    output = args.output or f"{args.pathway or args.module}_genes.fa"

    download_gene_sequences(gene_list_file, args.org)
    concatenate_sequences(gene_list_file, output, args.org)

if __name__ == "__main__":
    main()
