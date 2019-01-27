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
from missingdata import config as cfg

def frame(data,
          label_rows_with=None,
          label_cols_with=None,
          group_rows_by=None,
          group_cols_by=None,
          missing_color='black',
          backkground_color='silver',
          group_wise_colorbar=False,
          figsize=(15, 9),
          ):
    """Frame visualization of missingness.

    data : pandas DataFrame or ndarray
        of shape: (num_rows, num_col)

    group_rows_by : iterable, of length num_rows
        List of strings or numbers denoting their membership/category

    group_cols_by : iterable, of length num_cols
        List of strings or numbers denoting their membership/category

    missing_color : str or RGB
        Color name must be one from either
        https://matplotlib.org/examples/color/named_colors.html or
        https://xkcd.com/color/rgb/ (prefix them with 'xkcd:')

    figsize : tuple

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
        row_group_index_sorted = row_group_index[row_sort_idx]

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
        col_group_index_sorted = col_group_index[col_sort_idx]

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
    height = 0.6
    left_freq_over_col = 0.1

    frame_bottom = 0.08
    freq_cell_size = 0.02
    group_cell_size = 0.01
    group_cell_height = 0.02

    # FOC:freq over cols
    ext_FOC = (left_freq_over_col, frame_bottom, freq_cell_size, height)
    if show_row_groups:
        ext_show_row_groups = (ext_FOC[0]+ext_FOC[2]+0.005, ext_FOC[1],
                               group_cell_size, height)
        frame_left = ext_show_row_groups[0] + group_cell_size+ 0.01
    else:
        frame_left = ext_FOC[0]+ext_FOC[2]+0.005

    ext_frame = (frame_left, frame_bottom, width, height)
    # FOR: freq over rows
    if show_col_groups:
        ext_show_col_groups = (frame_left, frame_bottom+ext_frame[3]+group_cell_height+0.005,
                          width, group_cell_height)
        ext_FOR = (frame_left, ext_show_col_groups[1]+group_cell_height+0.01,
                   width, freq_cell_size)
    else:
        ext_FOR = (frame_left, frame_bottom+ height + freq_cell_size + 0.02,
               width, freq_cell_size)

    # ---
    ax_frame = fig.add_axes(ext_frame, frameon=False)
    ax_frame.imshow(frame)
    ax_frame.axis('off') # remove axes, ticks etc
    ax_frame.set_aspect('auto')

    # ---
    ax_freq_over_col = fig.add_axes(ext_FOC, sharey=ax_frame)
    ax_freq_over_col.set_xticks([])
    ax_freq_over_col.set_xticklabels([])
    if num_rows <= cfg.MAX_ROWS_DISPLAYABLE:
        ax_freq_over_col.set_yticks(range(num_rows))
        ax_freq_over_col.set_yticklabels(row_labels)
    else:
        ax_freq_over_col.set_yticks([])
        ax_freq_over_col.set_yticklabels([])
    ax_freq_over_col.imshow(row_wise_freq)
    ax_freq_over_col.set_aspect('auto')

    # ---
    ax_freq_over_row = fig.add_axes(ext_FOR, sharex=ax_frame)
    ax_freq_over_row.imshow(col_wise_freq)
    ax_freq_over_row.set_yticks([])
    ax_freq_over_row.set_yticklabels([])
    if num_cols <= cfg.MAX_COLS_DISPLAYABLE:
        ax_freq_over_row.xaxis.set_ticks_position('top')
        ax_freq_over_row.set_xticks(range(num_cols))
        ax_freq_over_row.set_xticklabels(col_labels, rotation=90)
    else:
        ax_freq_over_row.set_xticks([])
        ax_freq_over_col.set_xticklabels([])
    ax_freq_over_row.set_aspect('auto')

    # --- grouping indicators: direct association by proximity
    if show_row_groups:
        ax_row_groups = fig.add_axes(ext_show_row_groups)
        decorate_row_groups_with_total_freq(ax_row_groups, row_group_index_sorted,
                                            row_wise_freq, row_group_set)

    # colorbar at bottom
    if show_col_groups:
        ax_col_groups = fig.add_axes(ext_show_col_groups)
        decorate_col_groups_with_total_freq(ax_col_groups, col_group_index_sorted,
                                            col_wise_freq, col_group_set)


    # --- grouping stats - no association by proximity
    # colorbar on the right
    if show_row_groups and group_wise_colorbar:
        grpwise_freq_row = np.array([row_wise_freq[group_rows_sorted==row].sum() for
                                     row in row_group_set]).reshape(-1,1)
        ext_row_groups = (ext_frame[0]+ext_frame[2]+0.01, frame_bottom,
                          freq_cell_size, height)
        ax_row_groups = fig.add_axes(ext_row_groups) #sharey would be a problem
        ax_row_groups.imshow(grpwise_freq_row)
        ax_row_groups.set(xticks=[], xticklabels=[])
        ax_row_groups.yaxis.tick_right()
        if num_row_groups <= cfg.MAX_ROWS_DISPLAYABLE:
            ax_row_groups.set(yticks=range(num_row_groups), yticklabels=row_group_set)
        else:
            ax_row_groups.set(yticks=[], yticklabels=[])
        ax_row_groups.set_aspect('auto')

    # colorbar at bottom
    if show_col_groups and group_wise_colorbar:
        grpwise_freq_col = np.array([col_wise_freq[:, group_cols_sorted==col].sum() for
                                     col in col_group_set]).reshape(1,-1)
        ext_col_groups = (frame_left, frame_bottom - freq_cell_size - 0.02,
                          width, freq_cell_size)
        ax_col_groups = fig.add_axes(ext_col_groups) #sharex would be a problem
        ax_col_groups.imshow(grpwise_freq_col)
        ax_col_groups.set(yticks=[], yticklabels=[])
        if num_col_groups <= cfg.MAX_COLS_DISPLAYABLE:
            ax_col_groups.set(xticks=range(num_col_groups), xticklabels=col_group_set)
        else:
            ax_col_groups.set(xticks=[], xticklabels=[])
        ax_col_groups.set_aspect('auto')

    # plt.tight_layout()

    plt.show(block=False)


    return ax_frame, ax_freq_over_row, ax_freq_over_col



def reorder_rows(cell_flag, row_labels, row_group_index):

    return cell_flag[row_group_index,:], row_labels[row_group_index]


def reorder_cols(cell_flag, col_labels, col_group_index):

    return cell_flag[:, col_group_index], col_labels[col_group_index]


def decorate_row_groups_with_total_freq(ax, group_idx, freq, group_names):
    """Fancy plot to show where the ROW groups are, and their total missingness."""

    ax.imshow(group_idx.reshape(-1, 1), cmap=cfg.cmap_grouping)
    ax.set(xticks=[], xticklabels=[],
           yticks=[], yticklabels=[])
    ax.set_aspect('auto')

    freq = freq.ravel()
    total_missingness = np.sum(freq)
    for gg, name in enumerate(group_names):
        this_grp_idx = np.flatnonzero(group_idx==gg)
        this_grp_freq = freq[this_grp_idx].sum()
        # first_idx = this_grp_idx[0]
        mean_idx = int(np.mean(this_grp_idx))
        identifier = '{} {:.2f}%'.format(name, 100*this_grp_freq/total_missingness)
        ax.text(-0.25, mean_idx, identifier,
                color=cfg.grouping_text_color,
                # backgroundcolor=cfg.grouping_text_color_background,
                fontweight=cfg.grouping_fontweight,
                rotation=90, verticalalignment='center')


def decorate_col_groups_with_total_freq(ax, group_idx, freq, group_names):
    """Fancy plot to show where the COLUMN groups are, and their total missingness."""

    ax.imshow(group_idx.reshape(1, -1), cmap=cfg.cmap_grouping)
    ax.set(xticks=[], xticklabels=[],
           yticks=[], yticklabels=[])
    ax.set_aspect('auto')
    ax.set_frame_on(False)

    freq = freq.ravel()
    total_missingness = np.sum(freq)
    for gg, name in enumerate(group_names):
        this_grp_idx = np.flatnonzero(group_idx==gg)
        this_grp_freq = freq[this_grp_idx].sum()
        mean_idx = int(np.mean(this_grp_idx))
        identifier = '{} {:.2f}%'.format(name, 100*this_grp_freq/total_missingness)
        ax.text(mean_idx, 0.05, identifier,
                color=cfg.grouping_text_color,
                # backgroundcolor=cfg.grouping_text_color_background,
                fontweight=cfg.grouping_fontweight,
                horizontalalignment='center', verticalalignment='center')
