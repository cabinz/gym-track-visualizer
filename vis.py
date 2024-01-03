"""Processes for visualization."""
import pandas as pd
import matplotlib.pyplot as plt

from common import *
import analysis as anlys


def draw(df, ax, title, draw_skip_days=False, legend_outside=False):
    """Draw the training history chart on a given axis.

    The chart is a double-axis figure presenting both the capacity each day in bars,
    and best set weight each day in line."""
    if df.size < 1:
        ax.set_title(title.title())
        return ax.get_figure()

    df = df.reset_index()
    x = df[COL_DATE] if draw_skip_days else df.index

    ax_left = ax
    ax_right = ax.twinx()

    draw_bar_new(x, df, ax_left)
    draw_plot(x, df, ax_right)  # Plot after bar to draw the line plot on the top.

    # Horizontal (X-)axis
    if draw_skip_days:
        ax.set_xticks(df[COL_DATE])
    else:
        ax.set_xticks(x, df[COL_DATE])
    ax.set_xticklabels(df[COL_DATE].dt.strftime('%Y-%m-%d'), rotation=90)

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
    ax.bar(x, df[COL_TOT_CAPACITY], color=base_color, label='Total Capacity', alpha=0.25)
    ax.bar(x, df[COL_PASS_SET_CAP], color=base_color, label='Completed Set Capacity', alpha=0.5)
    ax.bar(x, df[COL_FULL_SET_CAP], color=base_color, label='Full Set Capacity')
    ax.set_ylabel(r'Capacity (kg$\cdot$reps)')

    return ax.get_figure()


def draw_bar_new(x, df, ax):
    """Here, capacity are accumulated regardless of the completion of each set.

    The darkest bars accumulate capacity of sets with weights >= COL_MAX_SET_W.
    The lightest bars accumulate capacity of sets with weights <= COL_MIN_SET_W.
    """
    # TODO: Add grey background bars of the max possible capacity under each max pass set weight.
    df = anlys.update_weight_boundaries(df)

    # Draw the stacked bar chart
    base_color = 'dodgerblue'  # 'skyblue'
    for i, row in df.iterrows():
        bottom = 0  # Initialize the bottom of the stack
        max_weight = row[COL_MAX_PASS_W]

        mapping = {max_weight: [0, 1.0]}  # weight -> [capacity, alpha]
        delta_alpha = 0.75
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
            ax.bar(x[i], c, bottom=bottom, alpha=a, color=base_color)
            bottom += c  # Update the bottom of the stack for the next sub-ba

    ax.bar(x[0], 0, color=base_color, label='Capacity')  # Only for a base color legend

    # Set labels and title
    ax.set_xlabel('Date')
    ax.set_ylabel('Capacity')
    ax.set_title('Stacked Bar Chart of Training Capacities')
