import unittest
import sys
sys.path.insert(0, "../tools/feature-based-molecular-networking/scripts/")
import msdial_formatter
import progenesis_formatter
import metaboscape_formatter

class TestLoaders(unittest.TestCase):

    def test_msdial(self):
        msdial_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/MS-DIAL/MS-DIAL-GNPS_AG_test_featuretable.txt", \
            "./msdial_output.csv")

    def test_progenesis(self):
        progenesis_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/Progensis_MSE/SONAR_20_Yeast_Peaks.csv", \
            "./progenesis_output.csv")

    def test_metaboscape(self):
        metaboscape_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/metaboscape/quantification_table-00000.csv", \
            "./metaboscape_output.csv")


if __name__ == '__main__':
    unittest.main()