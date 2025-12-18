# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------
import importlib
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # Direct imports for type-checking and IDE introspection.
    from .taskmanagers import WorkerBase, TaskManagerBase, LIFOTaskManager
    from .fileio import SaveFileManager
    from .shortcuts import (
        ShortcutManager, TitleSyncTranslator, ToolTipSyncTranslator,
        ActionMenuSyncTranslator)
else:
    # Module-level exports for explicit __all__.
    __all__ = [
        'WorkerBase',
        'TaskManagerBase',
        'LIFOTaskManager',
        'SaveFileManager',
        'ShortcutManager',
        'TitleSyncTranslator',
        'ToolTipSyncTranslator',
        'ActionMenuSyncTranslator',
        ]

    # Lazy import mapping.
    __LAZYIMPORTS__ = {
        'WorkerBase': 'qtapputils.managers.taskmanagers',
        'TaskManagerBase': 'qtapputils.managers.taskmanagers',
        'LIFOTaskManager': 'qtapputils.managers.taskmanagers',
        'SaveFileManager': 'qtapputils.managers.fileio',
        'ShortcutManager': 'qtapputils.managers.shortcuts',
        'TitleSyncTranslator': 'qtapputils.managers.shortcuts',
        'ToolTipSyncTranslator': 'qtapputils.managers.shortcuts',
        'ActionMenuSyncTranslator': 'qtapputils.managers.shortcuts'
        }

    def __getattr__(name):
        if name in __LAZYIMPORTS__:
            module_path = __LAZYIMPORTS__[name]

            try:
                module = importlib.import_module(module_path)
                attr = getattr(module, name)
                globals()[name] = attr

                return attr

            except ImportError as e:
                raise ImportError(
                    f"Failed to lazy import {name!r} from {module_path!r}: {e}"
                ) from e

            except AttributeError as e:
                raise AttributeError(
                    f"Module {module_path!r} has no attribute {name!r}"
                ) from e

        # Standard AttributeError for unknown attributes
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    def __dir__():
        return sorted(set(
            list(globals().keys()) +
            list(__LAZYIMPORTS__.keys()) +
            list(__all__)
            ))
