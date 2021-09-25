# syntax = docker/dockerfile:experimental
FROM debian:buster-20200511
LABEL maintainer="Liz Dobbins <liz@axiomalaska.com>"
ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

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
COPY docker/scripts/install-conda.sh /tmp/install-conda.sh
RUN /tmp/install-conda.sh && rm -f /tmp/install-conda.sh
COPY docker/builds/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

ENV PROJECT_NAME=sccoos-sass-calibration
ENV PROJECT_ROOT=/opt/sccoos-sass-calibration
ENV CONDA_ENV=sass_calibration

COPY docker/main/entrypoint.sh /entrypoint.sh
COPY docker/scripts/install-dependencies.sh /tmp/install-dependencies.sh
RUN mkdir /tmp/envs
COPY *environment.yml /tmp/envs/

RUN --mount=type=cache,id=sass_calibration,target=/opt/conda/pkgs --mount=type=cache,id=sass_calibration,target=/root/.cache/pip /tmp/install-dependencies.sh && rm -rf /tmp/envs /tmp/install-dependencies.sh

COPY docker/scripts/install-project.sh /tmp/install-project.sh

COPY sass $PROJECT_ROOT/sass
COPY tests $PROJECT_ROOT/tests
COPY conftest.py setup.py README.md requirements.txt dev-requirements.txt $PROJECT_ROOT/

RUN --mount=type=cache,id=sass_calibration,target=/opt/conda/pkgs --mount=type=cache,id=sass_calibration,target=/root/.cache/pip /tmp/install-project.sh && rm -rf /tmp/install-project.sh
WORKDIR $PROJECT_ROOT/