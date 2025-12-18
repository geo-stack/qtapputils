# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------


# ---- Stantard imports
from colorama import Fore


def print_warning(warning_type: str | type, message: str):
    """Print a formatted warning message to console."""
    if not isinstance(warning_type, str):
        warning_type = warning_type.__name__

    print(f"\n{Fore.RED}{warning_type}:{Fore.RESET} {message}")
