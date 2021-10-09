# syntax = docker/dockerfile:experimental

FROM debian:bullseye-slim
ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

# install curl etc so can download and install conda
RUN apt-get update && apt-get install -y \
        binutils \
        build-essential \
        bzip2 \
        ca-certificates \
        curl \
        wget \
        git \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV MINICONDA_VERSION py38_4.8.2
ENV MINICONDA_SHA256 5bbb193fd201ebe25f4aeb3c58ba83feced6a25982ef4afa86d5506c3656c142
# Installs Conda and sets up the conda bash profile
COPY docker/scripts/install-conda.sh /tmp/install-conda.sh
RUN /tmp/install-conda.sh && rm -f /tmp/install-conda.sh

# this is a wrapper so that both I and the GitLab CI can use the container
COPY docker/builds/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Setting environment variables
ENV PROJECT_NAME=sccoos-sass-calibration
ENV PROJECT_ROOT=/opt/sccoos-sass-calibration
ENV CONDA_ENV=sass_env

# prepping to run installation of conda packages
COPY docker/main/entrypoint.sh /entrypoint.sh
RUN mkdir /tmp/envs
COPY *environment.yml /tmp/envs/

# install the conda packages with an Axiom script
COPY docker/scripts/install-dependencies.sh /tmp/install-dependencies.sh
RUN --mount=type=cache,id=sass_env,target=/opt/conda/pkgs \
    --mount=type=cache,id=sass_env,target=/root/.cache/pip \
    /tmp/install-dependencies.sh && rm -rf /tmp/envs /tmp/install-dependencies.sh

# copy the python code into the image (but not extraneous stuff like references and docs)
COPY sass $PROJECT_ROOT/sass
COPY tests $PROJECT_ROOT/tests
COPY conftest.py setup.py README.md requirements.txt dev-requirements.txt $PROJECT_ROOT/

# activate the conda env and install package with pip -e using an Axiom script
COPY docker/scripts/install-project.sh /tmp/install-project.sh
RUN --mount=type=cache,id=sass_env,target=/opt/conda/pkgs \
    --mount=type=cache,id=sass_env,target=/root/.cache/pip \
    /tmp/install-project.sh && rm -rf /tmp/install-project.sh
WORKDIR $PROJECT_ROOT/
COPY call_sass.py $PROJECT_ROOT



