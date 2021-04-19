import sys
sys.path.insert(0, "../tools/library_conversion/")
import mzvault_conversion as mzvault_convert

def test():
    mzvault_convert.convert("data/IROA_small.msp", "IROA_small.mgf", "IROA_small_batch.tsv")
    