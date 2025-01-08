### scripts to retrive gene nucleotide sequence from KEGG pathway/module

> [!WARNING]
> The scripts comply with KEGG's requests the users to only send 3 requests per second
> SO DO NOT PARALLELISE THE SCRIPTS

# `fetch_all_genes.py`

Its a CLI tool can be used with arguments

```bash
./fetch_all_genes.py --help
usage: fetch_all_genes.py [-h] --org ORG [--pathway PATHWAY] [--module MODULE] [--output OUTPUT]

Retrieve KEGG gene sequences by pathway or module.

options:
  -h, --help         show this help message and exit
  --org ORG          Organism code (e.g., hsa or rsz)
  --pathway PATHWAY  Pathway ID (e.g., rsz00592)
  --module MODULE    Module ID (e.g., rsz_M00113)
  --output OUTPUT    Output file for concatenated sequences
```

## Usage examples:

```bash
./fetch_all_genes.py --org rsz --pathway rsz_00730 # generates rsz00966_genes.fa rsz00966_genes_id.tsv
./fetch_all_genes.py --org rsz --module rsz_M00005 # generates rsz_M00005_genes.fa rsz_modules.tsv rsz_rsz_M00005_genes.tsv

./fetch_all_genes.py --org rsz --pathway rsz_00730 --output Thiamine_metabolism.fa # generates rsz00730_genes_id.tsv Thiamine_metabolism.fa
./fetch_all_genes.py --org rsz --module rsz_M00005 --output PRPP.fa # generates PRPP.fa rsz_modules.tsv rsz_rsz_M00005_genes.tsv 
```


# `fetch_all_genes.sh`

open the file and change the `ORG` and `PATHWAY`
`ID_OUTPUT` `OUTPUT` (are optional, because they are set based on organism and pathway code)

## USAGE

PARAMETERS:
```bash
ORG="rsz"
PATHWAY="rsz00966"
```

OUTPUTS:
generates `rsz00966_genes.fa` `rsz00966_genes_id.tsv` files


# `fetch_genes_in_module.sh`

open the file and change the `ORG` and `MODULE`
`ID_OUTPUT` `MODULE_GENES` `OUTPUT` (are optional, because they are set based on organism and pathway code)

## USAGE

PARAMETERS:
```bash
ORG="rsz"
MODULE="rsz_M00005"
```

OUTPUTS:
generates `rsz_M00005_genes.fa` `rsz_modules.tsv` `rsz_rsz_M00005_genes.tsv` files
