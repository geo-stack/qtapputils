# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

"""
Centralized Shortcut Manager for PyQt5 Applications
"""
from typing import (
    TYPE_CHECKING, Dict, Callable, Optional, List, Tuple, Protocol, Any)
if TYPE_CHECKING:
    from appconfigs.user import UserConfig

# ---- Standard import
from dataclasses import dataclass
import configparser as cp

# ---- Third party import
from qtpy.QtWidgets import QWidget, QShortcut
from qtpy.QtGui import QKeySequence

# ---- Local import
from qtapputils.qthelpers import format_tooltip, get_shortcuts_native_text
from qtapputils.utils.console import print_warning


# =============================================================================
# UI Sync Translators
# =============================================================================
class UISyncTranslator(Protocol):
    def __call__(self, shortcut: list[str] | str) -> tuple:
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
# Shortcut Definition (Declarative - no QShortcut yet)
# =============================================================================

UISyncSetter = Callable[..., Any]
UISyncTarget = Tuple[UISyncSetter, UISyncTranslator]


@dataclass
class ShortcutDefinition:
    """
    Declarative shortcut definition - describes a shortcut without
    creating any Qt objects.

    This allows complete registration at startup.
    """
    context: str
    name: str
    key_sequence: str
    description: str

    @property
    def context_name(self) -> str:
        return f"{self.context}/{self.name}"

    @property
    def qkey_sequence(self) -> QKeySequence:
        return QKeySequence(self.key_sequence)

    @property
    def is_bound(self) -> bool:
        """Check if this definition has been bound to actual UI."""
        return hasattr(self, '_shortcut') and self._shortcut is not None

    @property
    def shortcut(self) -> Optional['ShortcutItem']:
        return getattr(self, '_shortcut', None)


class ShortcutItem:
    """
    A shortcut that has been bound to actual UI elements.
    Created when lazy UI is finally instantiated.
    """

    def __init__(self, definition: ShortcutDefinition, callback: Callable,
                 parent: QWidget, synced_ui_data: List[UISyncTarget] = None):

        self.definition = definition
        self.callback = callback
        self.parent = parent
        self.synced_ui_data = synced_ui_data or []

        self.shortcut = None
        self.enabled = False

        self._update_ui()

    @property
    def key_sequence(self, native: bool = False):
        if self.shortcut is None:
            return ''

        if native:
            return self.definition.qkey_sequence.toString(
                QKeySequence.NativeText)
        else:
            return self.definition.qkey_sequence.toString()

    def activate(self):
        """Create and activate the QShortcut."""
        if self.shortcut is None:
            self.shortcut = QShortcut(
                self.definition.qkey_sequence, self.parent)
            self.shortcut.activated.connect(self.callback)
            self.shortcut.setAutoRepeat(False)
        self.set_enabled(True)
        self._update_ui()

    def deactivate(self):
        """Deactivate and clean up the QShortcut."""
        if self.shortcut is not None:
            self.shortcut.setEnabled(False)
            self.shortcut.deleteLater()
            self.shortcut = None
        self.enabled = False
        self._update_ui()

    def set_keyseq(self, key_sequence: str):
        """Update the key sequence."""
        self.definition.key_sequence = key_sequence
        if self.shortcut is not None:
            self.shortcut.setKey(self.definition.qkey_sequence)
            self._update_ui()

    def set_enabled(self, enabled: bool = True):
        """Enable or disable the shortcut."""
        self.enabled = enabled
        if self.shortcut is not None:
            self.shortcut.setEnabled(enabled)

    def _update_ui(self):
        """Update synced UI elements with current key sequence."""
        keystr = self.key_sequence
        for setter, translator in self.synced_ui_data:
            setter(*translator(keystr))


# =============================================================================
# Shortcuts Manager
# =============================================================================
class ShortcutManager:
    """
    Centralized manager for application shortcuts.

    Supports two-phase shortcut management:
    1. Declaration phase: Define all shortcuts upfront (even before UI exists)
    2. Binding phase: Bind shortcuts to actual UI when it's created
    """

    def __init__(self, userconfig: 'UserConfig' = None,
                 blocklist: list[str] = None):
        self._userconfig = userconfig

        # The list of blocklisted key sequence.
        self._blocklist: list[str] = [] if blocklist is None else blocklist

        # All declared shortcuts (complete list available immediately)
        self._definitions: Dict[str, ShortcutDefinition] = {}

        # Shortcuts that have been bound to UI
        self._shortcuts: Dict[str, ShortcutItem] = {}

    # =========================================================================
    # ---- Declaration methods
    # =========================================================================
    def declare_shortcut(
            self,
            context: str,
            name: str,
            default_key_sequence: str = '',
            description: str = ''
            ) -> ShortcutDefinition:
        """
        Declare a shortcut definition.

        This allow populating the complete shortcut list, even before their
        UI exists..
        """
        context_name = f"{context}/{name}"
        if context_name in self._definitions:
            raise ValueError(
                f"Shortcut '{name}' already declared for context '{context}'."
            )

        key_sequence = default_key_sequence
        if self._userconfig is not None:
            try:
                # We don't pass the default value to 'get', because if
                # option does not exists in 'shortcuts' section, the default
                # is saved in the current user configs and we do not want
                # that.
                key_sequence = self._userconfig.get('shortcuts', context_name)
            except (cp.NoOptionError, cp.NoSectionError):
                pass

        if self.check_conflicts(context, name, key_sequence):
            key_sequence = ''

        qkey_sequence = QKeySequence(key_sequence)
        if qkey_sequence.isEmpty() and key_sequence not in (None, ''):
            raise ValueError(
                f"Key sequence '{key_sequence}' is not valid."
                )

        definition = ShortcutDefinition(
            context=context,
            name=name,
            key_sequence=key_sequence,
            description=description
            )

        self._definitions[context_name] = definition

        return definition

    def declare_shortcuts(self, shortcuts: List[dict]):
        """Bulk declare shortcuts from a list of definitions."""
        for sc in shortcuts:
            self.declare_shortcut(**sc)

    # =========================================================================
    # ---- Binding methods
    # =========================================================================
    def bind_shortcut(
            self,
            context: str,
            name: str,
            callback: Callable,
            parent: QWidget,
            synced_ui_data: Optional[List[UISyncTarget]] = None,
            activate: bool = True
            ) -> ShortcutItem:
        """
        Bind a previously declared shortcut to actual UI elements.
        Call this when the lazy-loaded UI is finally created.
        """
        context_name = f"{context}/{name}"
        if context_name not in self._definitions:
            raise ValueError(
                f"Shortcut '{name}' in context '{context}' was not declared. "
                f"Call declare_shortcut() first."
                )
        if context_name in self._shortcuts:
            raise ValueError(
                f"Shortcut '{name}' in context '{context}' is already bound."
                )

        definition = self._definitions[context_name]
        shortcut = ShortcutItem(
            definition=definition,
            callback=callback,
            parent=parent,
            synced_ui_data=synced_ui_data or []
            )

        # Link back to definition
        definition._shortcut = shortcut
        self._shortcuts[context_name] = shortcut

        if activate:
            shortcut.activate()

        return shortcut

    def unbind_shortcut(self, context: str, name: str):
        """Unbind a shortcut."""
        context_name = f"{context}/{name}"
        if context_name in self._shortcuts:
            self._shortcuts[context_name].deactivate()
            self._definitions[context_name]._shortcut = None
            del self._shortcuts[context_name]

    # =========================================================================
    # Shortcut Control
    # =========================================================================
    def activate_shortcut(self, context: str, name: str):
        """Activate a bound shortcut."""
        context_name = f"{context}/{name}"
        if context_name in self._shortcuts:
            self._shortcuts[context_name].activate()

    def deactivate_shortcut(self, context: str, name: str):
        """Deactivate a bound shortcut."""
        context_name = f"{context}/{name}"
        if context_name in self._shortcuts:
            self._shortcuts[context_name].deactivate()

    def enable_shortcut(self, context: str, name: str, enabled: bool = True):
        """Enable or disable a bound shortcut."""
        context_name = f"{context}/{name}"
        if context_name in self._shortcuts:
            self._shortcuts[context_name].set_enabled(enabled)

    # =========================================================================
    # Iteration & Query
    # =========================================================================
    def iter_definitions(self, context: str = None):
        """
        Iterate over ALL shortcut definitions (complete list).
        Use this for the settings panel.
        """
        for definition in self._definitions.values():
            if context is None or context == definition.context:
                yield definition

    def iter_shortcuts(self, context: str = None):
        """Iterate over bound shortcuts only."""
        for sc in self._shortcuts.values():
            if context is None or context == sc.definition.context:
                yield sc

    # =========================================================================
    # Conflict Detection
    # =========================================================================
    def check_conflicts(
            self, context: str, name: str, key_sequence: str
            ) -> bool:
        """Check for conflicts and print warnings."""

        qkey_sequence = QKeySequence(key_sequence)

        if qkey_sequence.toString() == '' and key_sequence not in (None, ''):
            print_warning(
                "ShortcutError",
                f"Key sequence '{key_sequence}' is not valid."
                )
            return True

        if qkey_sequence.toString() in self._blocklist:
            print_warning(
                "ShortcutError",
                f"Cannot set shortcut '{name}' in context '{context}' "
                f"because the key sequence '{key_sequence}' is reserved or "
                f"not allowed. Please select a different shortcut."
                )
            return True

        conflicts = self.find_conflicts(context, name, key_sequence)
        if conflicts:
            print_warning(
                "ShortcutError",
                f"Cannot set shortcut '{name}' in context '{context}' "
                f"to '{key_sequence}' because of the following "
                f"conflict(s):"
                )
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
        for sc_def in self._definitions.values():
            if sc_def.qkey_sequence.isEmpty():
                continue
            if (sc_def.context, sc_def.name) == (context, name):
                continue
            if sc_def.context in [context, '_'] or context == '_':
                if sc_def.qkey_sequence.matches(qkey_sequence) != no_match:
                    conflicts.append(sc_def)
                elif qkey_sequence.matches(sc_def.qkey_sequence) != no_match:
                    conflicts.append(sc_def)

        return conflicts

    # ---- End User Interface
    def print_shortcuts(self):
        """
        Print all declared shortcuts to the console in a formatted table.
        """
        defs = list(self.iter_definitions())
        context_w = max(len(scd.context) for scd in defs) + 2
        name_w = max(len(scd.name) for scd in defs) + 2

        print()
        print('-' * (context_w + name_w + 12))
        print(f"{'Context':<{context_w}}{'Name':<{name_w}}{'Key Sequence'}")
        print('-' * (context_w + name_w + 12))
        for scd in defs:
            print(f"{scd.context:<{context_w}}{scd.name:<{name_w}}"
                  f"{scd.qkey_sequence.toString()}")
        print('-' * (context_w + name_w + 12))

    def set_shortcut(
            self,
            context: str,
            name: str,
            new_key_sequence: str,
            sync_userconfig: bool = False
            ):
        """
        Set a new key sequence for a declared or bound shortcut.

        If the shortcut exists and the new key sequence is valid (i.e., not
        blocked or conflicting), the shortcut is updated. If the shortcut is
        currently bound to a UI element, the change will take effect
        immediately for it. If `sync_userconfig` is True and a user config
        has been passed to the shortcut manager, the user's new shortcut
        setting is saved for future sessions.

        Parameters
        ----------
        context : str
            The shortcut context (e.g., "file", "edit").
        name : str
            The name identifier of the shortcut within its
            context (e.g., "save", "copy").
        new_key_sequence : str
            The new key sequence to assign (e.g., "Ctrl+S").
        sync_userconfig : bool, optional
            Whether to save the change in the persistent user
            configuration. The default is False.

        Returns
        -------
        bool
            True if the update succeeded, False otherwise.
        """
        context_name = f"{context}/{name}"

        if context_name not in self._definitions:
            print_warning(
                "ShortcutError",
                f"Cannot find shortcut '{name}' in context '{context}'."
                )
            return False

        if self.check_conflicts(context, name, new_key_sequence):
            return False

        definition = self._definitions[context_name]
        definition.key_sequence = new_key_sequence

        # Update bound shortcut if it exists
        if context_name in self._shortcuts:
            self._shortcuts[context_name].set_keyseq(new_key_sequence)

        # Save to user config
        if self._userconfig is not None and sync_userconfig:
            self._userconfig.set(
                'shortcuts',
                context_name,
                QKeySequence(new_key_sequence).toString()
                )

        return True
