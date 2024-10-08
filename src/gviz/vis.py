"""Processes for visualization."""
import math
import pandas as pd
import matplotlib.pyplot as plt

from .common import *
from .preprocess import META_COLS
from . import preprocess as pp


def draw(df, ax, title,
         draw_skip_days=False, xtick_label_mode='dsparse', xtick_rotation=35,
         legend_outside=True, bar_width=0.8, draw_order=False,
         plot_marker='.'):
    """
    Draw the training history chart on a given axis.

    The chart is a double-axis figure presenting both the capacity each day in bars,
    and best set weight each day in line.

    Args:
        df: The dataframe
        ax: The plt axis to draw on
        title: Figure title
        draw_skip_days: If to leave blank for skipped days between workout days
        xtick_label_mode: 'd', 'dsparse', 'mo', 'yr', or 'moyr'
        xtick_rotation:  For xtick rotation
        legend_outside: If to draw legend out of the box
        bar_width: From range of [0, 1.0]
        draw_order: If to draw the set order in each workout day

    Returns:
        The figure.
    """
    if df.size < 1:
        ax.set_title(title.title())
        return ax.get_figure()

    df = df.sort_values(by=COL_DATE, ascending=True).reset_index()
    x = df[COL_DATE] if draw_skip_days else df.index
    xtick_labels = _get_xtick_labels(df[COL_DATE], mode=xtick_label_mode)

    ax_left = ax
    ax_right = ax.twinx()  # The twin ax will be drawn after (atop) the original one.

    # Draw the bars and plots.
    draw_plot(x, df, ax_right, marker=plot_marker)
    draw_bar_new(x, df, ax_left, bar_width=bar_width, draw_order=draw_order)

    # Draw X-axis tick labels.
    if draw_skip_days:
        ax.set_xticks(df[COL_DATE], xtick_labels, rotation=xtick_rotation)
    else:
        ax.set_xticks(x, xtick_labels, rotation=xtick_rotation)
        # ax.set_xticklabels(xtick_labels, rotation=xtick_rotation) can be used as well.

    # Add legends for both plots
    lines1, labels1 = ax_left.get_legend_handles_labels()
    lines2, labels2 = ax_right.get_legend_handles_labels()
    cmb_labels = labels1 + labels2
    if legend_outside:
        ax.legend(lines1 + lines2, cmb_labels, ncol=len(cmb_labels),
                  # `bbox_to_anchor` bounding box (x0, y0, width, height) default as (0, 0, 1, 1)
                  # `loc` specifies the location of legends in the bonding box
                  # `expand` mode makes legends horizontally filled up the bounding box
                  bbox_to_anchor=(0, 1.02, 1, 0.2), loc='lower left',
                  # mode='expand',
                  )
        ax.set_title(title.title(), y=1.2)
        # TODO: The title is not properly displayed without using fig.tight_layout()
    else:
        ax.legend(lines1 + lines2, cmb_labels, ncol=len(cmb_labels), loc='upper left')
        ax.set_title(title.title())

    return ax.get_figure()


def _get_xtick_labels(date_series, mode='date'):
    if mode not in ('d', 'dsparse', 'mo', 'yr', 'moyr'):
        raise ValueError(f'Unknown xtick_labels mode: {mode}')

    if mode == 'd' or (mode == 'dsparse' and len(date_series) < 10):
        return date_series.dt.strftime('%Y-%m-%d')
    
    xtick_lbls = []
    if mode == 'dsparse':
        # Show 10 xticks at most, ensuring the first and last dates are shown.
        interval = math.ceil(len(date_series) / 10)
        half_interval = interval // 2
        for i, date in enumerate(date_series):
            if i == 0  or i == len(date_series) - 1 or (
                i % interval == 0 and i + half_interval < len(date_series)
            ):
                xtick_lbls.append(date.strftime('%Y-%m-%d'))
            else:
                xtick_lbls.append('')
    if mode == 'yr':
        prev = -1
        for date in date_series:
            cur = date.year
            if cur != prev:
                prev = cur
                xtick_lbls.append(date.strftime('%Y'))
            else:
                xtick_lbls.append('')
    elif mode == 'mo':
        prev = -1
        for date in date_series:
            cur = date.month
            if cur != prev:
                prev = cur
                xtick_lbls.append(date.strftime('%b'))
            else:
                xtick_lbls.append('')
    elif mode == 'moyr':
        prev_mo, prev_yr = -1, -1
        for date in date_series:
            cur_mo, cur_yr = date.month, date.year
            lbl = ''
            # This block only deals with month, year is handle after this block
            if cur_mo != prev_mo or cur_yr != prev_yr:
                prev_mo = cur_mo
                lbl += date.strftime('%b')
            # Deal with year
            if cur_yr != prev_yr:
                prev_yr = cur_yr
                lbl += f'\n{date.strftime("%Y")}'
            xtick_lbls.append(lbl)
    return xtick_lbls


def draw_plot(x, df, ax, marker=None):
    df = pp.update_weight_boundaries(df)

    ax.plot(x, df[META_COLS.MAX_PASS_W], color='salmon', marker=marker, label='Best Set Weight')
    ax.set_ylabel(r'Weight (kg)')

    return ax.get_figure()


def draw_bar(x, df, ax):
    df = pp.update_capacity(df)

    base_color = 'dodgerblue'  # 'skyblue'
    ax.bar(x, df[META_COLS.TOT_CAP], color=base_color, label='Total Capacity', alpha=0.25)
    ax.bar(x, df[META_COLS.SUCC_SET_CAP], color=base_color, label='Successful Set Capacity', alpha=0.5)
    ax.bar(x, df[META_COLS.FULL_SET_CAP], color=base_color, label='Full Set Capacity')
    ax.set_ylabel(r'Capacity (kg$\cdot$reps)')

    return ax.get_figure()


def draw_bar_new(x, df, ax, bar_width=0.8, draw_order=False):
    """Here, capacity are accumulated regardless of the completion of each set.

    The darkest bars accumulate capacity of sets with weights >= COL_MAX_SET_W.
    The lightest bars accumulate capacity of sets with weights <= COL_MIN_SET_W.
    """
    df = pp.update_weight_boundaries(df)

    # Background bars (target capacity)
    bg_color, bg_alpha = 'grey', 0.15
    ax.bar(x, df[META_COLS.TGT_CAP], color=bg_color, alpha=bg_alpha, label='Target Capacity', width=bar_width)

    # Stacked bar (actual capacity)
    base_color = 'dodgerblue'  # 'skyblue'
    for i, row in df.iterrows():
        max_weight = row[META_COLS.MAX_PASS_W]

        # Stacked bar
        bottom = 0  # Initialize the bottom of the stack
        mapping = {max_weight: [0, 1.0]}  # weight -> [capacity, alpha]
        delta_alpha = 0.6
        delta_weight = row[META_COLS.MAX_PASS_W] - row[META_COLS.MIN_PASS_W]
        for weight_col, reps_col in valid_set_cols():
            weight, reps = row[weight_col], row[reps_col]
            if pd.isnull(weight) or pd.isnull(reps):
                continue
            capacity = weight * reps
            if weight < max_weight:
                if weight not in mapping:
                    # min() is needed because weight can be smaller than row[MIN_SET_W]
                    # since MIN_SET_W consider only the complete set
                    # i.e. the lightest bars accumulate capacity of all sets with weight <= row[MIN_SET_W]
                    dist_to_max = min(max_weight - weight, delta_weight)
                    alpha = 1 - delta_alpha * (dist_to_max / delta_weight)
                    mapping[weight] = [0, alpha]
                mapping[weight][0] += capacity
            else:
                # This branch covers all records of weight >= max_weight
                # (including those incomplete set with weight larger than row[MAX_SET_W])
                # i.e. the darkest bars cover accumulate of all sets with weight >= row[MAX_SET_W]
                mapping[max_weight][0] += capacity

        def sort_by_decr_2nd_elem(lt):
            return sorted(lt, key=lambda sub_lt: sub_lt[1], reverse=True)

        for c, a in sort_by_decr_2nd_elem(mapping.values()):
            ax.bar(x[i], c, bottom=bottom, alpha=a, color=base_color, width=bar_width)
            bottom += c  # Update the bottom of the stack for the next sub-bar

        # Draw the order at the bottom of the bar.
        if draw_order and not pd.isnull(row[COL_ORDER]):
            def num_to_order(num):
                num = int(num)
                if num % 10 == 1 and num != 11:
                    return rf'${num}^{{st}}$'
                elif num % 10 == 2 and num != 12:
                    return rf'${num}^{{nd}}$'
                elif num % 10 == 3 and num != 13:
                    return rf'${num}^{{rd}}$'
                else:
                    return rf'${num}^{{th}}$'

            ax.text(x[i], 0, num_to_order(row[COL_ORDER]), ha='center', va='bottom')

    ax.bar(x[0], 0, color=base_color, label='Actual Capacity', width=bar_width)  # Only for a legend
    # ax.set_xlabel('Date')
    ax.set_ylabel(r'Capacity (kg$\cdot$reps)')
