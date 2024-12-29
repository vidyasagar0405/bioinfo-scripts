#!/usr/bin/env bash

# Function to display usage
usage() {
    echo "Usage: conda-manager [--install | --set-env | --remove-env | --dry-run | --help]"
    echo ""
    echo "Options:"
    echo "  --install           Install Miniconda"
    echo "  --set-env           Create Conda environments"
    echo "  --remove-env        Remove Conda environment"
    echo "  --add-to-path       Adds conda-manager to ~/.local/bin"
    echo "  --dry-run           Simulate actions without executing them"
    echo "  --help              Display this help message"
}

# Function to install Miniconda
install_miniconda() {

    echo "Removing existing miniconda"
    rm -rf ~/miniconda3/
    echo "Installing Miniconda..."
    mkdir -p ~/miniconda3
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
    bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
    rm ~/miniconda3/miniconda.sh
    source ~/miniconda3/bin/activate
    conda init --all
    conda config --set changeps1 false
    echo "Miniconda installed successfully."
}

# Function to create Conda environments
create_envs() {
    echo "Creating Conda environments..."
    declare -A envs_packages=(
        [QC]="fastqc multiqc"
        [trimmomatic]="trimmomatic"
        [samtools]="bwa samtools"
        [picard]="picard"
        [gatk]="gatk"
        [snpEff]="snpEff"
    )

    for env in "${!envs_packages[@]}"; do
        if [[ "$DRY_RUN" == true ]]; then
            echo "[DRY RUN] Would create environment '$env' with packages: ${envs_packages[$env]}"
        else
            if conda info --envs | grep -q "^$env[[:space:]]"; then
                echo "Environment '$env' already exists. Skipping creation."
            else
                conda create -y -n "$env" -c conda-forge -c bioconda ${envs_packages[$env]}
            fi
        fi
    done

    conda env list
    echo "Conda environments creation process completed."
}

# Function to remove a Conda environment
remove_env() {
    echo "Removing Conda environments..."
    declare -A envs=(
        [QC]
        [trimmomatic]
        [samtools]
        [picard]
        [gatk]
        [snpEff]
    )

    for env in "${!envs[@]}"; do
        if [[ "$DRY_RUN" == true ]]; then
            echo "[DRY RUN] Would remove environment '$env'"
        else
            if conda info --envs | grep -q "^$env[[:space:]]"; then
                conda env remove -y -n "$env"
            else
                echo "Environment '$env' does not exist. Skipping removal."
            fi
        fi
    done

    conda env list
    echo "Conda environments removal process completed."
}

# Main script logic
DRY_RUN=false
if [[ $# -eq 0 ]]; then
    echo "Error: No arguments provided."
    usage
    exit 1
fi

if [[ $# -gt 2 ]]; then
    echo "Error: Too many arguments provided."
    usage
    exit 1
fi

if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    shift
fi

case "$1" in
    --install)
        install_miniconda
        ;;
    --set-env)
        create_envs
        ;;
    --remove-env)
        remove_env
        ;;
    --add-to-path)
        cd ~/.local/bin/
        ln -s ~/Documents/bioinfo/bioinfo-scripts/conda-manager.sh conda-manager
        cd -
        ;;
    --help)
        usage
        ;;


    *)
        echo "Error: Unknown option '$1'. Valid options are: --install, --set-env, --remove-env, --dry-run, --help."
        usage
        exit 1
        ;;
esac
