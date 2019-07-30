# -*- coding: utf-8 -*-

"""
Missing data handling, including visualization and imputation.

Visualization types include:
 1. blackholes: cell-wise boolean indicator plot (in a matrix form),
    showing blackholes where data is missing
 2. Frequency plots, row- and/or column-wise missingness
 3. Fancy composite combining 1. and 2., with options to color them by groups (rows/cols)
 4. Pairwise correlation

"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import colors
from os.path import realpath

from missingdata import config as cfg
from missingdata.utils import set_labels, remove_ticks_labels, \
    check_freq_thresh_labels


def blackholes(data_in,
               filter_spec_samples=None,
               filter_spec_variables=None,
               label_rows_with=None,
               label_cols_with=None,
               group_rows_by=None,
               group_cols_by=None,
               missing_color='black',
               backkground_color='silver',
               freq_thresh_show_labels=0.0,
               show_all_labels=False,
               group_wise_colorbar=False,
               figsize=(15, 10),
               out_path=None,
               show_fig=False
               ):
    """Visualization of holes (missingness) in data and their frequency.

    If you don't see any labels (for rows or columns), it may be because the total
    effective number of rows/cols being displayed, after applying filter_spec_*,
    exceeded a preset number (60/80) to avoid occlusion or illegible labeling.
    You can use the  the parameter freq_thresh_show_labels to bring the effective
    number of rows/cols to display to smaller number.

    data_in : pandas DataFrame
        of shape: (num_rows, num_col)

    filter_spec_samples : (float, float) or callable
        Mechanism to discard samples or variables with missing values below this
        threshold. This must be a tuple of two values in the closed interval [0,1].
        Default: do not show complete samples or variables (those with no missing data).
        This is very useful when sample size or dimensionality is high, so the plot
        legends and other labels are not too crowded or occluded altogether.
        To focus on those with frequently missing data (e.g. top 30%), choose (0.7, 1)
        To focus on those rarely missing (bottom 10%), choose (0.0, 0.1)
        To focus on both frequent/rare cases, pass in a callable that takes a float value
        as input (between 0 and 1) and returns a bool value to include or not e.g.

        def to_include(perc): return (perc<0.1) or (perc>0.9)

    filter_spec_variables : (float, float) or callable
        same as filter_spec_samples (which is for rows), except for variables (columns)

    label_rows_with : str or int or list of len num_rows
        Name of the variable in panda DataFrame to label rows with, or a list of
        elements convertible to str (like int etc) of the same length as num_rows

    label_cols_with : str or int or list of len num_cols
        Name of the variable in panda DataFrame to label columns with, or a list of
        elements convertible to str (like int etc) of the same length as num_rows

    group_rows_by : iterable, of length num_rows
        List of strings or numbers denoting their membership/category

    group_cols_by : iterable, of length num_cols
        List of strings or numbers denoting their membership/category

    missing_color : str or RGB
        Color name must be one from either
        https://matplotlib.org/examples/color/named_colors.html or
        https://xkcd.com/color/rgb/ (prefix them with 'xkcd:')
        Default: 'black'

    backkground_color : str or RGB
        Color name must be one from either
        https://matplotlib.org/examples/color/named_colors.html or
        https://xkcd.com/color/rgb/ (prefix them with 'xkcd:')
        Default: 'silver'

    freq_thresh_show_labels : float
        A threshold [0, 1) to not show labels for samples/columns with missingness
        frequency below this value. Very useful in when number of samples or variables
        is large, and you would like to see the holes (missing values) in the context
        of complete-data, while being able to easily identify which ones are missing.
        This parameter/option exists to avoid occlusion or illegible labeling, when
        the total effective number of rows/cols being displayed, after applying
        filter_spec_*, exceeded a preset number (60/80) to avoid occlusion or
        illegible labeling. You can use a higher threshold to bring the effective
        number of rows/cols to display to smaller number.
        Default: 0.0

    show_all_labels : bool
        A parameter to force the display of labels for both rows and columns,
        even if their number is large and they may result in text becoming
        occluded or illegible. The parameter freq_thresh_show_labels takes
        precedence over this parameter.
        Default: False

    group_wise_colorbar : bool
        Flag to indicate whether to display the innermost colorbar
        to indicate the groups rows or columns belong to
        Default: False

    figsize : tuple
        Tuple of (width, height) to control the size of the plot.
        Default: (15, 10)

    out_path : str
        Absolute path to export the figure to disk (PDF format, 300dpi).

    show_fig : bool
        Flag to indicate whether to bring the figure to foreground
        Default: False

    """

    try:
        data_in = pd.DataFrame(data_in)
    except:
        raise ValueError('Input must be convertible to a pandas dataframe!')

    num_rows_orig, num_cols_orig = data_in.shape
    if len(data_in.shape) != 2:
        raise ValueError('Input data must be 2D matrix!')

    label_filter = check_freq_thresh_labels(freq_thresh_show_labels)

    # ---- labels
    row_labels = process_labels(data_in, label_rows_with, num_rows_orig,
                                'row', 'row')
    col_labels = process_labels(data_in, label_cols_with, num_cols_orig,
                                data_in.columns, 'col')

    # adjusting defaults when dealing with very small samples
    # as even a small eps requirement for miss perc can exclude most samples
    filter_spec_samples = _set_default_filter_spec(filter_spec_samples,
                                                   data_in.shape[0],
                                                   cfg.MAX_ROWS_DISPLAYABLE)
    filter_spec_variables = _set_default_filter_spec(filter_spec_variables,
                                                   data_in.shape[1],
                                                   cfg.MAX_COLS_DISPLAYABLE)

    # filtering data
    data, row_filter, col_filter = freq_filter(data_in,
                                               filter_spec_samples,
                                               filter_spec_variables)
    # accordingly filterning labels
    row_labels = row_labels[row_filter]
    col_labels = col_labels[col_filter]

    # new size
    num_rows, num_cols = data.shape
    cell_flag = data.isnull().values


    # --- grouping
    if group_rows_by is not None:
        group_rows_by = np.array(group_rows_by)
        if len(group_rows_by) != num_rows_orig:
            raise ValueError('Grouping variable for samples/rows must have {} elements'
                             ''.format(num_rows_orig))
        group_rows_by = group_rows_by[row_filter]
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
        if len(group_cols_by) != num_cols_orig:
            raise ValueError('Grouping variable for variables/cols must have {} elements'
                             ''.format(num_cols_orig))
        group_cols_by = group_cols_by[col_filter]
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

    # normalizing frequency
    row_wise_freq = row_wise_freq / row_wise_freq.sum()
    col_wise_freq = col_wise_freq / col_wise_freq.sum()

    # --- positioning
    fig = plt.figure(figsize=figsize)
    width = 0.7
    height = 0.6
    left_freq_over_col = 0.1

    frame_bottom = 0.08
    freq_cell_size = 0.03
    group_cell_size = 0.015
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
        ext_show_col_groups = (frame_left,
                               frame_bottom+ext_frame[3]+group_cell_height+0.005,
                               width,
                               group_cell_height)
        ext_FOR = (frame_left,
                   ext_show_col_groups[1]+group_cell_height+0.01,
                   width,
                   freq_cell_size)
    else:
        ext_FOR = (frame_left,
                   frame_bottom+ height + freq_cell_size + 0.02,
                   width,
                   freq_cell_size)

    # ---
    ax_frame = fig.add_axes(ext_frame, frameon=False)
    ax_frame.imshow(frame)
    ax_frame.axis('off') # remove axes, ticks etc
    ax_frame.set_aspect('auto')

    # ---
    ax_freq_over_col = fig.add_axes(ext_FOC, sharey=ax_frame)
    remove_ticks_labels(ax_freq_over_col, 'x')
    if freq_thresh_show_labels > 0.0:
        set_labels(ax_freq_over_col, 'y',
                   range(num_rows), row_labels,
                   row_wise_freq, label_filter)
    else:
        if show_all_labels or num_rows <= cfg.MAX_ROWS_DISPLAYABLE:
            set_labels(ax_freq_over_col, 'y', range(num_rows), row_labels)
        else:
            remove_ticks_labels(ax_freq_over_col, 'y')

    ax_freq_over_col.imshow(row_wise_freq)
    ax_freq_over_col.set_aspect('auto')

    # ---
    ax_freq_over_row = fig.add_axes(ext_FOR, sharex=ax_frame)
    ax_freq_over_row.imshow(col_wise_freq)
    ax_freq_over_row.xaxis.tick_top()
    remove_ticks_labels(ax_freq_over_row, 'y')
    if freq_thresh_show_labels > 0.0:
        ax_freq_over_row.xaxis.set_ticks_position('top')
        set_labels(ax_freq_over_row, 'x', range(num_cols), col_labels,
                   col_wise_freq.ravel(), label_filter, rotation=90)
    else:
        if show_all_labels or num_cols <= cfg.MAX_COLS_DISPLAYABLE:
            set_labels(ax_freq_over_row, 'x', range(num_cols), col_labels,
                       rotation=90)
        else:
            remove_ticks_labels(ax_freq_over_row, 'x')
    ax_freq_over_row.set_aspect('auto')

    # --- grouping indicators: direct association by proximity
    if show_row_groups:
        ax_row_groups = fig.add_axes(ext_show_row_groups)
        decorate_row_groups_with_total_freq(ax_row_groups, row_group_index_sorted,
                                            row_wise_freq, row_group_set)
    else:
        ax_row_groups = None

    # colorbar at bottom
    if show_col_groups:
        ax_col_groups = fig.add_axes(ext_show_col_groups)
        decorate_col_groups_with_total_freq(ax_col_groups, col_group_index_sorted,
                                            col_wise_freq, col_group_set)
    else:
        ax_col_groups = None


    # --- grouping stats - no association by proximity
    # colorbar on the right
    if show_row_groups and group_wise_colorbar:
        grpwise_freq_row = np.array([row_wise_freq[group_rows_sorted==row].sum() for
                                     row in row_group_set]).reshape(-1,1)
        ext_row_groups = (ext_frame[0]+ext_frame[2]+0.01,
                          frame_bottom,
                          freq_cell_size,
                          height)
        ax_row_groups = fig.add_axes(ext_row_groups) #sharey would be a problem
        ax_row_groups.imshow(grpwise_freq_row)
        remove_ticks_labels(ax_row_groups, 'x')
        ax_row_groups.yaxis.tick_right()
        if show_all_labels or num_row_groups <= cfg.MAX_ROWS_DISPLAYABLE:
            ax_row_groups.set(yticks=range(num_row_groups), yticklabels=row_group_set)
        else:
            remove_ticks_labels(ax_row_groups, 'y')
        ax_row_groups.set_aspect('auto')

    # colorbar at bottom
    if show_col_groups and group_wise_colorbar:
        grpwise_freq_col = np.array([col_wise_freq[:, group_cols_sorted==col].sum() for
                                     col in col_group_set]).reshape(1,-1)
        ext_col_groups = (frame_left,
                          frame_bottom - freq_cell_size - 0.02,
                          width,
                          freq_cell_size)
        ax_col_groups = fig.add_axes(ext_col_groups) #sharex would be a problem
        ax_col_groups.imshow(grpwise_freq_col)
        remove_ticks_labels(ax_col_groups, 'y')
        if show_all_labels or num_col_groups <= cfg.MAX_COLS_DISPLAYABLE:
            ax_col_groups.set(xticks=range(num_col_groups), xticklabels=col_group_set)
        else:
            remove_ticks_labels(ax_col_groups, 'x')
        ax_col_groups.set_aspect('auto')

    # plt.tight_layout()

    if show_fig:
        plt.show(block=False)

    if out_path is not None:
        fig.savefig(realpath(out_path), dpi=300, format='pdf')

    return fig, ax_frame, \
           ax_freq_over_row, ax_freq_over_col, \
           ax_row_groups, ax_col_groups


def comissing(data_in,
              filter_spec_samples=(np.finfo(np.float32).eps, 1.0),
              filter_spec_variables=(np.finfo(np.float32).eps, 1.0),
              cmap='viridis',
              figsize=(15, 10),
              out_path=None,
              show_fig=False
              ):
    """
    Pairwise relations in missingness (co-missing) between variables/subjects.

    """

    raise NotImplementedError()


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
                rotation=90,
                verticalalignment='center')


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
                horizontalalignment='center',
                verticalalignment='center')


def freq_filter(data, row_spec, col_spec):
    """Removes samples and variables according to their missing data frequency"""

    row_filter = _validate_filter_spec(row_spec)
    col_filter = _validate_filter_spec(col_spec)

    # cell-wise boolean indicator of whether data is missing in that cell or not
    cell_flag = data.isnull().values

    row_freq = cell_flag.sum(axis=1).ravel()
    col_freq = cell_flag.sum(axis=0).ravel()

    filtered_rows = np.fromiter(map(row_filter, row_freq / row_freq.size), dtype=bool)
    filtered_cols = np.fromiter(map(col_filter, col_freq / col_freq.size), dtype=bool)

    return data.iloc[filtered_rows, filtered_cols], filtered_rows, filtered_cols


def _set_default_filter_spec(spec, size, max_size):
    """Adjusts the defaults filter spec when dealing with small samples"""

    if spec is None:
        out_spec = (0, 1) if size < max_size else (np.finfo(np.float32).eps, 1.0)
    else:
        out_spec = spec

    return out_spec


def _validate_filter_spec(spec):
    """Validates input and returns a func"""

    if isinstance(spec, (tuple, list)):
        error_msg_window = 'Filter perc must be specified as a tuple of two values: ' \
                           '(low, high), each value must be between 0 and 1.'

        if not len(spec) == 2:
            raise ValueError(error_msg_window)

        spec = np.array(spec)
        if (spec < 0.0).any() or (spec > 1.0).any():
            raise ValueError(error_msg_window)

        low_perc, high_perc = spec
        filter_func = lambda perc: (perc >= low_perc) and (perc <= high_perc)

    elif callable(spec):
        if not isinstance(spec(0.5), bool):
            raise ValueError('When filter spec is callable, its return value must be '
                             ' of type bool!')
        filter_func = spec
    else:
        raise TypeError('filter spec can only be a tuple or callable!')

    return filter_func


def process_labels(data, labels, length, default_prefix='row', type_='row'):
    """Returns the labels for samples/variables."""

    strip_all = lambda arr : [lbl.strip() for lbl in arr]

    if labels is not None:
        if labels in data:
            out_labels = data[labels]
        elif len(labels) == length:
            out_labels = labels
        else:
            raise ValueError('invalid input for {} labels!'
                             'It must be a column name in DataFrame or a list of '
                             'str or int, of the same number of {}s'
                             ''.format(type_, type_))
    else:
        if isinstance(default_prefix, str):
            out_labels = ['{}{}'.format(default_prefix, x) for x in range(length)]
        elif len(default_prefix) == length:
            out_labels = default_prefix
        else:
            raise ValueError('Invalid spec for obtaining {} labels!'.format(type_))

    # forcing them to be strings
    out_labels = [str(lbl) for lbl in out_labels]

    return np.array(strip_all(out_labels), dtype='str')
