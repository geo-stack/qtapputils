# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/qtapputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

"""
File for running tests programmatically.
"""

import os
os.environ['QTAPPUTILS_PYTEST'] = 'True'

import pytest


def main():
    """
    Run pytest tests.
    """
    args = ['-x', 'qtapputils', '-v', '-rw', '--durations=10',
            '--cov=qtapputils', '-o', 'junit_family=xunit2']
    if os.environ.get('Azure', None) is not None:
        args.append('--no-coverage-upload')
    errno = pytest.main(args)
    if errno != 0:
        raise SystemExit(errno)


if __name__ == '__main__':
    main()
