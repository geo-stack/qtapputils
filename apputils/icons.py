# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © AppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of AppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

# ---- Third party imports
from qtpy.QtCore import QSize, Qt
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QStyle, QApplication, QToolButton
import qtawesome as qta

# ---- Local imports
from apputils.colors import CSS4_COLORS, DEFAULT_ICON_COLOR


LOCAL_ICONS = {}

QTA_ICONS = {
    'arrow_left': [
        ('mdi.arrow-left-thick',),
        {'scale_factor': 1.2}],
    'arrow_right': [
        ('mdi.arrow-right-thick',),
        {'scale_factor': 1.2}],
    'arrow_up': [
        ('mdi.arrow-up-thick',),
        {'scale_factor': 1.2}],
    'arrow_down': [
        ('mdi.arrow-down-thick',),
        {'scale_factor': 1.2}],
    'console': [
        ('mdi.console',),
        {'scale_factor': 1.3}],
    'home': [
        ('mdi.home',),
        {'scale_factor': 1.3}],
    'report_bug': [
        ('mdi.bug',),
        {'scale_factor': 1.4}],
    'save': [
        ('fa.save',),
        {'scale_factor': 1.3}],
    'search': [
        ('fa5s.search',)],
    }

ICON_SIZES = {'large': (32, 32),
              'normal': (24, 24),
              'small': (20, 20)}


def get_icon(name, color: str = None):
    """Return a QIcon from a specified icon name."""
    if name in QTA_ICONS:
        try:
            args, kwargs = QTA_ICONS[name]
        except ValueError:
            args = QTA_ICONS[name][0]
            kwargs = {}
        if len(args) > 1:
            return qta.icon(*args, **kwargs)
        if color is not None:
            if color in CSS4_COLORS:
                kwargs['color'] = CSS4_COLORS[color]
            else:
                kwargs['color'] = color
        elif color is None and 'color' not in kwargs:
            kwargs['color'] = DEFAULT_ICON_COLOR
        return qta.icon(*args, **kwargs)
    elif name in LOCAL_ICONS:
        return QIcon(LOCAL_ICONS[name])
    else:
        return QIcon()


def get_iconsize(size: str):
    return QSize(*ICON_SIZES[size])


def get_standard_icon(constant):
    """
    Return a QIcon of a standard pixmap.

    See the link below for a list of valid constants:
    https://srinikom.github.io/pyside-docs/PySide/QtGui/QStyle.html
    """
    constant = getattr(QStyle, constant)
    style = QApplication.instance().style()
    return style.standardIcon(constant)


def get_standard_iconsize(constant: 'str'):
    """
    Return the standard size of various component of the gui.

    https://srinikom.github.io/pyside-docs/PySide/QtGui/QStyle
    """
    style = QApplication.instance().style()
    if constant == 'messagebox':
        return style.pixelMetric(QStyle.PM_MessageBoxIconSize)
    elif constant == 'small':
        return style.pixelMetric(QStyle.PM_SmallIconSize)


class QToolButtonBase(QToolButton):
    """A basic tool button."""

    def __init__(self, icon, *args, **kargs):
        super(QToolButtonBase, self).__init__(*args, **kargs)
        icon = get_icon(icon) if isinstance(icon, str) else icon
        self.setIcon(icon)
        self.setAutoRaise(True)
        self.setFocusPolicy(Qt.NoFocus)

    def setToolTip(self, ttip):
        """
        Qt method override to ensure tooltips are enclosed in <p></p> so
        that they wraps correctly.
        """
        ttip = ttip if ttip.startswith('<p>') else '<p>' + ttip
        ttip = ttip if ttip.endswith('</p>') else ttip + '</p>'
        super().setToolTip(ttip)


class QToolButtonNormal(QToolButtonBase):
    def __init__(self, Qicon, *args, **kargs):
        super(QToolButtonNormal, self).__init__(Qicon, *args, **kargs)
        self.setIconSize(get_iconsize('normal'))


class QToolButtonSmall(QToolButtonBase):
    def __init__(self, Qicon, *args, **kargs):
        super(QToolButtonSmall, self).__init__(Qicon, *args, **kargs)
        self.setIconSize(get_iconsize('small'))


class QToolButtonVRectSmall(QToolButtonBase):
    def __init__(self, Qicon, *args, **kargs):
        super(QToolButtonVRectSmall, self).__init__(Qicon, *args, **kargs)
        self.setIconSize(QSize(8, 20))


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout

    app = QApplication(sys.argv)

    window = QWidget()
    layout = QGridLayout(window)
    layout.addWidget(QToolButtonNormal(get_icon('download')), 0, 0)
    layout.addWidget(QToolButtonNormal(get_icon('close_all')), 0, 1)
    window.show()

    sys.exit(app.exec_())
