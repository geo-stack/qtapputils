# -*- coding: utf-8 -*-
# =============================================================================
# Copyright (C) Les Solutions Géostack, Inc. - All Rights Reserved
#
# This file is part of Seismate.
# Unauthorized copying, distribution, or modification of this file,
# via any medium, is strictly prohibited without explicit permission
# from Les Solutions Géostack, Inc. Proprietary and confidential.
#
# For inquiries, contact: info@geostack.ca
# Repository: https://github.com/geo-stack/seismate
# =============================================================================

"""
Centralized Shortcut Manager for PyQt5 Applications
"""
import configparser as cp
from typing import Dict, Callable, Optional, List, Union, Tuple, Protocol, Any
from enum import Enum
from PyQt5.QtWidgets import QWidget, QShortcut, QAction
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
from appconfigs.user import UserConfig
from qtapputils.qthelpers import format_tooltip, get_shortcuts_native_text


# =============================================================================
# UI Sync Translators
# =============================================================================
class UISyncTranslator(Protocol):
    def __call__(self, shortcut: List[str] | str) -> tuple:
        ...


class ActionMenuSyncTranslator:
    def __init__(self, text):
        self.text = text

    def __call__(self, shortcuts):
        keystr = get_shortcuts_native_text(shortcuts)
        if keystr:
            return f"{self.text}\t{keystr}",
        else:
            return self.text,


class TitleSyncTranslator:
    def __init__(self, text):
        self.text = text

    def __call__(self, shortcuts):
        keystr = get_shortcuts_native_text(shortcuts)
        if keystr:
            return f"{self.text} ({keystr})",
        else:
            return self.text,


class ToolTipSyncTranslator:
    def __init__(self, title='', text='', alt_text=None):
        self.title = title
        self.text = text
        self.alt_text = text if alt_text is None else alt_text

    def __call__(self, shortcuts):
        if shortcuts:
            return format_tooltip(self.title, self.alt_text, shortcuts),
        else:
            return format_tooltip(self.title, self.text, shortcuts),


# =============================================================================
# Shortcuts Manager
# =============================================================================

UISyncSetter = Callable[..., Any]
UISyncTarget = Tuple[UISyncSetter, UISyncTranslator]


class ShortcutItem:
    """Configuration class for shortcut definitions"""

    def __init__(self,
                 context: str,
                 name: str,
                 key_sequence: QKeySequence | str,
                 callback: Callable,
                 parent: QWidget,
                 enabled: bool = True,
                 description: str = '',
                 synced_ui_data: Optional[List[UISyncTarget]] = None
                 ):
        self.context = context
        self.name = name
        self.qkey_sequence = QKeySequence(key_sequence)
        self.callback = callback
        self.parent = parent
        self.description = description

        if synced_ui_data is None:
            synced_ui_data = []
        self.synced_ui_data = synced_ui_data

        self.shortcut = None
        if enabled is True:
            self.activate()

    @property
    def key_sequence(self, native: bool = False):
        if native:
            return self.qkey_sequence.toString(QKeySequence.NativeText)
        else:
            return self.qkey_sequence.toString()

    def activate(self):
        """Internal method to create a QShortcut"""
        if self.shortcut is None:
            self.shortcut = QShortcut(self.qkey_sequence, self.parent)
            self.shortcut.activated.connect(self.callback)
            self.shortcut.setAutoRepeat(False)
        self.set_enabled(True)
        self._update_ui()

    def deactivate(self):
        """Deactivate a specific shortcut"""
        if self.shortcut is not None:
            self.shortcut.setEnabled(False)
            self.shortcut.deleteLater()
            del self.shortcut
            self.shortcut = None
        self.enabled = False

    def set_keyseq(self, qkey_sequence: QKeySequence):
        if self.shortcut is not None:
            self.qkey_sequence = qkey_sequence
            self.shortcut.setKey(self.qkey_sequence)
            self._update_ui()

    def set_enabled(self, enabled: bool = True):
        """Enable or disable a shortcut"""
        self.enabled = enabled
        self.shortcut.setEnabled(enabled)

    def _update_ui(self):
        for setter, translator in self.synced_ui_data:
            setter(*translator(self.qkey_sequence.toString()))


class ShortcutManager:
    """
    Centralized manager for application shortcuts.
    """

    def __init__(self, userconfig: UserConfig = None):
        self._userconfig = userconfig
        self._shortcuts: Dict[str, ShortcutItem] = {}

    def register_shortcut(
            self,
            context: str,
            name: str,
            callback: Callable,
            parent: QWidget,
            description: str = "",
            default_key_sequence: str = None,
            synced_ui_data: Optional[List[UISyncTarget]] = None
            ):
        """
        Register a shortcut configuration.

        Args:
            name: Identifier for the shortcut
            key_sequence: Key combination (e.g., "Ctrl+S", "Alt+F4")
            callback: Function to call when shortcut is triggered
            context: Context where shortcut is active
            description: Human-readable description
        """
        context_name = f"{context}/{name}"
        if context_name in self._shortcuts:
            raise ValueError(
                f"There is already a shortcut '{name}' registered for "
                f"context '{context}'."
                )

        if self._userconfig is not None:
            if default_key_sequence is not None:
                self._userconfig.set_default(
                    'shortcuts', context_name, default_key_sequence
                    )

            try:
                # We don't pass the default value to 'get', because if
                # option does not exists in 'shortcuts' section, the default
                # is saved in the current user configs and we do not want
                # that.
                key_sequence = self._userconfig.get('shortcuts', context_name)
            except cp.NoOptionError:
                key_sequence = default_key_sequence or ''

        else:
            key_sequence = default_key_sequence or ''

        if self.check_conflicts(context, name, key_sequence):
            key_sequence = ''

        qkey_sequence = QKeySequence(key_sequence)
        if qkey_sequence.isEmpty() and key_sequence not in (None, ''):
            raise ValueError(
                f"Key sequence '{key_sequence}' is not valid."
                )

        self._shortcuts[context_name] = ShortcutItem(
            context=context,
            name=name,
            key_sequence=qkey_sequence,
            callback=callback,
            parent=parent,
            synced_ui_data=synced_ui_data
            )

    def unregister_shortcut(self, context: str, name: str):
        """Unregister a shortcut"""
        self._shortcuts[f"{context}/{name}"].deactivate()
        del self._shortcuts[f"{context}/{name}"]

    def activate_shortcut(self, context: str, name: str):
        """Activate a specific shortcut on a widget"""
        self._shortcuts[f"{context}/{name}"].activate()

    def deactivate_shortcut(self, context: str, name: str):
        """Deactivate a specific shortcut"""
        self._shortcuts[f"{context}/{name}"].deactivate()

    def enable_shortcut(
            self, context: str, name: str, enabled: bool = True):
        """Enable or disable a shortcut"""
        self._shortcuts[f"{context}/{name}"].set_enabled(enabled)

    def update_key_sequence(
            self, context: str, name: str, new_key_sequence: str,
            sync_userconfig: bool = False):
        """Update the key sequence for a shortcut"""
        if self.check_conflicts(context, name, new_key_sequence):
            return

        context_name = f"{context}/{name}"
        new_qkey_sequence = QKeySequence(new_key_sequence)
        self._shortcuts[context_name].set_keyseq(new_qkey_sequence)
        if self._userconfig is not None and sync_userconfig:
            self._userconfig.set(
                'shortcuts',
                context_name,
                new_qkey_sequence.toString()
                )

    def iter_shortcuts(self, context: str = None):
        """Iterate over keyboard shortcuts."""
        for sc in self._shortcuts.values():
            if context is None or context == sc.context:
                yield sc

    def check_conflicts(self, context: str, name: str, key_sequence: str):
        conflicts = self.find_conflicts(context, name, key_sequence)
        if len(conflicts):
            print(f"Cannot set shortcut '{name}' in context '{context}' "
                  f"to '{key_sequence}' because of the following "
                  f"conflict(s):")
            for sc in conflicts:
                print(f"  - shortcut '{sc.name}' in context '{sc.context}'")
            return True
        return False

    def find_conflicts(self, context: str, name: str, key_sequence: str):
        """Check shortcuts for conflicts."""
        conflicts = []
        qkey_sequence = QKeySequence(key_sequence)
        if qkey_sequence.isEmpty():
            return conflicts

        no_match = QKeySequence.SequenceMatch.NoMatch
        for sc in self.iter_shortcuts():
            if sc.qkey_sequence.isEmpty():
                continue
            if (sc.context, sc.name) == (context, name):
                continue
            if sc.context in [context, '_'] or context == '_':
                if sc.qkey_sequence.matches(qkey_sequence) != no_match:
                    conflicts.append(sc)
                elif qkey_sequence.matches(sc.qkey_sequence) != no_match:
                    conflicts.append(sc)
        return conflicts
