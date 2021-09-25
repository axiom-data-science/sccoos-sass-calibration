FROM continuumio/miniconda3:4.6.14
MAINTAINER Luke Campbell <luke@axds.co>

RUN conda config --set always_yes yes \
    && conda config --append channels conda-forge \
    && conda install mamba

RUN mamba create -y --name flakeit python=3.8 \
    && mamba install -y --name flakeit flake8 flake8-docstrings


COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["flake8", "sass"]