from test_common import TEST_FILE_PATH
from gviz import Loader


ldr = Loader(TEST_FILE_PATH)
df = ldr.get_records()
print(df.head())
