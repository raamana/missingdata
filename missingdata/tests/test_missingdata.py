#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `missingdata` package."""

from os import makedirs
from os.path import join as pjoin

import numpy as np
import pandas as pd

from missingdata.base import blackholes

# from quilt.data.ResidentMario import missingno_data
# collisions = missingno_data.nyc_collision_factors()
# collisions = collisions.replace("nan", np.nan)

in_dir = '/Volumes/data/work/rotman/CANBIND/data/Tier1_v1'
proc_dir = pjoin(in_dir, 'processing')
miss_vis_dir = pjoin(proc_dir, 'missingdata_vis')
makedirs(miss_vis_dir, exist_ok=True)

path_tier1 = pjoin(in_dir, 'Canbind.Primary.Variables.20190114.xlsx')
tier1_full = pd.read_excel(path_tier1)

np.random.seed(342)
rows = np.random.randint(0, 180, 150)
cols = np.append([0, 1], np.random.randint(2, 120, 100))  # keeping cols 0 and 1
tier1 = tier1_full.iloc[rows, cols]

path_dict_tier1 = pjoin(in_dir, 'Canbind.Tier.1.variables.DICT.0002.xlsx')
dict_tier1 = pd.read_excel(path_dict_tier1)

col_groups = dict_tier1['Category'].values.astype('str')

var_catg = np.genfromtxt(pjoin(proc_dir, 'variable_to_category.txt'),
                         dtype='str', delimiter=',')
subjlabel_dx = np.genfromtxt(pjoin(proc_dir, 'subjlabel_to_diagnosis.txt'),
                             dtype='str', delimiter=',')

catg = {var: catg for var, catg in var_catg}
diag = {lbl: dx for lbl, dx in subjlabel_dx}

row_groups = [diag[slbl] if slbl in diag else 'Unknown' for slbl in tier1['SUBJLABEL']]
col_groups = [catg[varb] if varb in catg else 'Unknown' for varb in tier1.columns]

# making them short
row_groups = [r[:4] for r in row_groups]
col_groups = [c[:4] for c in col_groups]

min_missing = 0.00
freq_thresh_show_labels = .01
out_path = pjoin(miss_vis_dir,
                 'missing_data_trial_minmiss{}perc_freqmissthresh{}.pdf'
                 ''.format(100 * min_missing, 100 * freq_thresh_show_labels))

# # missing data viz
# fig, ax_frame, \
# ax_freq_over_row, ax_freq_over_col, \
# ax_row_groups, ax_col_groups = blackholes(tier1,
#                                      label_rows_with='SUBJLABEL',
#                                      freq_thresh_show_labels=freq_thresh_show_labels,
#                                      out_path=out_path,
#                                      show_fig=True)

# fig, ax_frame, ax_freq_over_row, ax_freq_over_col, ax_row_groups, ax_col_groups \
#     = blackholes(tier1,
#             filter_spec_samples=(min_missing, 1.0),
#             filter_spec_variables=(min_missing, 1.0),
#             label_rows_with='SUBJLABEL',
#             freq_thresh_show_labels=freq_thresh_show_labels,
#             out_path=out_path,
#             show_fig=True)


fig, ax_frame, ax_freq_over_row, ax_freq_over_col, ax_row_groups, ax_col_groups = \
    blackholes(tier1, label_rows_with='SUBJLABEL',
               group_rows_by=row_groups, group_cols_by=col_groups,
               freq_thresh_show_labels=freq_thresh_show_labels,
               out_path=out_path, show_fig=True)

print()
