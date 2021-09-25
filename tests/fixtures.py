#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""Common fixtures."""
import shutil
import tempfile
from pathlib import Path
from sass.log import logger

import pytest


@pytest.fixture(scope='module')
def tempdir() -> Path:
    """Returns the path to the temporary directory for this test."""
    pth = tempfile.mkdtemp()
    logger.info(f'generated temporary directory {pth}')
    yield Path(pth)
    logger.info('removing temporary directory')
    shutil.rmtree(pth)