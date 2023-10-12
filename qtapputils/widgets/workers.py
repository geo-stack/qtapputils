# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------
from __future__ import annotations
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from uuid import UUID

# ---- Standard imports
from collections import OrderedDict
from time import sleep
import uuid

# ---- Third party imports
from qtpy.QtCore import QObject, QThread, Signal


class WorkerBase(QObject):
    """
    A worker to execute tasks without blocking the GUI.
    """
    sig_task_completed = Signal(object, object)

    def __init__(self):
        super().__init__()
        self._tasks = OrderedDict()

    def add_task(self, task_uuid4, task, *args, **kargs):
        """
        Add a task to the stack that will be executed when the thread of
        this worker is started.
        """
        self._tasks[task_uuid4] = (task, args, kargs)

    def run_tasks(self):
        """Execute the tasks that were added to the stack."""
        for task_uuid4, (task, args, kargs) in self._tasks.items():
            if task is not None:
                method_to_exec = getattr(self, '_' + task)
                returned_values = method_to_exec(*args, **kargs)
            else:
                returned_values = args
            self.sig_task_completed.emit(task_uuid4, returned_values)
        self._tasks = OrderedDict()
        self.thread().quit()

