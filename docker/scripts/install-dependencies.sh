#!/bin/bash
set -e
. /opt/conda/etc/profile.d/conda.sh
conda activate base
if [[ -e /tmp/envs/full-environment.yml ]]; then
    mamba env create -f /tmp/envs/full-environment.yml
    exit 0
fi
mamba env create -f /tmp/envs/environment.yml
if [[ -e /tmp/envs/test-environment.yml ]]; then
    mamba env update -f /tmp/envs/test-environment.yml
fi