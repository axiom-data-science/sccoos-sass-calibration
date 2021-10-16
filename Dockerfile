# syntax = docker/dockerfile:experimental
FROM mambaorg/micromamba:0.15.2

# Setting environment variables
ENV PROJECT_NAME=sccoos-sass-calibration
ENV PROJECT_ROOT=/opt/sccoos-sass-calibration

# prepping to run installation of conda packages
COPY --chown=micromamba:micromamba docker/main/entrypoint.sh /entrypoint.sh
RUN mkdir /tmp/envs
COPY --chown=micromamba:micromamba *environment.yml /tmp/envs/

RUN micromamba install -y -n base -f /tmp/envs/environment.yml && \
    micromamba install -y -n base -f /tmp/envs/test-environment.yml && \
    micromamba clean --all --yes

# copy the python code into the image (but not extraneous stuff like references and docs)
COPY --chown=micromamba:micromamba sass $PROJECT_ROOT/sass
COPY --chown=micromamba:micromamba tests $PROJECT_ROOT/tests
COPY --chown=micromamba:micromamba conftest.py setup.py README.md requirements.txt dev-requirements.txt .flake8 $PROJECT_ROOT/

# activate the conda env and install package with pip -e using an Axiom script
COPY --chown=micromamba:micromamba docker/scripts/install-project.sh /tmp/install-project.sh
RUN /tmp/install-project.sh && rm -rf /tmp/install-project.sh
WORKDIR $PROJECT_ROOT/
COPY --chown=micromamba:micromamba call_sass.py $PROJECT_ROOT
