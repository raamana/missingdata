# -*- coding: utf-8 -*-

"""
Missing data handling, including visualization and imputation.

Visualization types include:
 1. Frame: cell-wise boolean indicator plot (matrix)
 2. Frequency plots, row- and/or column-wise missingness
 3. Fancy composite combining 1. and 2., with options to color them by groups (rows/cols)
 4. Pairwise correlation

"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import colors

MAX_ROWS_DISPLAYABLE = 60
MAX_COLS_DISPLAYABLE = 80

def frame(data,
          label_rows_with=None,
          label_cols_with=None,
          group_rows_by=None,
          group_cols_by=None,
          figsize=(15, 9),
          missing_color='black',
          backkground_color='silver'):
    """Frame visualization of missingness.

    data : pandas DataFrame or ndarray
        of shape: (num_rows, num_col)

    group_rows_by : iterable, of length num_rows
        List of strings or numbers denoting their membership/category

    group_cols_by : iterable, of length num_cols
        List of strings or numbers denoting their membership/category

    figsize : tuple


    missing_color : str or RGB
        Color name must be one from either
        https://matplotlib.org/examples/color/named_colors.html or
        https://xkcd.com/color/rgb/ (prefix them with 'xkcd:')

    """

    try:
        data = pd.DataFrame(data)
    except:
        raise ValueError('Input must be convertible pandas dataframe!')

    if len(data.shape) != 2:
        raise ValueError('Input data must be 2D matrix!')

    num_rows, num_cols = data.shape

    # cell-wise boolean indicator of whether data is missing in that cell or not
    cell_flag = data.isnull().values

    # ---- labels
    if label_rows_with is not None:
        if label_rows_with in data:
            row_labels = [lbl.strip() for lbl in data[label_rows_with]]
        elif len(label_rows_with) == num_rows:
            row_labels = label_rows_with
        else:
            raise ValueError('invalid input for row labels')
    else:
        row_labels = ['row{}'.format(row) for row in range(num_rows)]

    if label_cols_with is not None:
        if label_cols_with in data:
            col_labels = [lbl.strip() for lbl in data[label_cols_with]]
        elif len(label_cols_with) == num_cols:
            col_labels = label_cols_with
        else:
            raise ValueError('invalid input for column labels')
    else:
        col_labels = data.columns

    row_labels = np.array(row_labels)
    col_labels = np.array(col_labels)

    # --- grouping
    if group_rows_by is not None:
        group_rows_by = np.array(group_rows_by)
        row_group_set, row_group_index = np.unique(group_rows_by, return_inverse=True)

        row_sort_idx = np.argsort(group_rows_by)
        cell_flag, row_labels = reorder_rows(cell_flag, row_labels, row_sort_idx)
        group_rows_sorted = group_rows_by[row_sort_idx]

        show_row_groups = True
        num_row_groups = len(row_group_set)
    else:
        show_row_groups = False

    if group_cols_by is not None:
        group_cols_by = np.array(group_cols_by)
        col_group_set, col_group_index = np.unique(group_cols_by, return_inverse=True)

        col_sort_idx = np.argsort(group_cols_by)
        cell_flag, col_labels = reorder_cols(cell_flag, col_labels, col_sort_idx)
        group_cols_sorted = group_cols_by[col_sort_idx]

        num_col_groups = len(col_group_set)
        show_col_groups = True
    else:
        show_col_groups = False
        

    # ---
    missing_color = colors.to_rgb(missing_color)  # no alpha
    backkground_color = colors.to_rgb(backkground_color)

    frame = np.zeros((num_rows, num_cols, 3), dtype='float64')
    frame[ cell_flag, :] = missing_color
    frame[~cell_flag, :] = backkground_color

    row_wise_freq = cell_flag.sum(axis=1).reshape(-1, 1)  # ensuring its atleast 2D
    col_wise_freq = cell_flag.sum(axis=0).reshape(1, -1)

    # --- positioning
    fig = plt.figure(figsize=figsize)
    width = 0.7
    height = 0.7
    left_freq_over_col = 0.1

    frame_bottom = 0.03
    freq_cell_size = 0.03

    frame_left = left_freq_over_col + freq_cell_size + 0.01

    ax_frame = fig.add_axes((frame_left, frame_bottom, width, height), frameon=False)
    ax_frame.imshow(frame)
    ax_frame.axis('off') # remove axes, ticks etc
    ax_frame.set_aspect('auto')

    ax_freq_over_col = fig.add_axes((left_freq_over_col, frame_bottom,
                                     freq_cell_size, height),
                                    sharey=ax_frame)
    ax_freq_over_col.set_xticks([])
    ax_freq_over_col.set_xticklabels([])
    if num_rows <= 60:
        ax_freq_over_col.set_yticks(range(num_rows))
        ax_freq_over_col.set_yticklabels(row_labels)
    else:
        ax_freq_over_col.set_yticks([])
        ax_freq_over_col.set_yticklabels([])
    ax_freq_over_col.imshow(row_wise_freq)
    ax_freq_over_col.set_aspect('auto')

    ax_freq_over_row = fig.add_axes((frame_left, height + freq_cell_size+ 0.01,
                                     width, freq_cell_size),
                                    sharex=ax_frame)
    ax_freq_over_row.imshow(col_wise_freq)
    ax_freq_over_row.set_yticks([])
    ax_freq_over_row.set_yticklabels([])
    if num_cols <= 80:
        ax_freq_over_row.xaxis.set_ticks_position('top')
        ax_freq_over_row.set_xticks(range(num_cols))
        ax_freq_over_row.set_xticklabels(col_labels, rotation=90)
    else:
        ax_freq_over_row.set_xticks([])
        ax_freq_over_col.set_xticklabels([])
    ax_freq_over_row.set_aspect('auto')

    # --- grouping indicators
    if show_row_groups:
        grpwise_freq_row = np.array([row_wise_freq[group_rows_sorted==row].sum() for
                                     row in row_group_set]).reshape(-1,1)
        ext_row_groups = (ext_frame[0]+ext_frame[2]+0.01, frame_bottom,
                          freq_cell_size, height)
        ax_row_groups = fig.add_axes(ext_row_groups) #sharey would be a problem
        ax_row_groups.imshow(grpwise_freq_row)
        ax_row_groups.set(xticks=[], xticklabels=[])
        ax_row_groups.yaxis.tick_right()
        if num_row_groups <= MAX_ROWS_DISPLAYABLE:
            ax_row_groups.set(yticks=range(num_row_groups), yticklabels=row_group_set)
        else:
            ax_row_groups.set(yticks=[], yticklabels=[])
        ax_row_groups.set_aspect('auto')
            
    if show_col_groups:
        grpwise_freq_col = np.array([col_wise_freq[:, group_cols_sorted==col].sum() for
                                     col in col_group_set]).reshape(1,-1)
        ext_col_groups = (frame_left, frame_bottom - freq_cell_size - 0.02,
                          width, freq_cell_size)

        ax_col_groups = fig.add_axes(ext_col_groups) #sharex would be a problem
        ax_col_groups.imshow(grpwise_freq_col)
        ax_col_groups.set(yticks=[], yticklabels=[])
        if num_col_groups <= MAX_COLS_DISPLAYABLE:
            ax_col_groups.set(xticks=range(num_col_groups), xticklabels=col_group_set)
        else:
            ax_col_groups.set(xticks=[], xticklabels=[])
        ax_col_groups.set_aspect('auto')

    # plt.tight_layout()

    plt.show(block=False)


    return ax_frame, ax_freq_over_row, ax_freq_over_col
