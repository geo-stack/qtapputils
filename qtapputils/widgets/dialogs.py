# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/qtapputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------
from __future__ import annotations
from typing import Callable


# ---- Third party imports
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QApplication, QDialog, QDialogButtonBox, QPushButton,
    QWidget, QStackedWidget, QVBoxLayout, QGridLayout)
from qtapputils.icons import get_standard_icon, get_standard_iconsize
from qtapputils.qthelpers import get_default_contents_margins

# ---- Local imports
from qtapputils.widgets.statusbar import ProcessStatusBar


class UserMessageDialogBase(QDialog):
    """
    Basic functionalities to implement a dialog window that provide
    the capability to show messages to the user.

    This class was taken from the Sardes project.
    See sardes/widgets/dialogs.py at https://github.com/geo-stack/sardes
    """

    def __init__(self, parent=None, minimum_height: int = 100,
                 minimum_width: int = None):
        super().__init__(parent)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.__setup__(minimum_height, minimum_width)

    def __setup__(self, minimum_height, minimum_width):
        """Setup the dialog with the provided settings."""

        self._buttons = []

        # Setup the main widget.
        self.central_widget = QWidget()
        self.central_layout = QGridLayout(self.central_widget)

        # Setup the main layout.
        main_layout = QVBoxLayout(self)
        main_layout.setSizeConstraint(main_layout.SetDefaultConstraint)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Setup the stacked widget.
        self._dialogs = []

        self.stackwidget = QStackedWidget()
        self.stackwidget.addWidget(self.central_widget)
        self.stackwidget.setMinimumHeight(minimum_height)
        if minimum_width is not None:
            self.stackwidget.setMinimumWidth(minimum_width)

        main_layout.addWidget(self.stackwidget)

        # Setup the button box.
        self.button_box = QDialogButtonBox()
        self.button_box.layout().addStretch(1)

        main_layout.addWidget(self.button_box)

        # Note that we need to set the margins of the button box after
        # adding it to the main layout or else, it has no effect.
        self.button_box.layout().setContentsMargins(
            *get_default_contents_margins())

    # ---- Helpers Methods
    def create_button(self, text: str, enabled: bool = True,
                      triggered: Callable = None, default: bool = False
                      ) -> QPushButton:
        """Create a pushbutton to add to the button box."""
        button = QPushButton(text)
        button.setDefault(default)
        button.setAutoDefault(False)
        if triggered is not None:
            button.clicked.connect(triggered)
        button.setEnabled(enabled)
        return button

    def add_button(self, button):
        """Add a new pushbutton to the button box."""
        self._buttons.append(button)
        self.button_box.layout().addWidget(button)

    def create_msg_dialog(self, std_icon_name: str,
                          buttons: list[QPushButton]
                          ) -> ProcessStatusBar:
        """Create a new message dialog."""
        dialog = ProcessStatusBar(
            spacing=10,
            icon_valign='top',
            vsize_policy='expanding',
            hsize_policy='expanding',
            text_valign='top',
            iconsize=get_standard_iconsize('messagebox'),
            contents_margin=get_default_contents_margins())
        dialog.set_icon('failed', get_standard_icon(std_icon_name))
        dialog.setAutoFillBackground(True)
        dialog._buttons = buttons

        palette = QApplication.instance().palette()
        palette.setColor(dialog.backgroundRole(), palette.light().color())
        dialog.setPalette(palette)

        # Hide the buttons of the dialogs.
        for btn in buttons:
            btn.setVisible(False)

        return dialog

    def add_msg_dialog(self, dialog: ProcessStatusBar):
        """Add a new message dialog to the stack widget."""
        self._dialogs.append(dialog)
        self.stackwidget.addWidget(dialog)
        for button in dialog._buttons:
            self.add_button(button)

    # ---- Public Interface
    def show_message_dialog(
            self, dialog: ProcessStatusBar, message: str, beep: bool = True):
        """Show to the user the specified dialog with the provided message."""
        self.show()
        for btn in self._buttons:
            btn.setVisible(btn in dialog._buttons)
        dialog.show_fail_icon(message)
        self.stackwidget.setCurrentWidget(dialog)
        if beep is True:
            QApplication.beep()

    def close_message_dialogs(self):
        """Close all message dialogs and show the main interface."""
        for btn in self._buttons:
            btn.setVisible(True)
        for dialog in self._dialogs:
            for btn in dialog._buttons:
                btn.setVisible(False)
        self.stackwidget.setCurrentWidget(self.central_widget)

    def show(self):
        """
        Override Qt method to raise window to the top when already visible.
        """
        if self.windowState() == Qt.WindowMinimized:
            self.setWindowState(Qt.WindowNoState)
        super().show()
        self.activateWindow()
        self.raise_()
