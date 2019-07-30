

import os
import shlex
import sys
from os.path import abspath, dirname, exists as pexists, join as pjoin, realpath
from os import makedirs

import numpy as np
import pandas as pd

from missingdata.base import blackholes

cur_dir = dirname(os.path.realpath(__file__))
miss_vis_dir = pjoin(cur_dir, 'missingdata_vis')
makedirs(miss_vis_dir, exist_ok=True)

data_path = pjoin(cur_dir, '..', 'datasets', 'OpenMV', 'travel-times-modified.csv')
# data_path = pjoin(cur_dir, '..', 'datasets', 'OpenMV', 'food-consumption.csv')

df = pd.read_csv(data_path)

# choosing only last 50
# df = df.iloc[-50:,:]

min_missing = 0.00

freq_thresh_show_labels = 0.00

out_path = pjoin(miss_vis_dir,
                 'missing_data_trial_minmiss{}perc_freqmissthresh{}.pdf'
                 ''.format(100 * min_missing, 100 * freq_thresh_show_labels))



fig, ax_frame, ax_freq_over_row, ax_freq_over_col, ax_row_groups, ax_col_groups = \
    blackholes(df,
               label_rows_with='DayOfWeek',
               freq_thresh_show_labels=freq_thresh_show_labels,
               out_path=out_path,
               show_fig=True)

# fig, ax_frame, ax_freq_over_row, ax_freq_over_col, ax_row_groups, ax_col_groups = \
#     blackholes(df,
#                out_path=out_path,
#                show_fig=True)

print()
