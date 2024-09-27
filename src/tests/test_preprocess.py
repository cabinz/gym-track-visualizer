from gviz import Loader
import gviz.preprocess as pp
from gviz.preprocess import PreprocessConfig
from test_common import TEST_FILE_PATH

config = PreprocessConfig(
    MIN_SET_REPS=5,
    FULL_SET_REPS=5,
    SET_ID_RANGE_L=1,
    SET_ID_RANGE_R=5
)

ldr = Loader(TEST_FILE_PATH)
df = ldr.get_records()
df = pp.execute(df, config)
print(df.head())

print(df[df["name"] == "bench press"].head())
