# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/qtapputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

# ---- Third party imports
from qtpy.QtCore import QSize, Qt
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QGridLayout, QLabel, QWidget, QTextBrowser
import qtawesome as qta


# ---- Local imports
from qtapputils.qthelpers import create_waitspinner
from qtapputils.colors import RED, GREEN, BLUE


class ProcessStatusBar(QWidget):
    """
    A status bar that shows the progression status and results of a process.

    This class was taken from the Sardes project.
    See sardes/widgets/statusbar.py at https://github.com/geo-stack/sardes
    """
    HIDDEN = 0
    IN_PROGRESS = 1
    PROCESS_SUCCEEDED = 2
    PROCESS_FAILED = 3
    NEED_UPDATE = 4

    def __init__(self, parent=None, iconsize=24, ndots=11,
                 orientation=Qt.Horizontal, spacing=None,
                 contents_margin: list = None,
                 hsize_policy='minimum', vsize_policy='minimum',
                 text_valign='center', icon_valign='center'):
        """
        A process status bar including an icon and a label.

        Parameters
        ----------
        parent : QWidget, optional
            The parent of the progress status bar. The default is None.
        iconsize : int, optional
            The size of the icon. The default is 24.
        ndots : int, optional
            Number of dots to use for the spinner icon . The default is 11.
        orientation : int, optional
            Orientation of the progress status bar. The default is
            Qt.Horizontal.
        spacing : in, optional
            Spacing between the icon and the label. Default to 0 if
            orientation is horizontal and to 5 if vertical.
        contents_margin : list[int], optional
            A list of four integers corresponding to the left, top, right, and
            bottom contents margin. The default is 0 on all sides.
        hsize_policy : str, optional
            An attribute describing horizontal resizing policy. Valid
            values are 'minimum' or 'expanding'.
        vsize_policy : str, optional
            An attribute describing vertical resizing policy. Valid
            values are 'minimum', 'expanding', or 'minimum_expanding'.
        text_valign : str, optional
            The vertical alignment of the text. De default is 'center'.
            Valid values are 'top', 'bottom', or 'center'.
        icon_valign : str, optional
            The vertical alignment of the icon. De default is 'center'.
            Valid values are 'top', 'bottom', or 'center'.
        """
        super().__init__(parent)
        self._status = self.HIDDEN
        self._iconsize = iconsize

        VALIGN_DICT = {
            'center': Qt.AlignVCenter,
            'top': Qt.AlignTop,
            'bottom': Qt.AlignBottom
            }

        class LabelBrowser(QTextBrowser):

            def minimumSizeHint(self):
                return QLabel().minimumSizeHint()

            def sizeHint(self):
                return QLabel().sizeHint()

        text_valign = VALIGN_DICT[text_valign]
        self._label = LabelBrowser()
        if orientation == Qt.Horizontal:
            self._label.setAlignment(Qt.AlignLeft | text_valign)
        else:
            self._label.setAlignment(Qt.AlignCenter | text_valign)
        self._label.setLineWrapMode(LabelBrowser.WidgetWidth)
        self._label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextBrowserInteraction)
        self._label.setOpenExternalLinks(True)
        self._label.setFocusPolicy(Qt.NoFocus)
        self._label.setFrameStyle(0)
        self._label.setStyleSheet("background-color:transparent;")

        self._spinner = create_waitspinner(iconsize, ndots, self)

        # Setup status icons.
        self._icons = {
            'failed': QLabel(),
            'success': QLabel(),
            'update': QLabel()
            }
        self.hide_icons()

        self.set_icon(
            'failed', qta.icon('mdi.alert-circle-outline', color=RED))
        self.set_icon(
            'success', qta.icon('mdi.update', color=GREEN))
        self.set_icon(
            'update', qta.icon('mdi.check-circle-outline', color=BLUE))

        # Setup layout.
        layout = QGridLayout(self)
        if contents_margin is None:
            contents_margin = [0, 0, 0, 0]
        layout.setContentsMargins(*contents_margin)

        icon_valign = VALIGN_DICT[icon_valign]
        if orientation == Qt.Horizontal:
            alignment = Qt.AlignLeft | icon_valign
        else:
            alignment = Qt.AlignCenter | icon_valign
        layout.addWidget(self._spinner, 1, 1, alignment)
        for widget in self._icons.values():
            layout.addWidget(widget, 1, 1, alignment)
        if orientation == Qt.Horizontal:
            layout.setColumnMinimumWidth(2, 5)
            layout.addWidget(self._label, 1, 3)
            if vsize_policy == 'minimum':
                layout.setRowStretch(0, 100)
                layout.setRowStretch(3, 100)
            elif vsize_policy == 'expanding':
                layout.setRowStretch(1, 100)
            if hsize_policy == 'minimum':
                layout.setColumnStretch(4, 100)
            elif hsize_policy == 'expanding':
                layout.setColumnStretch(3, 100)
            layout.setSpacing(spacing or 0)
        else:
            layout.addWidget(self._label, 2, 1)
            if vsize_policy == 'minimum':
                layout.setRowStretch(0, 100)
                layout.setRowStretch(4, 100)
            elif vsize_policy == 'expanding':
                layout.setRowStretch(2, 100)
            elif vsize_policy == 'minimum_expanding':
                layout.setRowStretch(0, 50)
                layout.setRowStretch(2, 100)
                layout.setRowStretch(4, 50)
            if hsize_policy == 'minimum':
                layout.setColumnStretch(0, 100)
                layout.setColumnStretch(2, 100)
            elif hsize_policy == 'expanding':
                layout.setColumnStretch(1, 100)
            layout.setSpacing(spacing or 5)

    def show_icon(self, icon_name):
        """Show icon named 'icon_name' and hide all other icons."""
        self._spinner.hide()
        self._spinner.stop()
        for name, icon in self._icons.items():
            if name == icon_name:
                icon.show()
            else:
                icon.hide()

    def hide_icons(self):
        """Hide all icons."""
        for icon in self._icons.values():
            icon.hide()

    def set_icon(self, name: str, icon: QIcon):
        """Set the icon named 'name'."""
        self._icons[name].setPixmap(
            icon.pixmap(QSize(self._iconsize, self._iconsize))
            )

    @property
    def status(self):
        return self._status

    def set_label(self, text):
        """Set the text that is displayed next to the spinner."""
        self._label.setText(text)

    def show_update_icon(self, message=None):
        """Stop and hide the spinner and show an update icon instead."""
        self._status = self.NEED_UPDATE
        self.show_icon('update')
        if message is not None:
            self.set_label(message)

    def show_fail_icon(self, message=None):
        """Stop and hide the spinner and show a failed icon instead."""
        self._status = self.PROCESS_FAILED
        self.show_icon('failed')
        if message is not None:
            self.set_label(message)

    def show_sucess_icon(self, message=None):
        """Stop and hide the spinner and show a success icon instead."""
        self._status = self.PROCESS_SUCCEEDED
        self.show_icon('success')
        if message is not None:
            self.set_label(message)

    def show(self, message=None):
        """Extend Qt method to start the waiting spinner."""
        self._status = self.IN_PROGRESS
        self._spinner.show()
        self.hide_icons()
        super().show()
        self._spinner.start()
        if message is not None:
            self.set_label(message)

    def hide(self):
        """Extend Qt hide to stop waiting spinner."""
        self._status = self.HIDDEN
        super().hide()
        self._spinner.stop()
