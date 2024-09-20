from gviz import Loader
import gviz.preprocess as pp
from test_common import TEST_FILE_PATH

ldr = Loader(TEST_FILE_PATH)
df = ldr.get_records()
df = pp.execute(df)
print(df.head())
