def set_labels(ax_h, axis,
               ticks, labels,
               metric=(), func=None,
               rotation=0,
               **kwargs):
    """
    Helper to show only a subset of labels that meet a specified criteria.

    Examples include frequency of missingness above a given threshold (say 5%).

    kwargs can include any settable property for labels and ticks.

    """

    if len(axis) != 1 and axis not in ('x', 'y'):
        raise ValueError('Axis must be single lowercase character x or y!')

    if len(ticks) != len(labels):
        raise ValueError('ticks, labels and metric must all be of the same length')

    if func is not None and not callable(func):
        raise TypeError('Func must be callable, if not None.')

    if len(labels) > 0:
        if func is not None and len(metric)==len(labels):
            t_n_l = [(tk, lbl) for tk, lbl, val in zip(ticks, labels, metric) if func(val)]
            ticks, labels = list(zip(*t_n_l))

    if axis == 'x':
        ax_h.set(xticks=ticks, **kwargs)
        ax_h.set_xticklabels(labels, rotation=rotation)
    else:
        ax_h.set(yticks=ticks, **kwargs)
        ax_h.set_yticklabels(labels, rotation=rotation)

    return ax_h


def remove_ticks_labels(ax_h, axis):
    """Removes ticks and labels for a specified axis within a Axis object ax_h."""

    if len(axis) != 1 and axis not in ('x', 'y'):
        raise ValueError('Axis must be single lowercase character x or y!')

    set_labels(ax_h, axis, [], [])


def check_freq_thresh_labels(freq_thresh_show_labels):

    if not (0.0 <= freq_thresh_show_labels < 1.0):
        raise ValueError('freq_thresh_show_labels must be >=0 and < 1.0')
    if freq_thresh_show_labels > 0.0:
        def label_filter(freq):
            return freq > freq_thresh_show_labels
    else:
        def label_filter(freq):
            return True

    return label_filter
