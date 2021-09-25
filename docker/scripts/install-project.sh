#!/bin/bash
set -e
. /opt/conda/etc/profile.d/conda.sh
conda activate $CONDA_ENV
cd $PROJECT_ROOT
pip install -e .