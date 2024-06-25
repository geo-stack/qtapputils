# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

# ---- Third party imports
from qtpy.QtCore import Signal, QObject, QLocale, Qt
from qtpy.QtGui import QValidator
from qtpy.QtWidgets import QDoubleSpinBox, QWidget

LOCALE = QLocale()


class DoubleSpinBox(QDoubleSpinBox):
    """
    A standard qt double spinbox that implements a workaround for
    the bug described at https://bugreports.qt.io/browse/QTBUG-77939.
    """

    def __init__(self, parent: QWidget = None,
                 consume_enter_events: bool = True):
        super().__init__(parent)
        # Whether to consume key press and key release events.
        # See jnsebgosselin/qtapputils#18
        self.consume_enter_events = consume_enter_events

    def keyReleaseEvent(self, event):
        """
        Override qt base method to consume key release events so that they are
        not propagated to the parent.
        """
        super().keyReleaseEvent(event)
        if (event.key() in (Qt.Key_Enter, Qt.Key_Return) and
                self.consume_enter_events):
            event.accept()

    def keyPressEvent(self, event):
        """
        Override qt base method to consume key press events so that they are
        not propagated to the parent.
        """
        super().keyPressEvent(event)
        if (event.key() in (Qt.Key_Enter, Qt.Key_Return) and
                self.consume_enter_events):
            event.accept()

    def textFromValue(self, value: float):
        """
        Override qt base method to work around the bug described at
        https://bugreports.qt.io/browse/QTBUG-77939 when a ',' is
        used as decimal separator.
        """
        from qtpy.QtCore import QLocale
        LOCALE = QLocale()
        if self.isGroupSeparatorShown():
            return LOCALE.toString(value, 'f', self.decimals())
        else:
            tostr = LOCALE.toString(value, 'f', self.decimals())
            index = self.decimals()
            if index == 0:
                return tostr.replace(LOCALE.groupSeparator(), '')
            else:
                return (
                    tostr[:-index-1].replace(LOCALE.groupSeparator(), '') +
                    tostr[-1-index:]
                    )


class RangeSpinBox(DoubleSpinBox):
    """
    A spinbox that allow to enter values that are lower or higher than the
    minimum and maximum value of the spinbox.

    When editing is finished, the value is corrected to the maximum if the
    value entered was above the maximum and to the minimum if it was below
    the minimum.
    """

    def __init__(self, parent: QWidget = None, maximum: float = None,
                 minimum: float = None, singlestep: float = None,
                 decimals: int = None, value: float = None):
        super().__init__(parent)
        self.setKeyboardTracking(False)
        if minimum is not None:
            self.setMinimum(minimum)
        if maximum is not None:
            self.setMaximum(maximum)
        if singlestep is not None:
            self.setSingleStep(singlestep)
        if decimals is not None:
            self.setDecimals(decimals)
        if value is not None:
            self.setValue(value)

    def sizeHint(self):
        """
        Override Qt method to add a buffer to the hint width of the spinbox,
        so that there is enough space to hold the maximum value in the spinbox
        when editing.
        """
        qsize = super().sizeHint()
        qsize.setWidth(qsize.width() + 8)
        return qsize

    def fixup(self, value):
        """Override Qt method."""
        if value in ('-', '', '.', ','):
            return super().fixup(value)

        num, success = LOCALE.toDouble(value)
        if float(num) > self.maximum():
            return self.textFromValue(self.maximum())
        else:
            return self.textFromValue(self.minimum())

    def validate(self, value, pos):
        """Override Qt method."""
        if value in ('-', '', '.', ','):
            return QValidator.Intermediate, value, pos

        num, success = LOCALE.toDouble(value)
        if success is False:
            return QValidator.Invalid, value, pos

        if float(num) > self.maximum() or float(num) < self.minimum():
            return QValidator.Intermediate, value, pos
        else:
            return QValidator.Acceptable, value, pos


class RangeWidget(QObject):
    """
    A Qt object that link two double spinboxes that can be used to define
    the start and end value of a range.

    The RangeWidget does not come with a layout and both the spinbox_start
    and spinbox_end must be added to a layout independently.
    """
    sig_range_changed = Signal(float, float)

    def __init__(self, parent: QWidget = None, maximum: float = 99.99,
                 minimum: float = 0, singlestep: float = 0.01,
                 decimals: int = 2, null_range_ok: bool = True):
        super().__init__()
        self.decimals = decimals
        self.null_range_ok = null_range_ok

        self.spinbox_start = RangeSpinBox(
            minimum=minimum, singlestep=singlestep, decimals=decimals,
            value=minimum)
        self.spinbox_start.valueChanged.connect(
            lambda: self._handle_value_changed())
        self.spinbox_start.editingFinished.connect(
            lambda: self._handle_value_changed())

        self.spinbox_end = RangeSpinBox(
            maximum=maximum, singlestep=singlestep, decimals=decimals,
            value=maximum)
        self.spinbox_end.valueChanged.connect(
            lambda: self._handle_value_changed())
        self.spinbox_end.editingFinished.connect(
            lambda: self._handle_value_changed())

        self._update_spinbox_range()

    def start(self):
        """Return the start value of the range."""
        return self.spinbox_start.value()

    def end(self):
        """Return the end value of the range."""
        return self.spinbox_end.value()

    def set_range(self, start: float, end: float):
        """Set the start and end value of the range."""
        old_start = self.start()
        old_end = self.end()

        self._block_spinboxes_signals(True)
        self.spinbox_start.setValue(start)
        self.spinbox_end.setValue(end)
        self._block_spinboxes_signals(False)

        if old_start != self.start() or old_end != self.end():
            self._handle_value_changed()

    def set_minimum(self, minimum: float):
        """Set the minimum allowed value of the start of the range."""
        old_start = self.start()

        self._block_spinboxes_signals(True)
        self.spinbox_start.setMinimum(minimum)
        self._block_spinboxes_signals(False)

        if old_start != self.start():
            self._handle_value_changed()

    def set_maximum(self, maximum: float):
        """Set the maximum allowed value of the end of the range."""
        old_end = self.end()

        self._block_spinboxes_signals(True)
        self.spinbox_end.setMaximum(maximum)
        self._block_spinboxes_signals(False)

        if old_end != self.end():
            self._handle_value_changed()

    # ---- Private methods and handlers
    def _block_spinboxes_signals(self, block: bool):
        """Block signals from the spinboxes."""
        self.spinbox_start.blockSignals(block)
        self.spinbox_end.blockSignals(block)

    def _update_spinbox_range(self):
        """
        Make sure lowcut and highcut spinbox ranges are
        mutually exclusive
        """
        self._block_spinboxes_signals(True)
        step = 0 if self.null_range_ok else 10**-self.decimals
        self.spinbox_start.setMaximum(self.spinbox_end.value() - step)
        self.spinbox_end.setMinimum(self.spinbox_start.value() + step)
        self._block_spinboxes_signals(False)

    def _handle_value_changed(self, silent: bool = False):
        """
        Handle when the value of the lowcut or highcut spinbox changed.
        """
        self._update_spinbox_range()
        self.sig_range_changed.emit(self.start(), self.end())
