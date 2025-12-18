# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/geo-stack/qtapputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------


# ---- Third party imports
from qtpy.QtCore import Signal
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QToolButton, QWidget


class MultiStateToolButton(QToolButton):
    """
    A QToolButton that cycles through a list of icons each time it is clicked.

    Parameters
    ----------
    icons : list of QIcon
        The list of icons to cycle through.
    parent : QWidget, optional
        The parent widget.
    index : int, optional
        The index of the starting icon (default is 0).

    Signals
    -------
    sig_index_changed : Signal(int)
        Signal emitted with the new index whenever the current state changes.
    """

    sig_index_changed = Signal(int)

    def __init__(
            self, icons: list[QIcon],
            parent: QWidget = None,
            index: int = 0
            ):
        super().__init__(parent)

        self.setAutoRaise(True)
        self.setCheckable(False)

        self._icons = icons
        self._current_index = index

        self.clicked.connect(self._handle_clicked)
        self._update_icon()

    def current_index(self):
        return self._current_index

    def set_current_index(self, index: int):
        if index >= len(self._icons):
            index = 0
        elif index < 0:
            index = len(self._icons) - 1

        if index == self._current_index:
            return

        self._current_index = index
        self._update_icon()
        self.sig_index_changed.emit(index)

    def _update_icon(self):
        self.setIcon(self._icons[self._current_index])

    def _handle_clicked(self):
        self.set_current_index(self._current_index + 1)
