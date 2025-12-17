# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

"""
Tests for the Centralized Shortcut Manager
"""

import configparser as cp
import pytest
from unittest.mock import Mock
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

from qtapputils.managers.shortcuts import (
    ShortcutManager, ShortcutDefinition, ShortcutItem,
    ActionMenuSyncTranslator, TitleSyncTranslator, ToolTipSyncTranslator)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def widget(qtbot):
    """Create a basic QWidget for testing."""
    w = QPushButton('')
    qtbot.addWidget(w)
    return w


@pytest.fixture
def userconfig():
    """Create a mock UserConfig object."""

    class UserConfigMock():

        def __init__(self):
            self._config = {'file/save': 'Ctrl+S',
                            'file/open': 'Ctrl+O'}

        def get(self, section, option):
            if section != 'shortcuts':
                raise KeyError(
                    f"'section' should be 'shortcuts', but got {section}.")

            if option in self._config:
                return self._config[option]
            else:
                raise cp.NoOptionError(option, section)

        def set(self, section, option, value):
            if section != 'shortcuts':
                raise KeyError(
                    f"'section' should be 'shortcuts', but got {section}.")
            self._config[option] = value

    return UserConfigMock()


@pytest.fixture
def definition():
    """Create a sample ShortcutDefinition."""
    return ShortcutDefinition(
        context="file",
        name="save",
        key_sequence="Ctrl+S",
        description="Save file"
        )


@pytest.fixture
def shortcut_item(definition, widget):
    """Create a ShortcutItem for testing."""
    title = "Save"
    text = "Save the file."
    alt_text = "Save with the file with {sc_str}."

    return ShortcutItem(
        definition=definition,
        callback=Mock(),
        parent=widget,
        synced_ui_data=[
            (widget.setToolTip,
             ToolTipSyncTranslator(title, text, alt_text)),
            (widget.setText,
             TitleSyncTranslator(title))
            ],
        )


@pytest.fixture
def populated_manager(widget):
    """Create a manager with multiple shortcuts, some bound."""
    manager = ShortcutManager()

    manager.declare_shortcut(
        context="file", name="save", default_key_sequence="Ctrl+S"
        )
    manager.declare_shortcut(
        context="file", name="open", default_key_sequence="Ctrl+O"
        )
    manager.declare_shortcut(
        context="edit", name="copy", default_key_sequence="Ctrl+C"
        )
    manager.declare_shortcut(
        context="_", name="quit", default_key_sequence="Ctrl+Q"
        )

    # Bind only some shortcuts
    manager.bind_shortcut(
        context="file", name="save", callback=Mock(), parent=widget
        )
    manager.bind_shortcut(
        context="edit", name="copy", callback=Mock(), parent=widget
        )

    return manager


# =============================================================================
# Tests
# =============================================================================
def test_uisync_translator():

    # Test action menu with and without shortcut.
    translator = ActionMenuSyncTranslator("Save")
    assert translator("Ctrl+S") == ("Save\tCtrl+S",)
    assert translator("") == ("Save",)

    # Test title sync translator with and without shortcut.
    translator = TitleSyncTranslator("Save File")
    assert translator("Ctrl+S") == ("Save File (Ctrl+S)",)
    assert translator("") == ("Save File",)

    # Test tooltip sync translator with and without shortcut.
    translator = ToolTipSyncTranslator(
        title="Save",
        text="Save the file.",
        alt_text="Save with the file with {sc_str}.")
    assert translator("Ctrl+S") == (
        "<p style='white-space:pre'>"
        "<b>Save (Ctrl+S)</b></p>"
        "<p>Save with the file with Ctrl+S.</p>", )
    assert translator("") == (
        "<p style='white-space:pre'>"
        "<b>Save</b></p>"
        "<p>Save the file.</p>", )


def test_shortcut_definition(definition):
    assert definition.context_name == "file/save"
    assert definition.qkey_sequence == QKeySequence("Ctrl+S")
    assert definition.is_bound is False
    assert definition.shortcut is None

    # Test the shortcut definition is bound after binding.
    definition._shortcut = Mock()
    assert definition.is_bound is True
    assert definition.shortcut is not None


def test_shortcut_item(shortcut_item, widget, qtbot):
    widget.show()
    qtbot.wait(300)

    # Initially not activated.
    assert shortcut_item.shortcut is None
    assert widget.text() == 'Save'
    assert widget.toolTip() == (
        "<p style='white-space:pre'>"
        "<b>Save</b></p>"
        "<p>Save the file.</p>")

    # Activate shortcut item.
    shortcut_item.activate()
    assert shortcut_item.shortcut is not None
    assert shortcut_item.enabled is True
    assert widget.text() == 'Save (Ctrl+S)'
    assert widget.toolTip() == (
        "<p style='white-space:pre'>"
        "<b>Save (Ctrl+S)</b></p>"
        "<p>Save with the file with Ctrl+S.</p>")

    # Test callback connection.
    qtbot.keyPress(widget, Qt.Key_S, modifier=Qt.ControlModifier)
    shortcut_item.callback.call_count == 1

    # Change key sequence
    shortcut_item.set_keyseq("Ctrl+A")
    assert widget.text() == 'Save (Ctrl+A)'
    assert widget.toolTip() == (
        "<p style='white-space:pre'>"
        "<b>Save (Ctrl+A)</b></p>"
        "<p>Save with the file with Ctrl+A.</p>")

    # Test callback connection.
    qtbot.keyPress(widget, Qt.Key_A, modifier=Qt.ControlModifier)
    shortcut_item.callback.call_count == 2

    # Disable the shortcut item.
    shortcut_item.set_enabled(False)
    assert shortcut_item.shortcut is not None
    assert shortcut_item.enabled is False
    assert widget.text() == 'Save (Ctrl+A)'
    assert widget.toolTip() == (
        "<p style='white-space:pre'>"
        "<b>Save (Ctrl+A)</b></p>"
        "<p>Save with the file with Ctrl+A.</p>")

    qtbot.keyPress(widget, Qt.Key_S, modifier=Qt.ControlModifier)
    shortcut_item.callback.call_count == 2

    # Deactivate shortcut item.
    shortcut_item.deactivate()
    assert shortcut_item.shortcut is None
    assert shortcut_item.enabled is False
    assert widget.text() == 'Save'
    assert widget.toolTip() == (
        "<p style='white-space:pre'>"
        "<b>Save</b></p>"
        "<p>Save the file.</p>")

    qtbot.keyPress(widget, Qt.Key_S, modifier=Qt.ControlModifier)
    shortcut_item.callback.call_count == 2


# =============================================================================
# ShortcutManager Tests
# =============================================================================

def test_declare_shortcut(capsys):
    manager = ShortcutManager()

    definition = manager.declare_shortcut(
        context="file",
        name="save",
        default_key_sequence="Ctrl+S",
        description="Save file"
        )

    assert isinstance(definition, ShortcutDefinition)
    assert definition.context == "file"
    assert definition.key_sequence == "Ctrl+S"
    assert definition.qkey_sequence.toString() == "Ctrl+S"

    # Test duplicate raise an error.
    with pytest.raises(ValueError, match="already declared"):
        manager.declare_shortcut(
            context="file",
            name="save",
            default_key_sequence="Ctrl+Shift+S"
            )

    # Test invalid key.
    captured = capsys.readouterr()
    assert "ShortcutError" not in captured.out

    definition = manager.declare_shortcut(
        context="file",
        name="load",
        default_key_sequence="InvalidKey123! @#"
        )

    captured = capsys.readouterr()
    assert "ShortcutError" in captured.out

    assert isinstance(definition, ShortcutDefinition)
    assert definition.context == "file"
    assert definition.key_sequence == ''
    assert definition.qkey_sequence.toString() == ''

    # Bulk shortcuts declaration.
    shortcuts = [
        {'context': 'file', 'name': 'print', 'default_key_sequence': 'Ctrl+P'},
        {'context': 'file', 'name': 'open', 'default_key_sequence': 'Ctrl+O'},
        {'context': 'edit', 'name': 'copy', 'default_key_sequence': 'Ctrl+C'}
        ]
    manager.declare_shortcuts(shortcuts)

    assert len(list(manager.iter_definitions())) == 5


def test_declare_shortcut_with_userconfig(userconfig):
    manager = ShortcutManager(userconfig=userconfig)

    # Declare shortcuts that are in the user config.
    manager.declare_shortcut(
        context="file", name="save", default_key_sequence="Ctrl+Shift+S"
        )

    definition = manager._definitions['file/save']
    assert definition.context == "file"
    assert definition.name == "save"
    assert definition.qkey_sequence.toString() == "Ctrl+S"

    manager.declare_shortcut(
        context="file", name="open"
        )

    definition = manager._definitions['file/open']
    assert definition.context == "file"
    assert definition.name == "open"
    assert definition.qkey_sequence.toString() == "Ctrl+O"

    # Declare shortcuts that are NOT in the user config.
    manager.declare_shortcut(
        context="edit", name="copy", default_key_sequence="Ctrl+C"
        )

    definition = manager._definitions['edit/copy']
    assert definition.context == "edit"
    assert definition.name == "copy"
    assert definition.qkey_sequence.toString() == "Ctrl+C"

    manager.declare_shortcut(
        context="edit", name="paste"
        )

    definition = manager._definitions['edit/paste']
    assert definition.context == "edit"
    assert definition.name == "paste"
    assert definition.qkey_sequence.toString() == ""


def test_bind_shortcut(widget):
    manager = ShortcutManager()

    # Bind a shortcut.
    manager.declare_shortcut(
        context="file", name="save", default_key_sequence="Ctrl+S"
        )
    shortcut_item = manager.bind_shortcut(
        context="file", name="save", callback=Mock(), parent=widget
        )
    assert isinstance(shortcut_item, ShortcutItem)
    assert shortcut_item.shortcut is not None

    # Unbind a shortcut.
    manager.unbind_shortcut("file", "save")
    assert shortcut_item.shortcut is None

    # Bind again after unbinding.
    shortcut_item = manager.bind_shortcut(
        context="file", name="save", callback=Mock(), parent=widget
        )
    assert shortcut_item.shortcut is not None

    # Bind a shortcut, but set 'activate' to False.
    manager.declare_shortcut(
        context="file", name="open", default_key_sequence="Ctrl+O"
        )
    shortcut_item = manager.bind_shortcut(
        context="file", name="open", callback=Mock(), parent=widget,
        activate=False
        )
    assert isinstance(shortcut_item, ShortcutItem)
    assert shortcut_item.shortcut is None

    # Assert that trying to bind a shortcut that was not declare
    # first raise an error
    with pytest.raises(ValueError, match="was not declared"):
        manager.bind_shortcut(
            context="file", name="edit", callback=Mock(), parent=widget
            )

    # Assert that trying to bind a shortcut that is already bound raises
    # an error.
    with pytest.raises(ValueError, match="already bound"):
        manager.bind_shortcut(
            context="file", name="save", callback=Mock(), parent=widget
            )


def test_set_shortcut(widget, capsys):
    manager = ShortcutManager()

    manager.declare_shortcut(
        context="file", name="save", default_key_sequence="Ctrl+S"
        )

    # Set a key sequence on an unbound shortcut.
    assert manager.set_shortcut("file", "save", "Ctrl+Shift+S")
    assert [d.key_sequence for d in manager.iter_definitions()] == [
        "Ctrl+Shift+S"]

    # Bind and set a new key sequence.
    manager.bind_shortcut(
        context="file", name="save", callback=Mock(), parent=widget
        )

    assert manager.set_shortcut("file", "save", "Alt+S")
    assert [d.key_sequence for d in manager.iter_definitions()] == [
        "Alt+S"]

    # Try setting a key sequence to an invalid shortcut name.
    captured = capsys.readouterr()
    assert "ShortcutError" not in captured.out

    result = manager.set_shortcut("file", "nonexistent", "Ctrl+S")
    assert result is False

    captured = capsys.readouterr()
    assert "ShortcutError" in captured.out


def test_set_shortcut_with_userconfig(widget, userconfig, capsys):
    manager = ShortcutManager(userconfig=userconfig)

    manager.declare_shortcut(
        context="file", name="save", default_key_sequence="Ctrl+Shift+S"
        )
    manager.bind_shortcut(
        context="file", name="save", callback=Mock(), parent=widget
        )
    assert [d.key_sequence for d in manager.iter_shortcuts()] == [
        "Ctrl+S"]

    # Set a new key sequence and assert the userconfig is updated
    # when sync_userconfig is set to True.
    manager.set_shortcut(
        "file", "save", "Ctrl+Shift+S", sync_userconfig=False
        )
    assert [d.key_sequence for d in manager.iter_shortcuts()] == [
        "Ctrl+Shift+S"]
    assert userconfig._config['file/save'] == 'Ctrl+S'

    manager.set_shortcut(
        "file", "save", "Ctrl+Shift+S", sync_userconfig=True
        )
    assert [d.key_sequence for d in manager.iter_shortcuts()] == [
        "Ctrl+Shift+S"]
    assert userconfig._config['file/save'] == "Ctrl+Shift+S"

    # Set an invalid key sequence.
    captured = capsys.readouterr()
    assert "ShortcutError" not in captured.out

    manager.set_shortcut(
        "file", "save", "InvalidKey123! @#", sync_userconfig=True
        )

    captured = capsys.readouterr()
    assert "ShortcutError" in captured.out
    assert [d.key_sequence for d in manager.iter_shortcuts()] == [
        "Ctrl+Shift+S"]
    assert userconfig._config['file/save'] == "Ctrl+Shift+S"


def test_iter_definitions(populated_manager):
    all_defs = list(populated_manager.iter_definitions())
    assert len(all_defs) == 4

    file_defs = list(populated_manager.iter_definitions(context="file"))
    assert len(file_defs) == 2
    assert all(d.context == "file" for d in file_defs)


def test_iter_bound_shortcuts(populated_manager):
    all_bound = list(populated_manager.iter_shortcuts())
    assert len(all_bound) == 2

    file_bound = list(populated_manager.iter_shortcuts(context="file"))
    assert len(file_bound) == 1
    assert file_bound[0].definition. context == "file"


def test_blocklist(userconfig, capsys):
    manager = ShortcutManager(blocklist=['Ctrl+Z'])

    captured = capsys.readouterr()
    assert "ShortcutError" not in captured.out

    definition = manager.declare_shortcut(
        context="file",
        name="save",
        default_key_sequence='Ctrl+Z',
        description="Save file"
        )
    assert definition.qkey_sequence.toString() == ''

    captured = capsys.readouterr()
    assert "ShortcutError" in captured.out

    assert manager.set_shortcut("file", "save", 'Ctrl+S')
    assert definition.qkey_sequence.toString() == 'Ctrl+S'

    assert manager.set_shortcut("file", "save", 'Ctrl+Z') is False
    assert definition.qkey_sequence.toString() == 'Ctrl+S'

    captured = capsys.readouterr()
    assert "ShortcutError" in captured.out


def test_find_conflicts(populated_manager, capsys):
    # context="file", name="save", default_key_sequence="Ctrl+S"
    # context="file", name="open", default_key_sequence="Ctrl+O"
    # context="edit", name="copy", default_key_sequence="Ctrl+C"
    # context="_", name="quit", default_key_sequence="Ctrl+Q"

    # Same context, same key - should conflict.
    conflicts = populated_manager.find_conflicts("file", "newaction", "Ctrl+S")
    assert len(conflicts) == 1
    assert conflicts[0].name == "save"

    # Different context, no overlap - no conflict
    conflicts = populated_manager.find_conflicts("view", "zoom", "Ctrl+Z")
    assert len(conflicts) == 0

    # Global context "_" conflicts with any context
    conflicts = populated_manager.find_conflicts("file", "newaction", "Ctrl+Q")
    assert len(conflicts) == 1
    assert conflicts[0].name == "quit"

    # Empty key sequence - no conflict
    conflicts = populated_manager.find_conflicts("file", "newaction", "")
    assert len(conflicts) == 0

    # Same shortcut shouldn't conflict with itself.
    conflicts = populated_manager.find_conflicts("file", "save", "Ctrl+S")
    assert len(conflicts) == 0

    # Declare with conflicting key - the 'default_key_sequence' is ignored.
    captured = capsys.readouterr()
    assert "ShortcutError" not in captured.out

    definition = populated_manager.declare_shortcut(
        context="file", name="save_as", default_key_sequence="Ctrl+S"
        )
    assert definition.key_sequence == ""

    captured = capsys.readouterr()
    assert "ShortcutError" in captured.out


def test_full_lifecycle(widget, qtbot):
    """Test complete declare -> bind -> use -> unbind lifecycle."""
    widget.show()
    qtbot.wait(300)

    manager = ShortcutManager()
    callback = Mock()

    # Declare.
    definition = manager.declare_shortcut(
        context="file", name="save", default_key_sequence="Ctrl+S"
        )
    assert definition.is_bound is False

    # Bind.
    manager.bind_shortcut(
        context="file", name="save", callback=callback, parent=widget
        )
    assert definition.is_bound is True

    # Use.
    qtbot.keyPress(widget, Qt.Key_S, modifier=Qt.ControlModifier)
    callback.assert_called_once()

    # Unbind.
    manager.unbind_shortcut("file", "save")
    assert definition.is_bound is False

    # Use and assert callback was not called..
    qtbot.keyPress(widget, Qt.Key_S, modifier=Qt.ControlModifier)
    callback.assert_called_once()


def test_lazy_ui_pattern(qtbot):
    """Test declaring shortcuts before UI exists, then binding later."""
    manager = ShortcutManager()

    # Declare before UI exists
    manager.declare_shortcuts([
        {'context': 'file', 'name': 'save', 'default_key_sequence': 'Ctrl+S'},
        {'context': 'file', 'name': 'open', 'default_key_sequence': 'Ctrl+O'}
        ])

    assert len(list(manager.iter_definitions())) == 2
    assert len(list(manager.iter_shortcuts())) == 0

    # Create UI and bind.
    widget = QPushButton()
    qtbot.addWidget(widget)

    assert widget.text() == ''
    assert widget.toolTip() == ''

    title = "Save"
    text = "Save the file."
    alt_text = "Save with the file with {sc_str}."

    manager.bind_shortcut(
        context="file", name="save", callback=Mock(), parent=widget,
        synced_ui_data=[
            (widget.setToolTip,
             ToolTipSyncTranslator(title, text, alt_text)),
            (widget.setText,
             TitleSyncTranslator(title))
            ]
        )

    assert len(list(manager.iter_definitions())) == 2
    assert len(list(manager.iter_shortcuts())) == 1

    assert widget.text() == 'Save (Ctrl+S)'
    assert widget.toolTip() == (
        "<p style='white-space:pre'>"
        "<b>Save (Ctrl+S)</b></p>"
        "<p>Save with the file with Ctrl+S.</p>")


def test_print_shortcuts(populated_manager, capsys):
    captured = capsys.readouterr()
    assert captured.out == ''

    populated_manager.print_shortcuts()

    captured = capsys.readouterr()
    assert captured.out == (
        "\n"
        "------------------------\n"
        "ContextName  Key Sequence\n"
        "------------------------\n"
        "file  save  Ctrl+S\n"
        "file  open  Ctrl+O\n"
        "edit  copy  Ctrl+C\n"
        "_     quit  Ctrl+Q\n"
        "------------------------\n"
        )


if __name__ == "__main__":
    pytest.main(['-x', __file__, '-vv', '-rw'])
