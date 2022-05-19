#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test calibration of O2."""

from pathlib import Path

from ..aanderaa_o2 import pressure_correction, salinity_correction

here = Path(__file__).parent


def test_pressure_correction():
    """Aanderaa manual has these example values.

    https://www.aanderaa.com/media/pdfs/oxygen-optode-4330-4835-and-4831.pdf page 19
    """
    # at 1 m depth
    # manual says 400 * 1.000032 = 400.12, which it doesn't.  Truncated?
    assert 400.0128 == 400 * pressure_correction(1)

    # at 100 m depth
    assert 412.8 == 400 * pressure_correction(1000)


def test_salinity_correction():
    """Example spreadsheet td-280-oxygen-optode-calculations.xls has these examples.

    Tricky because cells displayed rounded to 2 decimal places, but the numbers are
    really slightly different
    """
    assert 278 == salinity_correction(0, 20, 0) * 278

    O2C = salinity_correction(25.237075, 10, 0) * pressure_correction(500) * 300
    assert 259.52 == round(O2C, 2)
    assert 259.520559327266 == round(O2C, 12)

    O2C = salinity_correction(34.176, 7.701, 0) * pressure_correction(1000) * 344
    assert 284.36 == round(O2C, 2)
    assert 284.362118253806 == round(O2C, 12)

    # this one from Taylor's Notebook using real data  5/18/2022 23:30
    # Note: his Notebook had a bug
    O2C = salinity_correction(33.7113, 18.723, 0) * pressure_correction(2.553) * 67.773
    # This was his original with the bug:  assert 55.433233 == round(O2C, 6)
    assert 55.437601 == round(O2C, 6)
