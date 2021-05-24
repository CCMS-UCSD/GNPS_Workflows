import unittest
import sys
sys.path.insert(0, "../tools/library_conversion/")
import library_conversion
from library_conversion import InputFormat


class TestLibraryConversion(unittest.TestCase):

    def test_mzvault_convert_msp(self):
        library_conversion.convert(InputFormat.mzvault.name, "data/mzvault_IROA_small.msp", "mzvault_IROA_small.mgf",
                                   "mzvault_IROA_small_batch.tsv", "Robin Test PI", "Robin Test Collector")

    def test_mona_mzmine_msp(self):
        library_conversion.convert(InputFormat.nist_msp.name, "data/MoNA_mzmine_format.msp", "mona_mzmine.mgf",
                                   "mona_mzmine.tsv", "Robin Test PI", "Robin Test Collector")


if __name__ == '__main__':
    unittest.main()