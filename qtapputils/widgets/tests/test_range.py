# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

"""Tests for the RangeSpinBox and RangeWidget."""

from qtpy.QtCore import Qt
from qtapputils.widgets import RangeSpinBox, RangeWidget
import pytest


# =============================================================================
# Fixtures
# =============================================================================
@pytest.fixture
def range_spinbox(qtbot):
    spinbox = RangeSpinBox(
        minimum=3, maximum=101, singlestep=0.1, decimals=2, value=74.21)
    qtbot.addWidget(spinbox)
    spinbox.show()

    assert spinbox.maximum() == 101
    assert spinbox.minimum() == 3
    assert spinbox.decimals() == 2
    assert spinbox.singleStep() == 0.1
    assert spinbox.value() == 74.21

    return spinbox


@pytest.fixture
def range_widget(qtbot):
    widget = RangeWidget(null_range_ok=False)
    qtbot.addWidget(widget.spinbox_start)
    qtbot.addWidget(widget.spinbox_end)
    widget.spinbox_start.show()
    widget.spinbox_end.show()

    assert widget.start() == 0
    assert widget.end() == 99.99

    assert widget.spinbox_start.minimum() == 0
    assert widget.spinbox_start.maximum() == 99.98
    assert widget.spinbox_start.decimals() == 2
    assert widget.spinbox_start.singleStep() == 0.01
    assert widget.spinbox_start.value() == 0

    assert widget.spinbox_end.minimum() == 0.01
    assert widget.spinbox_end.maximum() == 99.99
    assert widget.spinbox_end.decimals() == 2
    assert widget.spinbox_end.singleStep() == 0.01
    assert widget.spinbox_end.value() == 99.99

    return widget


# =============================================================================
# Tests
# =============================================================================
def test_range_spinbox(range_spinbox, qtbot):
    """
    Test that the RangeSpinBox is working as expected.
    """
    # Test entering a value above the maximum.
    range_spinbox.clear()
    qtbot.keyClicks(range_spinbox, '120')
    qtbot.keyClick(range_spinbox, Qt.Key_Enter)
    assert range_spinbox.value() == 101

    # Test entering a value below the minimum.
    range_spinbox.clear()
    qtbot.keyClicks(range_spinbox, '-12')
    qtbot.keyClick(range_spinbox, Qt.Key_Enter)
    assert range_spinbox.value() == 3

    # Test entering a valid value.
    range_spinbox.clear()
    qtbot.keyClicks(range_spinbox, '45.3')
    qtbot.keyClick(range_spinbox, Qt.Key_Enter)
    assert range_spinbox.value() == 45.3

    # Test entering an intermediate value.
    range_spinbox.clear()
    qtbot.keyClicks(range_spinbox, '-')
    qtbot.keyClick(range_spinbox, Qt.Key_Enter)
    assert range_spinbox.value() == 45.3

    # Test entering invalid values.
    range_spinbox.clear()
    qtbot.keyClicks(range_spinbox, '23..a-45')
    qtbot.keyClick(range_spinbox, Qt.Key_Enter)
    assert range_spinbox.value() == 23.45


def test_range_widget(range_widget, qtbot):
    """
    Test that the RangeWidget is working as expected.
    """
    # Test set_minimum functionality.
    range_widget.set_minimum(24)
    assert range_widget.start() == 24
    assert range_widget.end() == 99.99

    assert range_widget.spinbox_start.minimum() == 24
    assert range_widget.spinbox_start.maximum() == 99.98
    assert range_widget.spinbox_start.value() == 24

    assert range_widget.spinbox_end.minimum() == 24.01
    assert range_widget.spinbox_end.maximum() == 99.99
    assert range_widget.spinbox_end.value() == 99.99

    # Test set_maximum functionality.
    range_widget.set_maximum(74)
    assert range_widget.start() == 24
    assert range_widget.end() == 74

    assert range_widget.spinbox_start.minimum() == 24
    assert range_widget.spinbox_start.maximum() == 73.99
    assert range_widget.spinbox_start.value() == 24

    assert range_widget.spinbox_end.minimum() == 24.01
    assert range_widget.spinbox_end.maximum() == 74.00
    assert range_widget.spinbox_end.value() == 74.00

    # Test set_range functionality.
    range_widget.set_range(48, 62.3)
    assert range_widget.start() == 48
    assert range_widget.end() == 62.3

    assert range_widget.spinbox_start.minimum() == 24
    assert range_widget.spinbox_start.maximum() == 62.29
    assert range_widget.spinbox_start.value() == 48

    assert range_widget.spinbox_end.minimum() == 48.01
    assert range_widget.spinbox_end.maximum() == 74.00
    assert range_widget.spinbox_end.value() == 62.3

    # Test entering values in spinbox.
    range_widget.spinbox_start.clear()
    qtbot.keyClicks(range_widget.spinbox_start, '43.51')
    qtbot.keyClick(range_widget.spinbox_start, Qt.Key_Enter)
    assert range_widget.start() == 43.51
    assert range_widget.end() == 62.3

    assert range_widget.spinbox_start.minimum() == 24
    assert range_widget.spinbox_start.maximum() == 62.29
    assert range_widget.spinbox_start.value() == 43.51

    assert range_widget.spinbox_end.minimum() == 43.52
    assert range_widget.spinbox_end.maximum() == 74.00
    assert range_widget.spinbox_end.value() == 62.3


if __name__ == '__main__':
    pytest.main(['-x', __file__, '-vv', '-rw'])
