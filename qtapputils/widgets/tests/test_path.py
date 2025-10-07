# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

"""
Tests for widgets in the path.py module.
"""

# ---- Standard imports
import os.path as osp

# ---- Third party imports
import pytest
from qtpy.QtCore import Qt
from qtpy.QtGui import QIcon

# ---- Local imports
from qtapputils.widgets.path import PathBoxWidget, QFileDialog


# =============================================================================
# ---- Fixtures
# =============================================================================
@pytest.fixture
def pathbox(qtbot):
    pathbox = PathBoxWidget(
        parent=None,
        path_type='getSaveFileName',
        filters=None
        )
    qtbot.addWidget(pathbox)
    pathbox.show()
    return pathbox


# =============================================================================
# ---- Tests for the PathBoxWidget
# =============================================================================
def test_initialization_no_icon(qtbot):
    pathbox = PathBoxWidget()
    qtbot.addWidget(pathbox)

    assert pathbox.is_empty()
    assert not pathbox.is_valid()
    assert pathbox.path() == ""
    assert pathbox.directory()


def test_initialization_with_icon(qtbot):
    icon = QIcon()
    pathbox = PathBoxWidget(browse_icon=icon)
    qtbot.addWidget(pathbox)

    assert pathbox.is_empty()
    assert not pathbox.is_valid()


def test_set_and_get_path_valid(tmp_path, qtbot):
    # Create a valid file
    f = tmp_path / "myfile.txt"
    f.write_text("content")

    pathbox = PathBoxWidget(path_type="getOpenFileName")
    qtbot.addWidget(pathbox)
    pathbox.set_path(str(f))

    assert not pathbox.is_empty()
    assert pathbox.is_valid()
    assert pathbox.path() == str(f)
    assert pathbox.directory() == str(tmp_path)


def test_set_and_get_path_invalid(qtbot):
    pathbox = PathBoxWidget()
    qtbot.addWidget(pathbox)
    pathbox.set_path("/tmp/nonexistent_file.txt")

    assert pathbox.path() == "/tmp/nonexistent_file.txt"
    assert pathbox.directory() == osp.expanduser('~')
    assert not pathbox.is_valid()


def test_set_directory_valid(tmp_path, qtbot):
    d = tmp_path / "dir"
    d.mkdir()

    pathbox = PathBoxWidget()
    qtbot.addWidget(pathbox)
    pathbox.set_directory(str(d))

    assert pathbox.directory() == str(d)


def test_set_directory_invalid(qtbot):
    pathbox = PathBoxWidget()
    qtbot.addWidget(pathbox)
    pathbox.set_directory("/tmp/nonexistent_dir")

    # Should fallback to home if directory is invalid
    assert pathbox.directory() == osp.expanduser('~')


def test_signal_emitted_on_path_change(tmp_path, qtbot):
    f = tmp_path / "file.txt"
    f.write_text("abc")

    pathbox = PathBoxWidget()
    qtbot.addWidget(pathbox)

    with qtbot.waitSignal(pathbox.sig_path_changed) as blocker:
        pathbox.set_path(str(f))
    assert blocker.args == [str(f)]


def test_browse_path_get_existing_directory(mocker, tmp_path, qtbot):
    d = tmp_path / "bro_dir"
    d.mkdir()

    pathbox = PathBoxWidget(path_type="getExistingDirectory")
    qtbot.addWidget(pathbox)

    qfdialog_patcher = mocker.patch.object(
        QFileDialog,
        'getExistingDirectory',
        return_value=str(d)
        )

    pathbox.browse_path()
    assert qfdialog_patcher.call_count == 1
    assert pathbox.path() == str(d)
    assert pathbox.directory() == str(tmp_path)
    assert pathbox.is_valid()


def test_browse_path_get_open_file_name(mocker, tmp_path, qtbot):
    f = tmp_path / "bro_file.txt"
    f.write_text("abc")

    pathbox = PathBoxWidget(path_type="getOpenFileName")
    qtbot.addWidget(pathbox)

    qfdialog_patcher = mocker.patch.object(
        QFileDialog,
        'getOpenFileName',
        return_value=(str(f), "")
        )

    pathbox.browse_path()
    assert qfdialog_patcher.call_count == 1
    assert pathbox.path() == str(f)
    assert pathbox.directory() == str(tmp_path)
    assert pathbox.is_valid()


def test_browse_path_get_save_file_name(mocker, tmp_path, qtbot):
    f = tmp_path / "save_file.txt"

    pathbox = PathBoxWidget(path_type="getSaveFileName")
    qtbot.addWidget(pathbox)

    qfdialog_patcher = mocker.patch.object(
        QFileDialog,
        'getSaveFileName',
        return_value=(str(f), "")
        )

    pathbox.browse_path()
    assert qfdialog_patcher.call_count == 1
    assert pathbox.path() == str(f)
    assert pathbox.directory() == str(tmp_path)


if __name__ == "__main__":
    pytest.main(['-x', osp.basename(__file__), '-v', '-rw'])
