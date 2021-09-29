#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""Package Root."""

__all__ = ['utilities', 'instrument_set', 'logger']

import logging
import pkg_resources

import logging.config


def setup_logging(name):
    """Initializes the project logging."""
    logger = logging.getLogger('sass')

    logging_conf_pth = pkg_resources.resource_filename(name, 'logging.conf')
    logging.config.fileConfig(logging_conf_pth)

    return logger


logger = setup_logging(__name__)
