"""Processes for visualization."""
import pandas as pd
import matplotlib.pyplot as plt

from common import *
import analysis as anlys


def draw(df, ax, title,
         draw_skip_days=False, xtick_rotation=35,
         legend_outside=False, bar_width=0.8, draw_order=False):
    """Draw the training history chart on a given axis.

    The chart is a double-axis figure presenting both the capacity each day in bars,
    and best set weight each day in line."""
    if df.size < 1:
        ax.set_title(title.title())
        return ax.get_figure()

    df = df.sort_values(by=COL_DATE, ascending=True).reset_index()
    x = df[COL_DATE] if draw_skip_days else df.index

    ax_left = ax
    ax_right = ax.twinx()  # The twin ax will be drawn after (atop) the original one.

    draw_plot(x, df, ax_right)
    draw_bar_new(x, df, ax_left, bar_width=bar_width, draw_order=draw_order)

    # Horizontal (X-)axis
    if draw_skip_days:
        ax.set_xticks(df[COL_DATE])
    else:
        ax.set_xticks(x, df[COL_DATE])
    ax.set_xticklabels(df[COL_DATE].dt.strftime('%Y-%m-%d'), rotation=xtick_rotation)

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
        # Title
        ax.set_title(title.title(), y=1.2)
    else:
        ax.legend(lines1 + lines2, cmb_labels, ncol=len(cmb_labels), loc='upper left')
        # Title
        ax.set_title(title.title())

    return ax.get_figure()


def draw_plot(x, df, ax):
    df = anlys.update_weight_boundaries(df)

    ax.plot(x, df[COL_MAX_PASS_W], color='salmon', marker='o', label='Best Set Weight')
    ax.set_ylabel(r'Weight (kg)')

    return ax.get_figure()


def draw_bar(x, df, ax):
    df = anlys.update_capacity(df)

    base_color = 'dodgerblue'  # 'skyblue'
    ax.bar(x, df[COL_TOT_CAP], color=base_color, label='Total Capacity', alpha=0.25)
    ax.bar(x, df[COL_PASS_SET_CAP], color=base_color, label='Completed Set Capacity', alpha=0.5)
    ax.bar(x, df[COL_FULL_SET_CAP], color=base_color, label='Full Set Capacity')
    ax.set_ylabel(r'Capacity (kg$\cdot$reps)')

    return ax.get_figure()


def draw_bar_new(x, df, ax, bar_width=0.8, draw_order=False):
    """Here, capacity are accumulated regardless of the completion of each set.

    The darkest bars accumulate capacity of sets with weights >= COL_MAX_SET_W.
    The lightest bars accumulate capacity of sets with weights <= COL_MIN_SET_W.
    """
    df = anlys.update_weight_boundaries(df)

    # Background bars (target capacity)
    bg_color, bg_alpha = 'grey', 0.15
    ax.bar(x, df[COL_TGT_CAP], color=bg_color, alpha=bg_alpha, label='Target Capacity', width=bar_width)

    # Stacked bar (actual capacity)
    base_color = 'dodgerblue'  # 'skyblue'
    for i, row in df.iterrows():
        max_weight = row[COL_MAX_PASS_W]

        # Stacked bar
        bottom = 0  # Initialize the bottom of the stack
        mapping = {max_weight: [0, 1.0]}  # weight -> [capacity, alpha]
        delta_alpha = 0.6
        delta_weight = row[COL_MAX_PASS_W] - row[COL_MIN_PASS_W]
        for weight_col, reps_col in valid_set_cols():
            weight, reps = row[weight_col], row[reps_col]
            if pd.isnull(weight) or pd.isnull(reps):
                continue
            capacity = weight * reps
            if weight < max_weight:
                if weight not in mapping:
                    # min() is needed because weight can be smaller than row[COL_MIN_SET_W]
                    # since COL_MIN_SET_W consider only the complete set
                    # i.e. the lightest bars accumulate capacity of all sets with weight <= row[COL_MIN_SET_W]
                    dist_to_max = min(max_weight - weight, delta_weight)
                    alpha = 1 - delta_alpha * (dist_to_max / delta_weight)
                    mapping[weight] = [0, alpha]
                mapping[weight][0] += capacity
            else:
                # This branch covers all records of weight >= max_weight
                # (including those incomplete set with weight larger than row[COL_MAX_SET_W])
                # i.e. the darkest bars cover accumulate of all sets with weight >= row[COL_MAX_SET_W]
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
    ax.set_xlabel('Date')
    ax.set_ylabel(r'Capacity (kg$\cdot$reps)')
