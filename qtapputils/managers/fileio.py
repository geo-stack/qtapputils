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
                 parent: QWidget = None, atomic: bool = False):
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

    def _get_valid_tempname(self, filename):
        destdir = osp.dirname(filename)
        while True:
            tempname = osp.join(
                destdir,
                f'.temp_{str(uuid.uuid4())[:8]}_'
                f'{osp.basename(filename)}'
                )
            if not osp.exists(tempname):
                return tempname

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
        ave file to the provided filename, with atomic write option.

        Parameters
        ----------
        filename : str
            The absolute path where to save the file.

        Returns
        -------
        filename : str
            The absolute path where the file was successfully saved.
            Returns None if save was cancelled or unsuccessful.
        """
        def _show_warning(message: str):
            QMessageBox.warning(
                self.parent, 'Save Error', message, QMessageBox.Ok
                )

        def _show_critical(error: Exception):
            msg = (f'An unexpected error occurred while saving the file:'
                   f'<br><br>'
                   f'<font color="#CC0000">{type(error).__name__}:</font> '
                   f'{error}')
            QMessageBox.critical(
                self.parent, 'Save Error', msg, QMessageBox.Ok
            )

        write_permission_msg = (
            "You do not have write permission for this location.\n\n"
            "Please choose a different location and try again."
            )
        overwrite_error_msg = (
            "The save operation could not be completed because:\n\n"
            "- You do not have write permission for the selected location"
            ", or\n"
            "- The file is currently in use by another application.\n\n"
            "Please choose a different location or ensure the file is not "
            "open in another program and try again."
            )

        while True:
            file_exists = osp.exists(filename)
            tempname = None

            try:
                if self.atomic:
                    tempname = self._get_valid_tempname(filename)
                    self.onsave(tempname, *args, **kwargs)
                    try:
                        os.replace(tempname, filename)
                        return filename
                    except PermissionError:
                        if file_exists:
                            _show_warning(overwrite_error_msg)
                        else:
                            _show_warning(write_permission_msg)

                        filename = self._get_new_save_filename(filename)
                        if not filename:
                            return None
                else:
                    self.onsave(filename, *args, **kwargs)
                    return filename

            except PermissionError:
                if self.atomic or not file_exists:
                    _show_warning(write_permission_msg)
                else:
                    _show_warning(overwrite_error_msg)

                filename = self._get_new_save_filename(filename)
                if not filename:
                    return None

            except Exception as error:
                _show_critical(error)
                return None

            finally:
                if self.atomic and osp.exists(tempname):
                    try:
                        os.remove(tempname)
                    except Exception:
                        pass

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
            'None' if the saving operation was cancelled or was unsuccessful.
        """
        filename = self._get_new_save_filename(filename)
        if filename:
            return self.save_file(filename, *args, **kwargs)
