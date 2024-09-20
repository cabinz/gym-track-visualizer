import gviz
from gviz import Loader
from test_common import TEST_FILE_PATH, TEST_OUT_DIR

import matplotlib.pyplot as plt

ldr = Loader(TEST_FILE_PATH)
df = ldr.get_records()

item_name = 'seated shoulder press'
groups = df.groupby(gviz.COL_ITEM_NAME)
item_df = groups.get_group(item_name)

fig, ax = plt.subplots(figsize=(12, 6))
fig = gviz.draw(
    item_df, ax, item_name,
    draw_skip_days=False,
    xtick_label_mode='dsparse',
    xtick_rotation=35,
    legend_outside=False,
    bar_width=0.8,
    plot_marker='.',
)
fig.tight_layout()
# plt.show()

dump_path = TEST_OUT_DIR / 'test_vis.png'
fig.savefig(dump_path)
print(f"Dumped to {dump_path}")
