# -*- coding: utf-8 -*-

"""Top-level package for missingdata."""

__author__ = """Pradeep Reddy Raamana"""
__email__ = 'raamana@gmail.com'

from sys import version_info
if version_info.major < 3:
    raise NotImplementedError('missingdata package is only tested and supported for '
                              'Python 3 or higher. We encourage upgrading!')

from missingdata.base import blackholes
