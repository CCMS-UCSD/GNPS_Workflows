import unittest
import sys
import filecmp
sys.path.insert(0, "../tools/feature-based-molecular-networking/scripts/")
sys.path.insert(0, "tools/feature-based-molecular-networking/scripts/")
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

        self.assertTrue(filecmp.cmp("./msdial_output.csv", "./reference_input_file_for_formatter/MS-DIAL/MS-DIAL-GNPS_AG_test_featuretable_reference_output_file.csv", shallow=False))

    def test_msdial_ims(self):
        msdial_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/MS-DIAL/GnpsTable_1_20198191357_PASEF.txt", \
            "./msdial_ims_output.csv")

        self.assertTrue(filecmp.cmp("./msdial_ims_output.csv", "./reference_input_file_for_formatter/MS-DIAL/GnpsTable_1_20198191357_PASEF_output.csv", shallow=False))

    def test_progenesis(self):
        ## SONAR MSE
        compound_to_scan_mapping = progenesis_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/Progenesis/SONAR_20_Yeast_Peaks_output.csv", \
            "./progenesis_MSE_output.csv")

        self.assertTrue(filecmp.cmp("./progenesis_MSE_output.csv", "./reference_input_file_for_formatter/Progenesis/SONAR_20_Yeast_Peaks_output.csv", shallow=False))

        progenesis_formatter.convert_mgf("./reference_input_file_for_formatter/Progenesis/SONAR_20_Yeast_MSMS.msp", "progenesis_MSE_output.mgf", compound_to_scan_mapping)

        self.assertTrue(filecmp.cmp("./progenesis_MSE_output.mgf", "./reference_input_file_for_formatter/Progenesis/SONAR_20_Yeast_MSMS.msp", shallow=False))

        ## CATECHIN MSE
        compound_to_scan_mapping = progenesis_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/Progenesis/Neg_MSE_Catechin.csv", \
            "./progenesis_MSE_output_catechin.csv")

        self.assertTrue(filecmp.cmp("./progenesis_MSE_output_catechin.csv", "./reference_input_file_for_formatter/Progenesis/Neg_MSE_Catechin_output.csv", shallow=False))

        progenesis_formatter.convert_mgf("./reference_input_file_for_formatter/Progenesis/Neg_MSE_Catechin.msp", "progenesis_MSE_output_catechin.mgf", compound_to_scan_mapping)

        self.assertTrue(filecmp.cmp("./progenesis_MSE_output_catechin.mgf", "./reference_input_file_for_formatter/Progenesis/Neg_MSE_Catechin.msp", shallow=False))

        ## IMS
        compound_to_scan_mapping = progenesis_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/Progenesis/161118_pos_IMS.csv", \
            "./progenesis_IMS_output.csv")

        self.assertTrue(filecmp.cmp("./progenesis_IMS_output.csv", "./reference_input_file_for_formatter/Progenesis/161118_pos_IMS_output.csv", shallow=False))

        progenesis_formatter.convert_mgf("./reference_input_file_for_formatter/Progenesis/161118_pos_IMS.msp", "progenesis_output_IMS.mgf", compound_to_scan_mapping)

        self.assertTrue(filecmp.cmp("./progenesis_output_IMS.mgf", "./reference_input_file_for_formatter/Progenesis/161118_pos_IMS.msp", shallow=False))


    def test_metaboscape(self):
        metaboscape_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/MetaboScape/Lipids.msmsonly.csv", \
            "./metaboscape_output.csv")

        metaboscape_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/MetaboScape/Lipids.msmsonly.csv", \
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

    def test_xcms3_iin(self):
        xcms_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/xcms3/camera_iin_quant_table_sub.txt", \
            "./xcms3_output_iin.csv")


if __name__ == '__main__':
    unittest.main()
