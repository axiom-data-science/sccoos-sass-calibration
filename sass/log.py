#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""Logging configuration."""
import logging
import logging.config
import pkg_resources


logger = logging.getLogger('sass')


def setup_logging():
    """Initializes the project logging."""
    logging_conf_pth = pkg_resources.resource_filename('sass', 'logging.conf')
    logging.config.fileConfig(logging_conf_pth)
