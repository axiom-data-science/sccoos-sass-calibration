#!/bin/bash
# docker/scripts/install-conda.sh
# Installs Conda and sets up the conda bash profile
set -eu

curl -k -o /miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-$MINICONDA_VERSION-Linux-x86_64.sh
echo $MINICONDA_SHA256 /miniconda.sh | sha256sum --check
/bin/bash /miniconda.sh -b -p /opt/conda
rm /miniconda.sh
/opt/conda/bin/conda clean -afy
ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh
echo ". /opt/conda/etc/profile.d/conda.sh" >> /etc/profile
echo "conda activate base" >> /etc/profile
find /opt/conda/ -follow -type f -name '*.a' -delete
find /opt/conda/ -follow -type f -name '*.js.map' -delete
/opt/conda/bin/conda update -n base conda
/opt/conda/bin/conda install -y conda-build anaconda-client
/opt/conda/bin/conda install -y -c conda-forge mamba
/opt/conda/bin/conda clean -afy