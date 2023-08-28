# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------


"""Tests for the IconManager"""

# Third party imports
import pytest
from qtpy.QtGui import QIcon

# Local imports
from qtapputils.colors import RED
from qtapputils.icons import IconManager


# =============================================================================
# ---- Pytest fixtures
# =============================================================================
# @pytest.fixture
# def configdir(tmpdir):
    # return osp.join(str(tmpdir), 'UserConfigTests')


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
def test_get_qta_icons(qtbot):
    """
    Test that getting qtawesome icons is working as expected.
    """
    IM = IconManager(QTA_ICONS)

    icon = IM.get_icon('home')

    # # Check each entry of the dict and try to get the respective icon
    # for name in FA_ICONS.keys():
    #     icon = get_icon(name)
    #     assert isinstance(icon, QIcon), name
    #     assert not icon.isNull(), name
    # for name in LOCAL_ICONS.keys():
    #     icon = get_icon(name)
    #     assert isinstance(icon, QIcon), name
    #     assert not icon.isNull(), name


if __name__ == "__main__":
    pytest.main(['-x', __file__, '-v', '-rw'])
