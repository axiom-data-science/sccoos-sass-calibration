#!/bin/bash

. /opt/conda/etc/profile.d/conda.sh
conda activate $CONDA_ENV
# Using eval keeps tini as pid 1, however gitlab ci uses
# a complex shell detection script as the docker command
# before executing scripts, which doesn't play nice with eval.
# Detect CI here and replace the command with a shell for CI if needed

# NOTE: Docker appears to strip quotes from CMD when it passes it to ENTRYPOINT
if [ -z "$CI" ]; then
  COMMAND="$@"
else
  echo "CI detected, replacing command"
  COMMAND="/bin/bash"
fi

echo Command: "$COMMAND"
eval "$COMMAND"