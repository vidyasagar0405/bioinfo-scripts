import pandas as pd
import requests
import sys
from rich import print


# Function to fetch data from Ensembl API
def get_snp_info(rsid):
    url = f"https://rest.ensembl.org/variation/human/{rsid}?content-type=application/json"
    response = requests.get(url)

    if response.ok:
        data = response.json()
        mappings = data.get("mappings", [])
        if mappings:
            pos = mappings[0]["location"].split("-")  # Split start-end positions

            start_pos = pos[0].split(":")[1]  # Extract number part after "chr:"
            end_pos = pos[1] if len(pos) > 1 else start_pos  # Handle cases where there's no range

            if start_pos.strip() == end_pos.strip():
                pos = [pos[0]]  # Keep only the first part (chr:start)

            pos = "-".join(pos)  # Convert list back to a string

            alleles = mappings[0].get("allele_string", "N/A")  # Get allele info
            ancestral_allele = mappings[0].get("ancestral_allele", None)  # Get ancestral allele

            # If ancestral allele is None, use the first allele
            if not ancestral_allele:
                ancestral_allele = alleles.split("/")[0]  # Take first allele as ancestral

            # Replace "/" with ",", and ensure correct formatting
            alleles_list = alleles.split("/")
            alleles_list.remove(ancestral_allele)  # Remove ancestral allele from the list
            formatted_alleles = ancestral_allele + ">" + ",".join(alleles_list) if alleles_list else ancestral_allele + ">"

            print(f"[green]Fetched data for rsID {rsid}...[/green]")

            return [rsid, pos, formatted_alleles]

    else:
        print(f"[red]Failed to fetch data for rsID {rsid}...status code: {response.status_code}[/red]")

    return [rsid, "N/A", "N/A"]


# Load rsIDs from a file (one rsID per line)
input_file = sys.argv[1]
output_file = sys.argv[2]

# Read rsIDs from file
with open(input_file, "r") as f:
    rsids = [line.strip() for line in f.readlines()]

# Fetch data for each rsID
results = [get_snp_info(rsid) for rsid in rsids]

# Save results to CSV
df = pd.DataFrame(results, columns=["rsID", "Position", "Alleles"])
df.to_csv(output_file, index=False, sep="\t")

print(f"[green]Results saved to {output_file}[/green]")
