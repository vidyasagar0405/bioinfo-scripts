ORG="rsz"
PATHWAY="rsz00966"
ID_OUTPUT="${PATHWAY}_genes_id.tsv"
OUTPUT="${PATHWAY}_genes.fa"

# Color codes for messages
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SUCCESS(){
    echo ""
    echo -e "${GREEN}------------------------------------"
    echo -e "$1"
    echo -e "------------------------------------${NC}"
    echo ""
}

FAILURE(){
    echo ""
    echo -e "${RED}------------------------------------"
    echo -e "$1"
    echo -e "------------------------------------${NC}"
    echo ""
}


# Step 1: Download the pathway genes list
wget --output-document $ID_OUTPUT https://rest.kegg.jp/link/${ORG}/${PATHWAY}

if [ $? -eq 0 ]; then
    for id in $(cut -f2 $ID_OUTPUT ); do
        wget --output-document "${id}.fa" https://rest.kegg.jp/get/"${id}"/ntseq
        if [ $? -eq 0 ]; then
            SUCCESS "Retrieved $id gene ntseq"
            sleep 0.4
        else
            FAILURE "There was a problem in retrieving $id data"
        fi
    done
else 
    FAILURE "There was a problem in retrieving the pathway genes list"
    exit 1
fi

# Step 2: Concatenate all .fa files into a single file and clean up
SUCCESS "Concatenating retrieved gene sequences"
for id in $(cut -f2 $ID_OUTPUT); do
    if [ -f "${id}.fa" ]; then
        cat "${id}.fa" >> "${OUTPUT}"
        rm "${id}.fa"
    else
        echo "File ${id}.fa not found, skipping..."
    fi
done
echo "All gene sequences saved to ${OUTPUT}"
