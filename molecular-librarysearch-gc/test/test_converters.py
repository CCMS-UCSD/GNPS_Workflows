import unittest
import sys
import filecmp
sys.path.insert(0, "../tools/tools/molecularsearch-gc/")
sys.path.insert(0, "tools/tools/molecularsearch-gc/")
import msdial_formatter_gc
import os


def test_msdial():
    os.makedirs("test_output", exist_ok=True)
    msdial_formatter_gc.convert_to_feature_csv("reference_data/msdial/input/Area_table_0_2020312104.txt", "test_output/Area_table_0_2020312104.tsv")
    msdial_formatter_gc.format_mgf("reference_data/msdial/input/HE-try-1_MS-DIAL.mgf", "test_output/HE-try-1_MS-DIAL.mgf")

    assert(filecmp.cmp("test_output/Area_table_0_2020312104.tsv", "reference_data/msdial/output/Area_table_0_2020312104_converted.txt", shallow=False) is True)
    assert(filecmp.cmp("test_output/HE-try-1_MS-DIAL.mgf", "reference_data/msdial/output/HE-try-1_MS-DIAL_prepared.mgf", shallow=False) is True)
