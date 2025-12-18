# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/geo-stack/qtapputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

"""
Helper functions for testing.
"""

from qtpy.QtGui import QIcon
from qtpy.QtCore import QSize


def icons_are_equal(icon1: QIcon, icon2: QIcon, size: QSize = QSize(16, 16)):
    """
    Return True if two QIcon objects have identical image data at
    the given size.

    Parameters
    ----------
    icon1 : QIcon
        The first icon to compare.
    icon2 : QIcon
        The second icon to compare.
    size : QSize, optional
        The size at which to compare the icons (default is 16x16).

    Returns
    -------
    bool
        True if the icons look the same at the specified size, False otherwise.
    """
    pm1 = icon1.pixmap(size)
    pm2 = icon2.pixmap(size)
    return pm1.toImage() == pm2.toImage()
