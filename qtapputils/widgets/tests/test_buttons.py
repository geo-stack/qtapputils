# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/geo-stack/qtapputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

import pytest
from qtpy.QtGui import QIcon, QPixmap
from qtpy.QtCore import Qt
from qtpy.QtTest import QSignalSpy

from qtapputils.widgets.buttons import MultiStateToolButton
from qtapputils.testing import icons_are_equal


@pytest.fixture
def icons():
    # Create dummy QIcons for testing
    pixmap1 = QPixmap(16, 16)
    pixmap1.fill(Qt.red)
    pixmap2 = QPixmap(16, 16)
    pixmap2.fill(Qt.green)
    pixmap3 = QPixmap(16, 16)
    pixmap3.fill(Qt.blue)
    return [QIcon(pixmap1), QIcon(pixmap2), QIcon(pixmap3)]


@pytest.fixture
def button(icons, qtbot):

    btn = MultiStateToolButton(icons)
    qtbot.addWidget(btn)
    btn.show()
    qtbot.waitUntil(btn.isVisible)

    assert btn.current_index() == 0
    assert icons_are_equal(btn.icon(), icons[0])

    return btn


def test_cycle_icons(button, qtbot, icons):
    """Test icon cycles forward with clicks and wraps around."""
    signal_spy = QSignalSpy(button.sig_index_changed)

    qtbot.mouseClick(button, Qt.LeftButton)

    assert len(signal_spy) == 1
    assert signal_spy[-1] == [1]
    assert icons_are_equal(button.icon(), icons[1])

    qtbot.mouseClick(button, Qt.LeftButton)

    assert len(signal_spy) == 2
    assert signal_spy[-1] == [2]
    assert icons_are_equal(button.icon(), icons[2])

    # Should wrap back to 0.
    qtbot.mouseClick(button, Qt.LeftButton)

    assert len(signal_spy) == 3
    assert signal_spy[-1] == [0]
    assert icons_are_equal(button.icon(), icons[0])


def test_set_index(button, qtbot, icons):
    """Test icon is set as expected when index is set programattically."""
    signal_spy = QSignalSpy(button.sig_index_changed)

    # Should wrap back to len(icons) - 1.
    button.set_current_index(-1)

    assert len(signal_spy) == 1
    assert signal_spy[-1] == [2]
    assert icons_are_equal(button.icon(), icons[2])

    # Should wrap back to 0.
    button.set_current_index(100)

    assert len(signal_spy) == 2
    assert signal_spy[-1] == [0]
    assert icons_are_equal(button.icon(), icons[0])

    # Should do nothing.
    button.set_current_index(100)

    assert len(signal_spy) == 2
    assert signal_spy[-1] == [0]
    assert icons_are_equal(button.icon(), icons[0])


if __name__ == '__main__':
    pytest.main(['-x', __file__, '-vv', '-rw'])
