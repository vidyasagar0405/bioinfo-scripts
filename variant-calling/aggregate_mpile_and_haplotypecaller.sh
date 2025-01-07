#!/usr/bin/bash

# Remove any existing test directory and recreate the folder structure
rm -rf ./my-pipeline-test/
mkdir -p ./my-pipeline-test/sam-bcf-tools
mkdir -p ./my-pipeline-test/gatk

###################################################
# ONLY Modify these lines (REF and SAMPLES)
###################################################
# Define reference genome and sample BAM file paths
REF="./hello-nextflow/data/ref/ref.fasta"
SAMPLE1="./hello-nextflow/data/bam/reads_son.bam"
SAMPLE2="./hello-nextflow/data/bam/reads_father.bam"
SAMPLE3="./hello-nextflow/data/bam/reads_mother.bam"
###################################################


# Extract just the file name from the full file path
filename1=$(basename "$SAMPLE1")
filename2=$(basename "$SAMPLE2")
filename3=$(basename "$SAMPLE3")

# Define output VCF file paths for SAMtools and BCFtools
MPILEUP_OUT1="./my-pipeline-test/sam-bcf-tools/$filename1.vcf"
MPILEUP_OUT2="./my-pipeline-test/sam-bcf-tools/$filename2.vcf"
MPILEUP_OUT3="./my-pipeline-test/sam-bcf-tools/$filename3.vcf"

# Define output VCF file paths for GATK
GATK_OUT1="./my-pipeline-test/gatk/$filename1.vcf"
GATK_OUT2="./my-pipeline-test/gatk/$filename2.vcf"
GATK_OUT3="./my-pipeline-test/gatk/$filename3.vcf"

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

SUCCESS "                  MPILEUP                  "

# Activate the bcftools Conda environment
source $(conda info --base)/etc/profile.d/conda.sh && conda activate bcftools
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to activate bcftools environment.${NC}" >&2
    exit 1
fi

# Process SAMPLE1 with SAMtools and BCFtools
samtools index $SAMPLE1 && 
bcftools mpileup -f $REF $SAMPLE1 | bcftools call -mv -o $MPILEUP_OUT1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}SAMPLE1 SUCCESS!!!${NC}"
else
    echo -e "${RED}SAMPLE1 FAILED!!!${NC}" >&2
fi

# Process SAMPLE2 with SAMtools and BCFtools
samtools index $SAMPLE2 && 
bcftools mpileup -f $REF $SAMPLE2 | bcftools call -mv -o $MPILEUP_OUT2
if [ $? -eq 0 ]; then
    echo -e "${GREEN}SAMPLE2 SUCCESS!!!${NC}"
else
    echo -e "${RED}SAMPLE2 FAILED!!!${NC}" >&2
fi

# Process SAMPLE3 with SAMtools and BCFtools
samtools index $SAMPLE3 && 
bcftools mpileup -f $REF $SAMPLE3 | bcftools call -mv -o $MPILEUP_OUT3
if [ $? -eq 0 ]; then
    echo -e "${GREEN}SAMPLE3 SUCCESS!!!${NC}"
else
    echo -e "${RED}SAMPLE3 FAILED!!!${NC}" >&2
fi

echo "                    GATK                    "

# Activate the GATK Conda environment
source $(conda info --base)/etc/profile.d/conda.sh && conda activate gatk
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to activate gatk environment.${NC}" >&2
    exit 1
fi

# Process SAMPLE1 with GATK HaplotypeCaller
gatk HaplotypeCaller \
    -R $REF \
    -I $SAMPLE1 \
    -O $GATK_OUT1
if [ $? -eq 0 ]; then
   SUCCESS "SAMPLE1 SUCCESS!!!"
else
    FAILURE "SAMPLE1 FAILED!!!"
fi

# Process SAMPLE2 with GATK HaplotypeCaller
gatk HaplotypeCaller \
    -R $REF \
    -I $SAMPLE2 \
    -O $GATK_OUT2
if [ $? -eq 0 ]; then
    SUCCESS "SAMPLE2 SUCCESS!!!"
else
    FAILURE "SAMPLE2 FAILED!!!"
fi

# Process SAMPLE3 with GATK HaplotypeCaller
gatk HaplotypeCaller \
    -R $REF \
    -I $SAMPLE3 \
    -O $GATK_OUT3
if [ $? -eq 0 ]; then
    SUCCESS "SAMPLE3 SUCCESS!!!"
else
    FAILURE "SAMPLE3 FAILED!!!"
fi

# Count and display the number of non-header lines (variants) in each VCF file
SUCCESS "                  MPILEUP                 "
echo "$filename1 - $(grep -v "#" $MPILEUP_OUT1 | wc -l)"
echo "$filename2 - $(grep -v "#" $MPILEUP_OUT2 | wc -l)"
echo "$filename3 - $(grep -v "#" $MPILEUP_OUT3 | wc -l)"
echo "------------------------------------------"
echo ""

SUCCESS "                    GATK                   "
echo "$filename1 - $(grep -v "#" $GATK_OUT1 | wc -l)"
echo "$filename2 - $(grep -v "#" $GATK_OUT2 | wc -l)"
echo "$filename3 - $(grep -v "#" $GATK_OUT3 | wc -l)"
echo "-------------------------------------------"
echo ""

# Extract specific columns (position and genotype) for each sample

grep -v "#" "$MPILEUP_OUT1" | cut -f2,6 | sort -k1,1 | awk -v OFS="," '{$1=$1; print}'> "${MPILEUP_OUT1}.cut2.sorted.csv"
grep -v "#" "$MPILEUP_OUT2" | cut -f2,6 | sort -k1,1 | awk -v OFS="," '{$1=$1; print}'> "${MPILEUP_OUT2}.cut2.sorted.csv"
grep -v "#" "$MPILEUP_OUT3" | cut -f2,6 | sort -k1,1 | awk -v OFS="," '{$1=$1; print}'> "${MPILEUP_OUT3}.cut2.sorted.csv"
                                                     
grep -v "#" "$GATK_OUT1"    | cut -f2,6 | sort -k1,1 | awk -v OFS="," '{$1=$1; print}'> "${GATK_OUT1}.cut2.sorted.csv"
grep -v "#" "$GATK_OUT2"    | cut -f2,6 | sort -k1,1 | awk -v OFS="," '{$1=$1; print}'> "${GATK_OUT2}.cut2.sorted.csv"
grep -v "#" "$GATK_OUT3"    | cut -f2,6 | sort -k1,1 | awk -v OFS="," '{$1=$1; print}'> "${GATK_OUT3}.cut2.sorted.csv"

echo "cut 2 fields files generated"

echo -e "MPILEUP-POS,MPILEUP-QUAL,GATK-POS,GATK-QUAL" > ./my-pipeline-test/"$filename1".csv
echo -e "MPILEUP-POS,MPILEUP-QUAL,GATK-POS,GATK-QUAL" > ./my-pipeline-test/"$filename2".csv
echo -e "MPILEUP-POS,MPILEUP-QUAL,GATK-POS,GATK-QUAL" > ./my-pipeline-test/"$filename3".csv

paste -d , "${MPILEUP_OUT1}.cut2.sorted.csv" "${GATK_OUT1}.cut2.sorted.csv" >> ./my-pipeline-test/"$filename1".csv
paste -d , "${MPILEUP_OUT2}.cut2.sorted.csv" "${GATK_OUT2}.cut2.sorted.csv" >> ./my-pipeline-test/"$filename2".csv
paste -d , "${MPILEUP_OUT3}.cut2.sorted.csv" "${GATK_OUT3}.cut2.sorted.csv" >> ./my-pipeline-test/"$filename3".csv

echo "Compariison files generated"

