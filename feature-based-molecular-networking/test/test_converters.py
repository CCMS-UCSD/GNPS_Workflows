import unittest
import sys
import filecmp
sys.path.insert(0, "../tools/feature-based-molecular-networking/scripts/")
sys.path.insert(0, "tools/feature-based-molecular-networking/scripts/")
import msdial_formatter
import progenesis_formatter
import metaboscape_formatter
import xcms_formatter
import mzmine_formatter
import openms_formatter
import agilent_formatter

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
        compound_to_scan_mapping = progenesis_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/Progenesis/SONAR_20_Yeast_Peaks.txt", \
            "./progenesis_MSE_output.csv")

        self.assertTrue(filecmp.cmp("./progenesis_MSE_output.csv", "./reference_input_file_for_formatter/Progenesis/SONAR_20_Yeast_Peaks_output.csv", shallow=False))

        progenesis_formatter.convert_mgf("./reference_input_file_for_formatter/Progenesis/SONAR_20_Yeast_MSMS.msp", "SONAR_20_Yeast_MSMS.mgf", compound_to_scan_mapping)

        self.assertTrue(filecmp.cmp("./SONAR_20_Yeast_MSMS.mgf", "./reference_input_file_for_formatter/Progenesis/SONAR_20_Yeast_MSMS.mgf", shallow=False))

        ## CATECHIN MSE
        compound_to_scan_mapping = progenesis_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/Progenesis/Neg_MSE_Catechin.txt", "./Neg_MSE_Catechin_output.csv")

        self.assertTrue(filecmp.cmp("./Neg_MSE_Catechin_output.csv", "./reference_input_file_for_formatter/Progenesis/Neg_MSE_Catechin_output.csv", shallow=False))

        progenesis_formatter.convert_mgf("./reference_input_file_for_formatter/Progenesis/Neg_MSE_Catechin.msp", "Neg_MSE_Catechin.mgf", compound_to_scan_mapping)

        self.assertTrue(filecmp.cmp("./Neg_MSE_Catechin.mgf", "./reference_input_file_for_formatter/Progenesis/Neg_MSE_Catechin.mgf", shallow=False))

        ## IMS
        compound_to_scan_mapping = progenesis_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/Progenesis/161118_pos_IMS.txt", \
            "./progenesis_IMS_output.csv")

        self.assertTrue(filecmp.cmp("./progenesis_IMS_output.csv", "./reference_input_file_for_formatter/Progenesis/161118_pos_IMS_output.csv", shallow=False))

        progenesis_formatter.convert_mgf("./reference_input_file_for_formatter/Progenesis/161118_pos_IMS.msp", "161118_pos_IMS.mgf", compound_to_scan_mapping)

        self.assertTrue(filecmp.cmp("./161118_pos_IMS.mgf", "./reference_input_file_for_formatter/Progenesis/161118_pos_IMS.mgf", shallow=False))

        #More input
        compound_to_scan_mapping = progenesis_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/Progenesis/202005_IMS_w_tags.txt", \
                    "./progenesis_IMS_output.csv")

        self.assertTrue(filecmp.cmp("./progenesis_IMS_output.csv", "./reference_input_file_for_formatter/Progenesis/202005_IMS_w_tags_output.csv", shallow=False))

        progenesis_formatter.convert_mgf("./reference_input_file_for_formatter/Progenesis/202005_IMS_w_tags.msp", "202005_IMS_w_tags.mgf", compound_to_scan_mapping)

        self.assertTrue(filecmp.cmp("./202005_IMS_w_tags.mgf", "./reference_input_file_for_formatter/Progenesis/202005_IMS_w_tags.mgf", shallow=False))

    #Making sure this raises exception

    def test_metaboscape(self):
        metaboscape_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/MetaboScape/Lipids.msmsonly.csv", \
            "./metaboscape_output.csv")

        metaboscape_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/MetaboScape/SRM1950 Lipidomics.msmsonly.csv", \
            "./metaboscape_output2.csv")

    def test_mzmine2(self):
        mzmine_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/mzmine2/MZmine-GNPS_AG_test_featuretable.csv", \
            "./mzmine_output.csv")

        self.assertTrue(filecmp.cmp("./mzmine_output.csv", "./reference_input_file_for_formatter/mzmine2/MZmine-GNPS_AG_test_featuretable_output.csv", shallow=False))

    def test_mzmine3(self):
        mzmine_formatter.convert_to_feature_csv(
            "./reference_input_file_for_formatter/mzmine3/mzmine3_full.csv", "./mzmine3_output.csv")

        self.assertTrue(filecmp.cmp("./mzmine3_output.csv",
                                    "./reference_input_file_for_formatter/mzmine3/mzmine3_full_output.csv", shallow=False))

    def test_openms(self):
        openms_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/openms/textexporter-00000.csv", \
            "./openms_output.csv")

    def test_openms_iimn(self):
        openms_formatter.convert_to_feature_csv(
            "./reference_input_file_for_formatter/openms/openms_iimn.txt", \
            "./openms_iimn_output.txt")

        self.assertTrue(filecmp.cmp("./openms_iimn_output.txt",
                                    "./reference_input_file_for_formatter/openms/openms_iimn_output.txt",
                                    shallow=False))

    def test_xcms3(self):
        xcms_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/xcms3/XCMS3-GNPS_AG_test_featuretable.txt", \
            "./xcms3_output.csv")

    def test_xcms3_iin(self):
        xcms_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/xcms3/camera_iin_quant_table_sub.txt", \
            "./xcms3_output_iin.csv")

    def test_agilent(self):
        agilent_formatter.convert_to_feature_csv("./reference_input_file_for_formatter/agilent/agilent_test.csv", \
            "./agilent_output.csv")


if __name__ == '__main__':
    tester = TestLoaders()
    tester.test_agilent()
    #unittest.main()
