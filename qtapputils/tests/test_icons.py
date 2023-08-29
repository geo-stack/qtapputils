# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------


"""Tests for the IconManager"""


# ---- Standard imports
import os.path as osp

# ---- Third party imports
import pytest
from qtpy.QtGui import QIcon, QPixmap, QImage

# ---- Local imports
from qtapputils.colors import RED, YELLOW
from qtapputils.icons import IconManager


# =============================================================================
# ---- Pytest fixtures
# =============================================================================
LOCAL_ICONS = {
    'alert': osp.join(osp.dirname(__file__), 'alert_icon.tiff')
    }

QTA_ICONS = {
    'home': [
        ('mdi.home',),
        {'scale_factor': 1.3}],
    'save': [
        ('mdi.content-save',),
        {'color': RED, 'scale_factor': 1.2}],
    }


# =============================================================================
# ---- Tests
# =============================================================================
def test_get_qta_icons(qtbot, tmp_path):
    """
    Test that getting qtawesome icons is working as expected.
    """
    IM = IconManager(QTA_ICONS)

    icon = IM.get_icon('home')
    expected_home_img = osp.join(osp.dirname(__file__), 'home_icon.tiff')
    assert QImage(expected_home_img) == icon.pixmap(48).toImage()

    icon = IM.get_icon('save')
    expected_home_img = osp.join(
        osp.dirname(__file__), 'red_save_icon.tiff')
    assert QImage(expected_home_img) == icon.pixmap(48).toImage()

    icon = IM.get_icon('save', color=YELLOW)
    expected_home_img = osp.join(
        osp.dirname(__file__), 'yellow_save_icon.tiff')
    assert QImage(expected_home_img) == icon.pixmap(48).toImage()

    icon = IM.get_icon('save', color='#FF007F')
    expected_home_img = osp.join(
        osp.dirname(__file__), 'pink_save_icon.tiff')
    assert QImage(expected_home_img) == icon.pixmap(48).toImage()


def test_get_local_icons(qtbot, tmp_path):
    """
    Test that getting local icons is working as expected.
    """
    IM = IconManager(QTA_ICONS, LOCAL_ICONS)

    icon = IM.get_icon('alert')
    expected_home_img = osp.join(osp.dirname(__file__), 'alert_icon.tiff')
    assert QImage(expected_home_img) == icon.pixmap(48).toImage()


if __name__ == "__main__":
    pytest.main(['-x', __file__, '-v', '-rw'])
