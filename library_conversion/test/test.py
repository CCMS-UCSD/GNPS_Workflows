import sys
sys.path.insert(0, "../tools/library_conversion/")
import library_conversion
from library_conversion import InputFormat

def test():
    library_conversion.convert(InputFormat.mzvault.name, "data/IROA_small.msp", "IROA_small.mgf",
                               "IROA_small_batch.tsv", "Robin Test PI", "Robin Test Collector")
