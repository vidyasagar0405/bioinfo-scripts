GENE="$1"
wget "https://www.ebi.ac.uk/gwas/api/search/downloads?q=ensemblMappedGenes:${GENE}&amp;pvalfilter=&amp;orfilter=&amp;betafilter=&amp;datefilter=&amp;genomicfilter=&amp;genotypingfilter[]=&amp;traitfilter[]=&amp;dateaddedfilter=&amp;facet=association&amp;efo=true"
