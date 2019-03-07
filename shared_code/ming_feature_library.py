#!/usr/bin/python

import ming_fileio_library

class ConsensusFeature:
    def __init__(self, featureid, file_feature_maps):
        self.featureid = featureid
        self.file_feature_maps = file_feature_maps #it is a key on filename to a rt, mz, and intensity

    def __str__(self):
        output_string = self.featureid + "\t"
        for filename in self.file_feature_maps:
            output_string += str(self.file_feature_maps[filename].intensity) + "\t" 
            output_string += str(self.file_feature_maps[filename].mz) + "\t" 
            output_string += str(self.file_feature_maps[filename].rt) + "\t"

        return output_string

    def get_header(self):
        output_string = "FeatureID" + "\t"
        for filename in self.file_feature_maps:
            output_string += str(self.file_feature_maps[filename].filename + "_INT" ) + "\t" 
            output_string += str(self.file_feature_maps[filename].filename + "_MZ") + "\t" 
            output_string += str(self.file_feature_maps[filename].filename + "_RT") + "\t"

        return output_string

    def get_max_intensity(self):
    	max_int = 0
    	for filename in self.file_feature_maps:
    		max_int = max(self.file_feature_maps[filename].intensity, max_int)
		return max_int

class LC_Feature:
    def __init__(self, filename, mz, rt, intensity):
        self.filename = filename
        self.mz = mz
        self.rt = rt
        self.intensity = intensity


#Returns a list of consensus features 
def parse_input_consensus_feature(tsv_file):
    rows, table_data = ming_fileio_library.parse_table_with_headers(tsv_file)
    headers = table_data.keys()
    print headers

    #Finding all file names
    data_filenames = []
    for header in headers:
        if header.find("_MZ") != -1:
            data_filenames.append(header[:-3])

    consensus_features = []

    for i in range(rows):
        file_feature_map = {}
        for filename in data_filenames:
            intensity_key = filename
            mz_key = filename + "_MZ"
            rt_key = filename + "_RT"

            intensity_value = float(table_data[intensity_key][i])
            mz_value = float(table_data[mz_key][i])
            rt_value = float(table_data[rt_key][i])

            file_feature = LC_Feature(filename, mz_value, rt_value, intensity_value)
            file_feature_map[filename] = file_feature

        consensus_feature = ConsensusFeature(table_data["#FeatureID"][i], file_feature_map)
        consensus_features.append(consensus_feature)
    
    return consensus_features


def max_intensity_consensus_features(consensus_features):
	max_intensity = 0
	for consensus_feature in consensus_features:
		max_intensity = max(max_intensity, consensus_feature.get_max_intensity())

	return max_intensity
