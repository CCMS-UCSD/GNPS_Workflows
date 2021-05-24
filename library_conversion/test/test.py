import unittest
import sys

sys.path.insert(0, "../tools/library_conversion/")
import library_conversion
from library_conversion import InputFormat


class TestLibraryConversion(unittest.TestCase):

    def test_mzvault_convert_msp(self):
        library_conversion.convert(InputFormat.mzvault.name, "data/mzvault_IROA_small.msp",
                                   "tmp/mzvault_IROA_small.mgf", "tmp/mzvault_IROA_small_batch.tsv", "Robin Test PI",
                                   "Robin Test Collector")

    def test_mona_mzmine_msp(self):
        library_conversion.convert(InputFormat.nist_msp.name, "data/MoNA_mzmine_format.msp", "tmp/mona_mzmine.mgf",
                                   "tmp/mona_mzmine.tsv", "Robin Test PI", "Robin Test Collector")

    def test_mzmine_json(self):
        library_conversion.convert(InputFormat.mzmine_json.name, "data/mzmine.json", "tmp/mzmine_json.mgf",
                                   "tmp/mzmine_json.tsv", "Robin Test PI", "Robin Test Collector")

    def test_exception_on_wrong_input_format(self):
        print("Test exception for MZmine .json (json lines) library in other converters:")
        self.assertRaises(Exception, library_conversion.convert, InputFormat.mzvault.name, "data/mzmine.json",
                          "tmp/mzmine_json_wrong.mgf", "tmp/mzmine_json_wrong.tsv", "Robin Test PI",
                          "Robin Test Collector")

        self.assertRaises(Exception, library_conversion.convert, InputFormat.nist_msp.name, "data/mzmine.json",
                          "tmp/mzmine_json_wrong.mgf", "tmp/mzmine_json_wrong.tsv", "Robin Test PI",
                          "Robin Test Collector")

        print("Test exception for MZvault .msp in other converters:")
        self.assertRaises(Exception, library_conversion.convert, InputFormat.nist_msp.name,
                          "data/mzvault_IROA_small.msp", "tmp/wrong.mgf", "tmp/wrong.tsv", "Robin Test PI",
                          "Robin Test Collector")

        self.assertRaises(Exception, library_conversion.convert, InputFormat.mzmine_json.name,
                          "data/mzvault_IROA_small.msp", "tmp/wr.mgf", "tmp/wr.tsv", "Robin Test PI",
                          "Robin Test Collector")

        print("Test exception for NIST compatible .msp in other converters:")
        self.assertRaises(Exception, library_conversion.convert, InputFormat.mzvault.name,
                          "data/MoNA_mzmine_format.msp", "tmp/wr.mgf", "tmp/wr.tsv", "Robin Test PI",
                          "Robin Test Collector")

        self.assertRaises(Exception, library_conversion.convert, InputFormat.mzmine_json.name,
                          "data/MoNA_mzmine_format.msp", "tmp/wr.mgf", "tmp/wr.tsv", "Robin Test PI",
                          "Robin Test Collector")

    def test_exception_on_empty_input_file(self):
        self.assertRaises(Exception, library_conversion.convert, InputFormat.mzvault.name, "data/empty.msp",
                          "tmp/wrong_empty.mgf", "tmp/wrong_empty.tsv", "Robin Test PI", "Robin Test Collector")

        self.assertRaises(Exception, library_conversion.convert, InputFormat.nist_msp.name, "data/empty.msp",
                          "tmp/wrong_empty.mgf", "tmp/wrong_empty.tsv", "Robin Test PI", "Robin Test Collector")

        self.assertRaises(Exception, library_conversion.convert, InputFormat.mzmine_json.name, "data/empty.msp",
                          "tmp/wrong_empty.mgf", "tmp/wrong_empty.tsv", "Robin Test PI", "Robin Test Collector")

if __name__ == '__main__':
    unittest.main()
