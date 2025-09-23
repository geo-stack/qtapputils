# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

from __future__ import annotations
from typing import Callable

# ---- Standard imports
import os
import os.path as osp
import uuid

# ---- Third party imports
from qtpy.QtCore import QObject
from qtpy.QtWidgets import QMessageBox, QFileDialog, QWidget


class SaveFileManager(QObject):
    def __init__(self, namefilters: dict, onsave: Callable,
                 parent: QWidget = None, atomic: str = None):
        """
        A manager to save files.

        Parameters
        ----------
        namefilters : dict
            A dictionary containing the file filters to use in the
            'Save As' file dialog. For example:

                namefilters = {
                    '.pdf': 'Portable Document Format (*.pdf)',
                    '.svg': 'Scalable Vector Graphics (*.svg)',
                    '.png': 'Portable Network Graphics (*.png)',
                    '.jpg': 'Joint Photographic Expert Group (*.jpg)'
                    }

            Note that the first entry in the dictionary will be used as the
            default name filter in the 'Save As' dialog.
        onsave : Callable
            The callable that is used to save the file. This should be a
            function that takes the output filename as its first argument,
            and writes the file contents to disk.
        parent: QWidget, optional
            The parent widget to use for the 'Save As' file dialog.
        atomic: str
            Whether to save the file atomically.
        """
        super().__init__()
        self.parent = parent
        self.namefilters = namefilters
        self.onsave = onsave
        self.atomic = atomic

    def _get_new_save_filename(self, filename):
        root, ext = osp.splitext(filename)
        if ext not in self.namefilters:
            ext = next(iter(self.namefilters))
            filename += ext

        filename, filefilter = QFileDialog.getSaveFileName(
            self.parent,
            "Save As",
            filename,
            ';;'.join(self.namefilters.values()),
            self.namefilters[ext])

        if filename:
            # Make sure the filename has the right extension.
            ext = dict(map(reversed, self.namefilters.items()))[filefilter]
            if not filename.endswith(ext):
                filename += ext

        return filename

    # ---- Public methods
    def save_file(self, filename: str, *args, **kwargs) -> str:
        """
        Save in provided filename.

        Parameters
        ----------
        filename : str
            The absolute path where to save the file.

        Returns
        -------
        filename : str
            The absolute path where the file was successfully saved. Returns
            'None' if the saving operation was cancelled or was unsuccessful.
        """
        file_in_use_msg = (
            "The save file operation cannot be completed because "
            "the file is in use by another application or user."
            )
        save_except_msg = (
            'An unexpected error occurred while saving the file:'
            '<br><br>'
            '<font color="{}">{}:</font> {}'
            )

        if self.atomic:
            while True:

                destdir = osp.dirname(filename)
                while True:
                    tempname = osp.join(
                        destdir,
                        f'.temp_{str(uuid.uuid4())[:8]}_'
                        f'{osp.basename(filename)}'
                        )
                    if not osp.exists(tempname):
                        break

                try:
                    self.onsave(tempname, *args, **kwargs)
                    os.replace(tempname, filename)
                    return filename
                except PermissionError:
                    QMessageBox.warning(
                        self.parent, 'File in Use',
                        file_in_use_msg, QMessageBox.Ok)

                    filename = self._get_new_save_filename(filename)

                    if not filename:
                        return None
                except Exception as error:
                    message = save_except_msg.format(
                        '#CC0000', type(error).__name__, error)
                    QMessageBox.critical(
                        self.parent, 'Save Error', message, QMessageBox.Ok)
                    return None
                finally:
                    if osp.exists(tempname):
                        try:
                            os.remove(tempname)
                        except Exception:
                            pass
        else:
            while True:
                try:
                    self.onsave(filename, *args, **kwargs)
                    return filename
                except PermissionError:
                    QMessageBox.warning(
                        self.parent, 'File in Use',
                        file_in_use_msg, QMessageBox.Ok)

                    filename = self._get_new_save_filename(filename)

                    if not filename:
                        return None

                except Exception as error:
                    message = save_except_msg.format(
                        '#CC0000', type(error).__name__, error)
                    QMessageBox.critical(
                        self.parent,
                        'Save Error',
                        message,
                        QMessageBox.Ok)

                    return None

    def save_file_as(self, filename: str, *args, **kwargs) -> str:
        """
        Save in a new file.

        Parameters
        ----------
        filename : dict
            The default or suggested absolute path where to save the file.

        Returns
        -------
        filename : str
            The absolute path where the file was successfully saved. Returns
            'None' if the saving operation was cancelled or was unsuccessfull.
        """
        filename = self._get_new_save_filename(filename)
        if filename:
            return self.save_file(filename, *args, **kwargs)
