# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © AppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of AppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

"""Qt utilities"""

from __future__ import annotations
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from qtpy.QtGui import QIcon

# ---- Standard imports
import sys
import platform

# ---- Third party imports
from qtpy.QtGui import QKeySequence
from qtpy.QtCore import QByteArray, Qt, QSize
from qtpy.QtWidgets import (
    QWidget, QSizePolicy, QToolButton, QApplication, QStyleFactory, QAction)

# ---- Local imports
from apputils.icons import get_icon, get_iconsize


def qbytearray_to_hexstate(qba):
    """Convert QByteArray object to a str hexstate."""
    return str(bytes(qba.toHex().data()).decode())


def hexstate_to_qbytearray(hexstate):
    """Convert a str hexstate to a QByteArray object."""
    return QByteArray().fromHex(str(hexstate).encode('utf-8'))


def create_qapplication(ft_ptsize: int = None, ft_family: str = None):
    """Create a QApplication instance if it doesn't already exist"""
    qapp = QApplication.instance()
    if qapp is None:
        qapp = QApplication(sys.argv)

        if platform.system() == 'Windows':
            qapp.setStyle(QStyleFactory.create('WindowsVista'))

    ft = qapp.font()
    if ft_ptsize is not None:
        ft.setPointSize(ft_ptsize)
    if ft_family is not None:
        ft.setFamily(ft_family)
    qapp.setFont(ft)

    return qapp


def create_toolbar_stretcher():
    """Create a stretcher to be used in a toolbar """
    stretcher = QWidget()
    stretcher.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    return stretcher


def create_toolbutton(parent, text: str = None, shortcut: str = None,
                      icon: str | QIcon = None, tip: str = None,
                      toggled: Callable = None, triggered: Callable = None,
                      autoraise=True, text_beside_icon: bool = False,
                      iconsize: int | QSize | str = None):
    """Create a QToolButton with the provided settings."""
    button = QToolButton(parent)
    if text is not None:
        button.setText(text)
    if icon is not None:
        icon = get_icon(icon) if isinstance(icon, str) else icon
        button.setIcon(icon)
    if any((text, tip, shortcut)):
        button.setToolTip(format_tooltip(text, tip, shortcut))
    if text_beside_icon:
        button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
    button.setAutoRaise(autoraise)
    if triggered is not None:
        button.clicked.connect(triggered)
    if toggled is not None:
        button.toggled.connect(toggled)
        button.setCheckable(True)
    if shortcut is not None:
        if isinstance(shortcut, (list, tuple)):
            for sc in shortcut:
                button.setShortcut(sc)
        else:
            button.setShortcut(shortcut)
    if iconsize is not None:
        if isinstance(iconsize, str):
            iconsize = get_iconsize(iconsize)
        elif isinstance(iconsize, int):
            iconsize = QSize(iconsize, iconsize)
        button.setIconSize(iconsize)
    return button


def create_action(parent, text: str = None, shortcut: str = None,
                  icon: str | QIcon = None, tip: str = None,
                  toggled: Callable = None, triggered: Callable = None,
                  data=None, menurole=None,
                  context=Qt.WindowShortcut, name: str = None):
    """Create and return a QAction with the provided settings."""
    action = QAction(text, parent)
    action.setShortcutContext(context)
    if triggered is not None:
        action.triggered.connect(triggered)
    if toggled is not None:
        action.toggled.connect(toggled)
        action.setCheckable(True)
    if icon is not None:
        icon = get_icon(icon) if isinstance(icon, str) else icon
        action.setIcon(icon)
    if any((text, tip, shortcut)):
        action.setToolTip(format_tooltip(text, tip, shortcut))
    if text:
        action.setStatusTip(format_statustip(text, shortcut))
    if data is not None:
        action.setData(data)
    if menurole is not None:
        action.setMenuRole(menurole)
    if shortcut is not None:
        if isinstance(shortcut, (list, tuple)):
            action.setShortcuts(shortcut)
        else:
            action.setShortcut(shortcut)
    if name is not None:
        action.setObjectName(name)

    return action


def format_statustip(text: str, shortcuts: list[str] | str):
    """
    Format text and shortcut into a single str to be set
    as an action status tip. The status tip is displayed on all status
    bars provided by the action's top-level parent widget.
    """
    keystr = get_shortcuts_native_text(shortcuts)
    if text and keystr:
        stip = "{} ({})".format(text, keystr)
    elif text:
        stip = "{}".format(text)
    else:
        stip = ""
    return stip


def format_tooltip(text: str, tip: str, shortcuts: list[str] | str):
    """
    Format text, tip and shortcut into a single str to be set
    as a widget's tooltip.
    """
    keystr = get_shortcuts_native_text(shortcuts)
    # We need to replace the unicode characters < and > by their HTML
    # code to avoid problem with the HTML formatting of the tooltip.
    keystr = keystr.replace('<', '&#60;').replace('>', '&#62;')
    ttip = ""
    if text or keystr:
        ttip += "<p style='white-space:pre'>"
        if text:
            ttip += "{}".format(text) + (" " if keystr else "")
        if keystr:
            ttip += "({})".format(keystr)
        ttip += "</p>"
    if tip:
        ttip += "<p>{}</p>".format(tip or '')
    return ttip


def get_shortcuts_native_text(shortcuts: list[str] | str):
    """
    Return the native text of a shortcut or a list of shortcuts.
    """
    if not isinstance(shortcuts, (list, tuple)):
        shortcuts = [shortcuts, ]

    return ', '.join([QKeySequence(sc).toString(QKeySequence.NativeText)
                      for sc in shortcuts])
