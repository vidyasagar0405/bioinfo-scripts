curl -fsSL https://get.nf-test.com | bash
curl -s https://get.nextflow.io | bash
chmod +x nf-test nextflow
mv nf-test nextflow ~/.local/bin/
echo "nextflow and nf-test binary installed via curl"
pip install nf-core
echo "nf-core installed via pip"
