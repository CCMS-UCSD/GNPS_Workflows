import unittest
import sys
import filecmp
sys.path.insert(0, "../tools/feature-based-molecular-networking/scripts/")
import msdial_formatter
import progenesis_formatter
import metaboscape_formatter
import xcms_formatter
import mzmine2_formatter
import openms_formatter

class TestLoaders(unittest.TestCase):

    def test_msdial(self):
        msdial_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/MS-DIAL/MS-DIAL-GNPS_AG_test_featuretable.txt", \
            "./msdial_output.csv")

        self.assertTrue(filecmp.cmp("./msdial_output.csv", "./reference_input_file_for_formatter/MS-DIAL/reference_output_file.csv", shallow=False))

    def test_progenesis(self):
        progenesis_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/Progensis_MSE/SONAR_20_Yeast_Peaks.csv", \
            "./progenesis_output.csv")

    def test_metaboscape(self):
        metaboscape_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/metaboscape/quantification_table-00000.csv", \
            "./metaboscape_output.csv")

    def test_mzmine2(self):
        mzmine2_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/mzmine2/MZmine-GNPS_AG_test_featuretable.csv", \
            "./mzmine_output.csv")
        
    def test_openms(self):
        openms_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/openms/textexporter-00000.csv", \
            "./openms_output.csv")
    
    def test_xcms3(self):
        xcms_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/xcms3/XCMS3-GNPS_AG_test_featuretable.txt", \
            "./xcms3_output.csv")


if __name__ == '__main__':
    unittest.main()