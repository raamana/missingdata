#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `missingdata` package."""

import pytest
from missingdata.base import frame

from os import makedirs
from os.path import join as pjoin

import numpy as np
import pandas as pd

import pickle
from os.path import dirname, join as pjoin, realpath
from warnings import catch_warnings, filterwarnings
import warnings
from pyradigm import MLDataset
import umap


in_dir = '/Volumes/data/work/rotman/CANBIND/data/Tier1_v1'
proc_dir = pjoin(in_dir, 'processing')

path_tier1 = pjoin(in_dir, 'Canbind.Primary.Variables.20190114.xlsx')
tier1 = pd.read_excel(path_tier1)

# missing data viz
frame(tier1.iloc[:50,:80],
      label_rows_with='SUBJLABEL')
