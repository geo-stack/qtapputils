# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

"""
Tests for the fileio managers.
"""

# ---- Standard imports
import os
import os.path as osp
import stat
from unittest.mock import MagicMock, patch

# ---- Third party imports
import pytest
from qtpy.QtWidgets import QFileDialog, QMessageBox, QWidget

# ---- Local imports
from qtapputils.managers import SaveFileManager

FILECONTENT = "Test save file manager."


# =============================================================================
# ---- Fixtures
# =============================================================================

# Dummy onsave function for success
def dummy_onsave_success(filename, *args, **kwargs):
    with open(filename, "w") as f:
        f.write("data")


# Dummy onsave function for permission error
def dummy_onsave_permission_error(filename, *args, **kwargs):
    raise PermissionError("No write permission")


# Dummy onsave function for generic error
def dummy_onsave_generic_error(filename, *args, **kwargs):
    raise RuntimeError("Unexpected error")


NAMEFILTERS = {
    ".txt": "Text Files (*.txt)",
    ".csv": "CSV Files (*.csv)"
    }


@pytest.fixture
def parent(qtbot):
    parent = QWidget()
    qtbot.addWidget(parent)
    return parent


# =============================================================================
# ---- Tests
# =============================================================================
@pytest.mark.parametrize('atomic', [True, False])
def test_save_file_success(tmp_path, atomic, parent):
    """Test successful file save in atomic and non-atomic modes."""
    manager = SaveFileManager(
        namefilters=NAMEFILTERS,
        onsave=dummy_onsave_success,
        parent=parent,
        atomic=atomic
        )

    filename = osp.join(tmp_path, "output.txt")
    result = manager.save_file(filename)
    assert result == filename
    assert osp.exists(filename)
    with open(filename) as f:
        assert f.read() == "data"


@pytest.mark.parametrize('atomic', [True, False])
def test_save_file_as_success(tmp_path, mocker, atomic, parent):
    """Test successful file save using the 'Save As' dialog."""
    manager = SaveFileManager(
        namefilters=NAMEFILTERS,
        onsave=dummy_onsave_success,
        parent=parent,
        atomic=atomic
        )

    filename = osp.join(tmp_path, "newfile.csv")
    qfdialog_patcher = mocker.patch.object(
        QFileDialog,
        'getSaveFileName',
        return_value=(filename, "CSV Files (*.csv)")
        )

    suggested = osp.join(tmp_path, "suggested.txt")
    result = manager.save_file_as(suggested)

    assert qfdialog_patcher.call_count == 1
    assert result == filename
    assert osp.exists(filename)
    assert not osp.exists(suggested)


@pytest.mark.parametrize('atomic', [True, False])
def test_save_file_permission_error(tmp_path, mocker, atomic, parent):
    """Test handling of PermissionError during save with user cancel."""
    manager = SaveFileManager(
        namefilters=NAMEFILTERS,
        onsave=dummy_onsave_permission_error,
        parent=parent,
        atomic=atomic
    )

    filename = osp.join(tmp_path, "fail.txt")

    # Mock QMessageBox so no GUI appears.
    qmsgbox_patcher = mocker.patch.object(
        QMessageBox, 'warning', return_value=QMessageBox.Ok
        )

    # Mock file dialog to simulate cancel.
    qfdialog_patcher = mocker.patch.object(
        QFileDialog,
        'getSaveFileName',
        return_value=(None, None)
        )

    result = manager.save_file(str(filename))
    assert result is None
    assert qfdialog_patcher.call_count == 1
    assert qmsgbox_patcher.call_count == 1
    assert not osp.exists(filename)


@pytest.mark.parametrize('atomic', [True, False])
def test_save_file_generic_exception(tmp_path, mocker, atomic, parent):
    """Test handling of generic exception during save."""
    manager = SaveFileManager(
        namefilters=NAMEFILTERS,
        onsave=dummy_onsave_generic_error,
        parent=parent,
        atomic=atomic
        )

    filename = osp.join(tmp_path, "fail.txt")

    # Mock QMessageBox so no GUI appears.
    qmsgbox_patcher = mocker.patch.object(
        QMessageBox, 'critical', return_value=QMessageBox.Ok
        )

    result = manager.save_file(str(filename))
    assert result is None
    assert not osp.exists(filename)
    assert qmsgbox_patcher.call_count == 1


@pytest.mark.parametrize('atomic', [True, False])
def test_extension_added_if_missing(tmp_path, mocker, atomic, parent):
    """Test automatic extension addition when missing in file name."""
    manager = SaveFileManager(
        namefilters=NAMEFILTERS,
        onsave=dummy_onsave_success,
        parent=parent,
        atomic=atomic
    )

    # Simulate user picking CSV filter, but filename without extension.
    filename = osp.join(tmp_path, "nofile")

    qfdialog_patcher = mocker.patch.object(
        QFileDialog,
        'getSaveFileName',
        return_value=(filename, "CSV Files (*.csv)")
        )

    result = manager.save_file_as(filename)

    assert result == filename + '.csv'
    assert osp.exists(filename + '.csv')
    assert qfdialog_patcher.call_count == 1


@pytest.mark.parametrize('atomic', [True, False])
def test_save_file_as_cancel(tmp_path, mocker, atomic, parent):
    """Test 'Save As' dialog cancel returns None and does not save."""
    manager = SaveFileManager(
        namefilters=NAMEFILTERS,
        onsave=dummy_onsave_success,
        parent=parent,
        atomic=atomic
        )

    qfdialog_patcher = mocker.patch.object(
        QFileDialog,
        'getSaveFileName',
        return_value=("", "")
        )

    filename = osp.join(tmp_path, "suggested.txt")
    result = manager.save_file_as(filename)

    assert result is None
    assert qfdialog_patcher.call_count == 1
    assert not osp.exists(filename)


def test_atomic_save_replace_permission_error(tmp_path, mocker, parent):
    """Test atomic save when os.replace raises PermissionError."""
    manager = SaveFileManager(
        namefilters=NAMEFILTERS,
        onsave=dummy_onsave_success,
        parent=parent,
        atomic=True
    )
    filename = osp.join(tmp_path, "file.txt")

    # Patch os.replace to raise PermissionError.
    mocker.patch(
        "os.replace", side_effect=PermissionError("Permission denied")
        )

    # Patch QMessageBox.warning so no GUI appears
    qmsgbox_patcher = mocker.patch.object(
        QMessageBox, 'warning', return_value=QMessageBox.Ok
        )

    # Patch the file dialog to simulate cancel.
    qfdialog_patcher = mocker.patch.object(
        QFileDialog,
        'getSaveFileName',
        return_value=("", "")
        )

    result = manager.save_file(filename)

    assert result is None
    assert qfdialog_patcher.call_count == 1
    assert qmsgbox_patcher.call_count == 1


if __name__ == "__main__":
    pytest.main(['-x', __file__, '-v', '-rw', '-s'])
