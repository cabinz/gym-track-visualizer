"""Processes for visualization."""
import pandas as pd
import matplotlib.pyplot as plt

from common import *
import analysis as anlys


def draw(df, ax, title, draw_skip_days=False):
    """Draw the training history chart on a given axis.

    The chart is a double-axis figure presenting both the capacity each day in bars,
    and best set weight each day in line."""
    if df.size < 1:
        ax.set_title(title.title())
        return ax.get_figure()

    df = df.reset_index()
    x = df[COL_DATE] if draw_skip_days else df.index

    # Plot the bar chart on the primary axis
    base_color = 'dodgerblue'  # 'skyblue'
    ax.bar(x, df[COL_TOT_CAPACITY], color=base_color, label='Total Capacity', alpha=0.25)
    ax.bar(x, df[COL_COMPLETED_SET_CAPACITY], color=base_color, label='Completed Set Capacity', alpha=0.5)
    ax.bar(x, df[COL_FULL_SET_CAPACITY], color=base_color, label='Full Set Capacity')
    ax.set_ylabel(r'Capacity (kg$\cdot$reps)')

    # Create a secondary axis for the line plot
    ax2 = ax.twinx()
    # Plot the line plot on the secondary axis
    ax2.plot(x, df[COL_MAX_SET], color='salmon', marker='o', label='Best Set Weight')
    ax2.set_ylabel(r'Weight (kg)')

    # Horizontal (X-)axis
    if draw_skip_days:
        ax.set_xticks(df[COL_DATE])
    else:
        ax.set_xticks(x, df[COL_DATE])
    ax.set_xticklabels(df[COL_DATE].dt.strftime('%Y-%m-%d'), rotation=90)

    # Add a legend for both plots
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    cmb_labels = labels + labels2

    ax.legend(lines + lines2, cmb_labels, ncol=len(cmb_labels),
              # `bbox_to_anchor` bounding box (x0, y0, width, height) default as (0, 0, 1, 1)
              # `loc` specifies the location of legends in the bonding box
              # `expand` mode makes legends horizontally filled up the bounding box
              bbox_to_anchor=(0, 1.02, 1, 0.2), loc='lower left', mode='expand')
    ax.set_title(title.title(), y=1.2)

    return ax.get_figure()