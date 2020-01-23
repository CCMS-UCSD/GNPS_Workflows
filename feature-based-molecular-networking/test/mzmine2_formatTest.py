#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest 
import sys
sys.path.insert(1,'../tools/feature-based-molecular-networking/scripts/')
from mzmine2_formatter import validate_mzmine_output_file

class ValidatorTests(unittest.TestCase):
    def test_Correct(self):
        validate_mzmine_output_file('reference_input_file_for_formatter/mzmine2/MZmine-GNPS_AG_test_featuretable.csv')
        
    @unittest.expectedFailure
    def test_Column(self):            
        validate_mzmine_output_file('reference_input_file_for_formatter/mzmine2/rowMZ_only.csv')    

    @unittest.expectedFailure
    def test_Delimeter(self):
        validate_mzmine_output_file('reference_input_file_for_formatter/mzmine2/incorrectDelim.csv')
