#!/usr/bin/python


import sys
import getopt
import os
import math
import ming_spectrum_library
import json
import ming_gnps_library
import spectrum_alignment
import ming_proteosafe_library
import ming_parallel_library
import ming_fileio_library
import trace_to_single_file
from collections import defaultdict

def usage():
    print("<param.xml> <parallel filename> <output matches file>")

PATH_TO_DATASET_UPLOADS = "/data/ccms-data/uploads"


def get_spectrum_collection_from_param_obj(param_obj):
    precursor_mz = float(param_obj["precursor_mz"][0])
    spectrum_string = param_obj["spectrum_string"][0]
    peaks_lines = spectrum_string.split("\n")
    peak_list = []
    for peak_line in peaks_lines:
        splits = peak_line.split()
        mass = float(splits[0])
        intensity = float(splits[1])
        peak_list.append([mass, intensity])

    peak_list = sorted(peak_list, key=lambda peak: peak[0])

    spectrum_obj = ming_spectrum_library.Spectrum("search_spectrum.mgf", 1, 0, peak_list, precursor_mz, 1, 2)
    spectrum_collection = ming_spectrum_library.SpectrumCollection("search_spectrum.mgf")

    spectrum_collection.spectrum_list = [spectrum_obj]

    return spectrum_collection

"""Returns a map of dataset to a list of matches"""
def finding_matches_in_public_data(input_spectrum_collection, all_datasets, match_parameters):
    all_matches_to_datasets_map = {}

    dataset_search_parameters = []
    for dataset in all_datasets:
        if dataset["title"].upper().find("GNPS") == -1:
            continue
        dataset_id = dataset["dataset"]
        dataset_search_parameters.append({"dataset_id" : dataset_id, "input_spectrum_collection" : input_spectrum_collection, "match_parameters" : match_parameters})

    print("datasets to consider: " + str(len(dataset_search_parameters)))

    #Parallel
    search_results = ming_parallel_library.run_parallel_job(find_matches_in_dataset_wrapper, dataset_search_parameters, 50)

    #formatting output
    for i in range(len(search_results)):
        dataset_matches = search_results[i]
        dataset_id = dataset_search_parameters[i]["dataset_id"]
        all_matches_to_datasets_map[dataset_id] = { "matches" : dataset_matches}

    return all_matches_to_datasets_map


def find_matches_in_dataset_wrapper(parameters_dict):
    return find_matches_in_dataset(parameters_dict["dataset_id"], parameters_dict["input_spectrum_collection"], parameters_dict["match_parameters"])


def find_matches_in_dataset(dataset_id, input_spectrum_collection, match_parameters):
    if match_parameters["SEARCH_RAW"]:
        """Finding all data in ccms_peak collection"""
        path_to_ccms_peak = os.path.join("/data/massive/", dataset_id, "ccms_peak")
        #Recursive find file
        all_files = ming_fileio_library.list_all_files_in_directory(path_to_ccms_peak)
        #all_files = all_files[:1]
        print(all_files)

        all_matches = []
        for filename in all_files:
            size_of_file = os.path.getsize(filename)
            if size_of_file > 200 * 1024 * 1024:
                continue
            all_matches += find_matches_in_file(input_spectrum_collection, filename, filename.replace("/data/massive/", ""), match_parameters)

        return all_matches
    else:
        #Searching Clustered
        path_to_clustered_mgf = os.path.join(PATH_TO_DATASET_UPLOADS, "continuous", "clustered_data", dataset_id + "_specs_ms.mgf")
        relative_user_path_to_clustered = os.path.join("continuous", "clustered_data", dataset_id + "_specs_ms.mgf")
        return find_matches_in_file(input_spectrum_collection, path_to_clustered_mgf, relative_user_path_to_clustered, match_parameters, top_k=10000)

def find_matches_in_file(input_spectrum_collection, dataset_filepath, relative_dataset_filepath, match_parameters, top_k=1):
    dataset_match_list = []

    if not ming_fileio_library.is_path_present(dataset_filepath):
        print("Cant find", dataset_filepath)
        return dataset_match_list

    dataset_query_spectra = ming_spectrum_library.SpectrumCollection(dataset_filepath)
    try:
        dataset_query_spectra.load_from_file()
    except:
        return dataset_match_list

    # Parameterizing Analog Search Parameters
    analog_contraint_masses = []
    if match_parameters["ANALOG_CONSTRAINT"] == "BIOTRANSFORMATIONS":
        parsed_anntation_list = "0.50097:z = 2|1.00335:isotope_13C|1.9958:isotope_34S|1.99704999999999:isotope_37Cl|1.99795:isotope_81Cl|2.01565:H2|4.961:Na↔ NH4|4.0313:H4|7.008:Halogen exchange with cyano group|12:C|13.0078:CH|14.0031:N|14.0157:CH2|15.0109:NH|15.0235:CH3|15.9949:O|16.0187:NH2|16.0313:CH4|17.0027:OH|17.026547:adduct_rel_H_NH4 or NH3|18.0106:H2O|21.981942:adduct_rel_H_Na|24:C2|25.0078:C2H|26.0031:CN|26.0157:C2H2|27.0109:CHN|27.0235:C2H3|27.9949:CO|28.0062:N2|28.0187:CH2N|28.0313:C2H4|29.0027:CHO|29.014:HN2|29.0266:CH3N|29.0391:C2H5|29.998:NO|30.0106:CH2O|30.0218:H2N2|30.0344:CH4N|30.047:C2H6|31.0058:HNO|31.0184:CH3O|31.0297:H3N2|31.0422:CH5N|31.9898:O2|32.0136:H2NO|32.0262:CH4O|32.0375:H4N2|32.9976:HO2|33.0215:H3NO|34.0054:H2O2|36:C3|37.0078:C3H|37.955882:adduct_rel_H_K|38.0031:C2N|38.0157:C3H2|39.0109:C2HN|39.0235:C3H3|39.9949:C2O|40.0062:CN2|40.0187:C2H2N|40.0313:C3H4|41.0027:C2HO|41.014:CHN2|41.0266:C2H3N|41.0391:C3H5|41.998:CNO|42.0093:N3|42.0106:C2H2O|42.0218:CH2N2|42.0344:C2H4N|42.047:C3H6|43.0058:CHNO|43.0171:HN3|43.0184:C2H3O|43.0297:CH3N2|43.0422:C2H5N|43.0548:C3H7|43.9898:CO2|44.0011:N2O|44.0136:CH2NO|44.0249:H2N3|44.0262:C2H4O|44.0375:CH4N2|44.0501:C2H6N|44.0626:C3H8|44.9976:CHO2|45.0089:HN2O|45.0215:CH3NO|45.0328:H3N3|45.034:C2H5O|45.0453:CH5N2|45.0579:C2H7N|45.9929:NO2|46.0054:CH2O2|46.0167:H2N2O|46.0293:CH4NO|46.0406:H4N3|46.0419:C2H6O|46.0532:CH6N2|47.0007:HNO2|47.0133:CH3O2|47.0248:H3N2O|47.0371:CH5NO|47.0484:H5N3|47.9965:SO|48.9925:HO3|49.0078:C4H|49.0164:H3NO2|50.0003:H2O3|50.0031:C3N|50.0157:C4H2|51.0109:C3HN|51.0235:C4H3|51.9949:C3O|52.0062:C2N2|52.0187:C3H2N|52.0313:C4H4|53.0027:C3HO|53.014:C2HN2|53.0266:C3H3N|53.0391:C4H5|53.998:C2NO|54.0093:CN3|54.0106:C3H2O|54.0218:C2H2N2|54.0344:C3H4N|54.047:C4H6|55.0058:C2HNO|55.0171:CHN3|55.0184:C3H3O|55.0297:C2H3N2|55.0422:C3H5N|55.0548:C4H7|55.9898:C2O2|56.0011:CN2O|56.0124:N4|56.0136:C2H2NO|56.0249:CH2N3|56.0262:C3H4O|56.0375:C2H4N2|56.0501:C3H6N|56.0626:C4H8|56.9976:C2HO2|57.0089:CHN2O|57.0202:HN4|57.0215:C2H3NO|57.0328:CH3N3|57.034:C3H5O|57.0453:C2H5N2|57.0579:C3H7N|57.0705:C4H9|57.9929:CNO2|58.0042:N3O|58.0054:C2H2O2|58.0167:CH2N2O|58.028:H2N4|58.0293:C2H4NO|58.0406:CH4N3|58.0419:C3H6O|58.0532:C2H6N2|58.0657:C3H8N|58.0783:C4H10|59.0007:CHNO2|59.012:HN3O|59.0133:C2H3O2|59.0246:CH3N2O|59.0359:H3N4|59.0371:C2H5NO|59.0484:CH5N3|59.0497:C3H7O|59.061:C2H7N2|59.0736:C3H9N|59.9847:CO3|59.996:N2O2|60:C5|60.0085:CH2NO2|60.0198:H2N3O|60.0211:C2H4O2|60.0324:CH4N2O|60.0437:H4N4|60.0449:C2H6NO|60.0563:CH6N3|60.0575:C3H8O|60.0688:C2H8N2|60.9925:CHO3|61.0038:HN2O2|61.0078:C5H|61.0164:CH3NO2|61.0277:H3N3O|61.0289:C2H5O2|61.0402:CH5N2O|61.0515:H5N4|61.0528:C2H7NO|61.0641:CH7N3|61.9878:NO3|62.0003:CH2O3|62.0031:C4N|62.0116:H2N2O2|62.0157:C5H2|62.0242:CH4NO2|62.0368:H4N3O|62.0368:C2H6O2|62.048:CH6N2O|62.0575:C4H8O|62.0594:H6N4|62.9956:HNO3|63.0082:CH3O3|63.0109:C4HN|63.0195:H3N2O2|63.0235:C5H3|63.032:CH5NO2|63.0433:H5N3O|63.9796:O4|63.9949:C4O|64.0034:H2NO3|64.0062:C3N2|64.016:CH4O3|64.0187:C4H2N|64.0273:H4N2O2|64.0313:C5H4|64.9874:HO4|65.0027:C4HO|65.0113:N3NO3|65.014:C3HN2|65.0266:C4H3N|65.0391:C5H5|65.9953:H2O4|65.998:C3NO|65.998:C3NO|66.0093:C2N3|66.0106:C4H2O|66.0218:C3H2N2|66.0344:C5H6|66.047:C5H6|67.0058:C3HNO|67.0171:C2HN3|67.0184:C4H3O|67.0297:C3H3N2|67.0422:C4H5N|67.0548:C5H7|67.9898:C3O2|68.0011:C2N2O|68.0124:CN4|68.0136:C3N2NO|68.0249:C2H2N3|68.0262:C4H4O|68.0375:C3H4N2|68.05011:C4H6N|68.0626:C5H8|68.9976:C3HO2|69.0089:C2HN2O|69.0202:CHN4|69.0215:C3H3NO|69.0328:C2H3N3|69.034:C4H5O|69.0453:C3H5N2|69.0579:C4H7N|69.0705:C5H9|69.9929:C2NO2|70.0042:CN3O|70.0054:C3H2O2|70.0167:C2H2N2O|70.028:CH2N4|70.0293:C3H4NO|70.0406:C2H4N3|70.0419:C4H6O|70.0532:C3H6N2|70.0657:C4H8N|70.0783:C5H10|71.0007:C2HNO2|71.012:CHN3O|71.0133:C3H3O2|71.0246:C2H3N2O|71.0359:CH3N4|71.0371:C3H5NO|71.0484:C2H5N3|71.0497:C4H7O|71.061:C3H7N2|71.0736:C4H9N|71.0861:C5H11|71.9847:C2O3|71.996:CN2O2|72:C6|72.0073:N40|72.0085:C2H2NO2|72.0198:CH2N3O|72.0211:C3H492|72.0324:C2H4N2O|72.0449:C3H6NO|72.0497:CH4N4|72.0563:C2H6N3|72.0688:C3H8N2|72.0814:C4H10N|72.0939:C5H12|72.9925:C2HO3|73.0038:CHN2O2|73.0078:C6H|73.0151:HN40|73.0164:C2H3NO2|73.0277:CH3N3O|73.0289:C3H5O2|73.0402:C2H5N2O|73.0515:CH5N4|73.0528:C3H7NO|73.0641:C2H7N3|73.0653:C4H9O|73.0767:C3H9N2|73.0892:C4H11N|73.9878:CNO3|73.9991:N3O2|74.0003:C2H2O3|74.0031:C5N|74.0116:CH2N2O2|74.0157:C6H2|74.0229:H2N40|74.0242:C2H4NO2|74.0355:CH4N3O|74.0368:C3H6O2|74.0433:CH5N3O|74.048:C2H6N2O|74.0594:CH6N4|74.0606:C3H8NO|74.0719:C2H8N3|74.0732:C4H10O|74.0845:C3H10N2|74.9956:CHNO3|75.0069:HN3O2|75.0082:C2H3O3|75.0109:C5HN|75.0195:CH3N2O2|75.0235:C6H3|75.0308:H3N4O|75.032:C2H5NO2|75.0446:C3H7O2|75.0559:C2H7N2O|75.0672:CH7N4|75.0684:C3H9NO|75.0798:C2H9N3|75.9796:CO4|75.9949:C5O|76.0034:CH2NO3|76.0062:C4N2|76.016:C4H4O3|76.017:H2N3O2|76.0187:C5H2N|76.0273:CH4N2O2|76.0313:C6H4|76.0386:H4N4O|76.0399:C2H6NO2|76.0511:CH6N3O|76.0524:C3H8O2|76.0637:C2H8N2O|76.0653:C6H9O|76.075:CH8N4|76.9874:CHO4|76.9909:N2O3|76.9987:HN2O3|77.0027:C5HO|77.0113:CH3NO3|77.014:C4HN2|77.0226:H3N3O2|77.0238:C2H5O3|77.0266:C5H3N|77.0351:CH5N2O2|77.0391:C6H5|77.0464:H5N4O|77.0477:C2HNO2|77.059:CH7N3O|77.9827:NO4|77.9953:CH2O4|77.998:C4NO|78.0065:H2N2O3|78.0093:C3N3|78.0106:C5H2O|78.0191:CH4NO3|78.0218:C4H2N2|78.0304:H4N3O2|78.0317:C2H6O3|78.0344:C5H4N|78.0429:CH6N2O2|78.047:C6H6|78.0542:H6N4O|78.9905:HNO4|79.0031:CH3O4|79.0058:C4HNO|79.0144:H3N2O3|79.0171:C3HN3|79.0184:C5H3O|79.0269:CH5NO3|79.0297:C4H3N2|79.0382:H5N3O2|79.0422:C5H5N|79.0548:C6H7|79.9898:C4O2|79.9983:H2NO4|80.0011:C3N2O|80.0124:C2N4|80.0136:C4H2NO|80.0222:H4N2O3|80.0249:C3H2N3|80.0262:C5H4O|80.0375:C4H4N2|80.0501:C5H6N|80.0626:C6H8|80.109:CH4O4|80.9976:C4HO2|81.0062:H3NO4|81.0089:C3HN2O|81.0202:C2HN4|81.0215:C4H3NO|81.0328:C3H3N3|81.034:C5H5O|81.0453:C4H5N2|81.0579:C5H7N|81.0705:C6H9|81.9929:C3NO2|82.0042:C2N3O|82.0054:C4H2O2|82.0167:C3H2N2O|82.028:C2H2N4|82.0293:C4H4NO|82.0406:C3H4N3|82.0419:C5H6O|82.0532:C4H6N2|82.0657:C5H8N|82.0783:C6H10|83.0007:C3HNO2|83.012:C2HN3O|83.0133:C4H3O2|83.0246:C3H3N2O|83.0359:C2H3N4|83.0371:C4H5NO|83.0484:C3H5N3|83.0497:C5H7O|83.061:C4H7N2|83.0736:C5H9N|83.0861:C6H11|83.9847:C3O3|83.996:C2N2O2|84:C7|84.0073:CN4O|84.0085:C3H2NO2|84.0198:C2H2N3O|84.0211:C4H4O2|84.0308:CH3N4O|84.0324:C3H4N2O|84.0437:C2H4N4|84.0449:C4H6NO|84.0563:C3H6N3|84.0575:C5H8O|84.0688:C4H8N2|84.0798:C3H9N3|84.0814:C5H10N|84.0939:C6H12|84.9925:C3HO3|85.0031:C6N|85.0038:C2HN2O2|85.0078:C7H|85.0151:CHN4O|85.0157:C7H2|85.0164:C3H3NO2|85.0277:C2H3N3O|85.0289:C4H5O2|85.0402:C3H5N2O|85.0515:C2H5N4|85.0528:C4H7NO|85.0641:C3H7N3|85.0653:C5H9O|85.0767:C4H9N2|85.0892:C5H11N|85.1018:C6H13|85.9878:C2NO3|85.9991:CN3O2|86.0003:C3H2O3|86.0116:C2H2N2O2|86.0229:CH2N4O|86.0242:C3H4NO2|86.0355:C2H4N3O|86.0368:C4H6O2|86.048:C3H6N2O|86.0594:C2H6N4|86.0606:C4H8NO|86.0719:C3H8N3|86.0732:C5H10O|86.0845:C4H10N2|86.097:C5H12N|86.1096:C6H14|86.9956:C2HNO3|87.0069:CHN3O2|87.0082:C3H3O3|87.0109:C6HN|87.0195:C2H3N2O2|87.0235:C7H3|87.032:C3H5NO2|87.0433:C2H5N3O|87.0446:C4H7O2|87.0559:C3H7N2O|87.0672:C2H7N4|87.0684:C4H9NO|87.081:C5H11O|87.0923:C4H11N2|87.1049:C5H13N|87.9796:C2O4|87.9909:CN2O3|87.9949:C6O|88.0022:N4O2|88.0034:C2H2NO3|88.0062:C5N2|88.0147:CH2N3O2|88.016:C3H4O3|88.0187:C6H2N|88.0273:C2H4N2O2|88.0313:C7H4|88.0386:CH4N4O|88.0399:C3H6NO2|88.0511:C2H6N3O|88.0524:C4H8O2|88.0637:C3H8N2O|88.075:C2HIN4|88.0763:C4H10NO|88.0876:C3H10N3|88.0888:C5H12O|88.1001:C4H12N2|88.9874:C2HO4|88.9987:CHN2O3|89.0027:C6HO|89.01:HN4O2|89.0113:C2H3NO3|89.014:C5NHN2|89.0226:CH3N3O2|89.0238:C3H5O3|89.0266:C6H3N|89.0351:C2H5N2O2|89.0391:C7H5|89.0464:CH5N4O|89.0477:C3H7NO2|89.059:C2H7N3O|89.0603:C4H9O2|89.0715:C3H9N2O|89.0829:C2H9N4|89.0841:C4H11NO|89.0954:C3H11N3|89.9827:CNO4|89.993:C5NO|89.994:N3O3|89.9953:C2H2O4|90.0065:CH2N2O3|90.0093:C4N3|90.0106:C6H2O|90.0178:H2N4O2|90.0191:C2H4NO|90.0218:C5H2N2|90.0304:CH4N3O2|90.0317:C3H6O3|90.0344:C6H4N|90.0429:C2H6N2O2|90.047:C7H6|90.0542:CH6N4O|90.0555:C3H8NO2|90.0668:C28N3O|90.0681:C4H10O2|90.0794:C3H10N2O|90.0907:C2H10N4|90.9905:CHNO4|91.0018:HN3O3|91.0031:C2H3O4|91.0058:C5HNO|91.0144:CH3N2O3|91.0171:C4HN3|91.0184:C6H3O|91.0257:H3N4O2|91.0269:C2H5NO3|91.0297:C5H3N2|91.0382:CH5N3O2|91.0395:C3H7O3|91.0422:C6H5N|91.0508:C2H7N2O2|91.0548:C7H7|91.0634:C3HONO2|91.0746:C2H9N3O|91.9858:N2O4|91.9898:C5O2|91.9983:CH2NO4|92.0011:C4N2O|92.0096:H2N3O3|92.0109:C2H4O4|92.0124:C3N4|92.0222:CH4N2O3|92.0249:C4H2N3|92.0262:C6H4O|92.0335:H4N4O2|92.0348:C2H6NO3|92.0375:C5H4N2|92.046:CH6N3O2|92.0473:C3H8O3|92.0501:C6H6N|92.0586:C2H8N2O2|92.0621:CH7N4O|92.0626:C7H8|92.0699:CH8N4O|92.136:C5H2NO|92.9936:HN2O4|92.9976:C5HO2|93.0062:CH3NO4|93.0089:C44HN2O|93.0175:H3N3O3|93.0187:C2H5O4|93.0202:C3HN4|93.0215:C5H3NO|93.03:CH5N2O3|93.034:C6H5O|93.0413:H5N4O2|93.0426:C2H7NO3|93.0453:C5H5N2|93.0539:CH7N3O2|93.0579:C6H7N|93.0705:C7H9|93.328:C4H3N3|93.9929:C4NO2|94.0014:H2N2O4|94.0042:C3N3O|94.0054:C5H2O2|94.014:CH4NO4|94.0167:C4H2N2O|94.0253:H4N3O3|94.0266:C2H6O4|94.028:C3H2N4|94.0293:C5H4NO|94.0379:CH6N2O3|94.0406:C4H4N3|94.0419:C6H6O|94.0491:H6N4O2|94.0532:C5H6N2|94.0657:C6H8N|94.0783:C7H10|95.0007:C4HNO2|95.0093:H3N2O4|95.012:C3HN3O|95.0133:C5H3O2|95.0218:CH5NO4|95.0246:C4H3N2O|95.0331:H5N3O3|95.0359:C3H3N4|95.0371:C5H5NO|95.0484:C4H5N3|95.0497:C6H7O|95.061:C5H7N2|95.0736:C6H9N|95.0861:C7H11|95.9847:C4O3|95.996:C3N2O2|96:C8|96.0073:C2N4O|96.0085:C4H2NO2|96.0171:H4N2O4|96.0198:C3H2N3O|96.0211:C5H4O2|96.0324:C4H4N2O|96.0437:C3H4N4|96.0449:C5H6NO|96.0563:C4H6N3|96.0575:C6H8O|96.0688:C5H8N2|96.0814:C6H10N|96.0939:C7H12|96.9925:C4HO3|97.0038:C3HN2O2|97.0078:C8H|97.0151:C2HN4O|97.0154:C4H3NO2|97.0277:C3H3N3O|97.0289:C5H5O2|97.0402:C4H5N2O|97.0515:C3H5N4|97.0528:C5H7NO|97.0641:C4H7N3|97.0767:C5H9N2|97.0892:C6H11N|97.1018:C7H13|97.9878:C3NO3|97.9991:C2N3O2|98.0003:C4H2O3|98.0031:C7N|98.0116:C3H2N2O2|98.0157:C8H2|98.0229:C2H2N4O|98.0242:C4H4NO2|98.0355:C3H4N3O|98.0368:C5H6O2|98.048:C4H6N2O|98.0594:C3H6N4|98.0606:C5H8NO|98.0645:C5H10N2|98.0719:C4H8N3|98.0732:C6H10O|98.097:C6H12N|98.1096:C7H14|99.0069:C2HN3O2|99.0082:C4H3O3|99.0109:C7HN|99.0195:C3H3N2O2|99.0235:C8H3|99.0308:C2H3N4O|99.032:C4H5NO2|99.0433:C3H5N3O|99.0446:C5H7O2|99.0559:C4H7N2O|99.0672:C3H7N4|99.0684:C5H9NO|99.0798:C4H9N3|99.081:C6H11O|99.0923:C5H11N2|99.1049:C6H13N|99.1174:C7H15|99.9956:C3HNO3|116.0825:C4H10N3O|132.0782:C6H12O3|132.1138:C5H14N30|168.1879:C12H24|172.0735:C8H12O4|172.0763:C11H10NO|174.1244:C7H16N3O|174.1256:C9H18O3|176.1049:C8H16O4|176.1063:C9H12N4|176.1076:C11H14NO|176.1202:C12H16O|182.142:C10H18N2O|191.1158:C817NO4|191.1185:C11H15N2O|216.1012:C11H12N4O|220.13:C11H16N4O|220.1338:C13H20N2O|-129.057846:G-W|-115.042196:A-W|-106.041866:G-Y|-99.079646:G-R|-99.047281:S-W|-92.026216:A-Y|-90.046946:G-F|-89.026546:P-W|-87.010896:V-W|-85.063996:A-R|-85.03163:T-W|-83.07012:C-W|-80.037446:G-H|-76.031301:S-Y|-76.031296:A-F|-74.019016:G-M|-72.99525:L-W|-72.99525:I-W|-72.03638:N-W|-72.021126:G-E|-71.073496:G-K|-71.05237:D-W|-71.037116:G-Q|-69.069081:S-R|-66.021796:A-H|-66.010566:P-Y|-63.994916:V-Y|-62.01565:T-Y|-60.05414:C-Y|-60.036381:S-F|-60.003366:A-M|-59.048346:P-R|-58.02073:Q-W|-58.005476:G-D|-58.005476:A-E|-57.98435:K-W|-57.057846:A-K|-57.03672:E-W|-57.032696:V-R|-57.021466:G-N|-57.021466:A-Q|-56.062596:G-L|-56.062596:G-I|-55.05343:T-R|-55.03883:M-W|-53.09192:C-R|-50.026881:S-H|-50.015646:P-F|-49.97927:L-Y|-49.97927:I-Y|-49.0204:N-Y|-49.0204:H-W|-48.03639:D-Y|-47.999996:V-F|-46.02073:T-F|-45.987726:G-C|-44.05922:C-F|-44.026216:G-T|-44.008451:S-M|-43.989826:A-D|-43.01705:L-R|-43.01705:I-R|-43.005816:A-N|-42.05818:N-R|-42.04695:G-V|-42.046946:A-L|-42.046946:A-I|-42.010561:S-E|-41.07417:D-R|-41.062931:S-K|-41.026551:S-Q|-40.0313:G-P|-40.006146:P-H|-39.0109:F-W|-37.990496:V-H|-36.01123:T-H|-35.00475:Q-Y|-34.96837:K-Y|-34.04972:C-H|-34.02074:E-Y|-33.987716:P-M|-33.98435:L-F|-33.98435:I-F|-33.02548:N-F|-32.04147:D-F|-32.02285:M-Y|-31.989826:P-E|-31.972076:A-C|-31.972066:V-M|-31.042196:P-K|-31.005816:P-Q|-30.010566:A-T|-30.010565:G-S|-29.9928:T-M|-29.9782:R-W|-29.974176:V-E|-29.026546:V-K|-28.990166:V-Q|-28.04253:Q-R|-28.0313:A-V|-28.03129:C-M|-28.00615:K-R|-27.994911:S-D|-27.99491:T-E|-27.05852:E-R|-27.04728:T-K|-27.010901:S-N|-27.0109:T-Q|-26.052031:S-L|-26.052031:S-I|-26.0334:C-E|-26.01565:A-P|-26.00442:H-Y|-25.08577:C-K|-25.06063:M-R|-25.04939:C-Q|-23.97485:L-H|-23.97485:I-H|-23.01598:N-H|-23.01598:Y-W|-22.03197:D-H|-19.0422:H-R|-19.00983:Q-F|-18.97345:K-F|-18.02582:E-F|-17.974176:P-D|-17.95642:L-M|-17.95642:I-M|-16.99755:N-M|-16.990166:P-N|-16.031296:P-L|-16.031296:P-I|-16.02793:M-F|-16.01354:D-M|-15.99492:F-Y|-15.994915:A-S|-15.977161:S-C|-15.95853:L-E|-15.95853:I-E|-15.958526:V-D|-15.0109:L-K|-15.0109:I-K|-14.99966:N-E|-14.97452:L-Q|-14.97452:I-Q|-14.974516:V-N|-14.05203:N-K|-14.015651:S-T|-14.01565:G-A|-14.01565:N-Q|-14.01565:D-E|-14.015646:V-L|-14.015646:V-I|-13.97926:T-D|-13.06802:D-K|-13.03164:D-Q|-12.99525:T-N|-12.036385:S-V|-12.03638:T-L|-12.03638:T-I|-12.01775:C-D|-11.03374:C-N|-10.07487:C-L|-10.07487:C-I|-10.020735:S-P|-10.0095:H-F|-9.0327:F-R|-9.00033:Q-H|-8.96395:K-H|-8.01632:E-H|-6.96222:R-Y|-6.01843:M-H|-5.956426:P-C|-3.994916:P-T|-3.940776:V-C|-2.9819:Q-M|-2.94552:K-M|-2.01565:P-V|-1.99789:E-M|-1.979266:V-T|-1.96151:T-C|-1.94288:L-D|-1.94288:I-D|-0.98401:N-D|-0.98401:Q-E|-0.95887:L-N|-0.95887:I-N|-0.94763:K-E|-0.03638:Q-K|0.03638:K-Q|0.94763:E-K|0.95887:N-L|0.95887:N-I|0.98401:D-N|0.98401:E-Q|1.94288:D-L|1.94288:D-I|1.96151:C-T|1.979266:T-V|1.99789:M-E|2.01565:V-P|2.94552:M-K|2.9819:M-Q|3.940776:C-V|3.994916:T-P|5.956426:C-P|6.01843:H-M|6.96222:Y-R|8.01632:H-E|8.96395:H-K|9.00033:H-Q|9.0327:R-F|10.0095:F-H|10.020735:P-S|10.07487:L-C|10.07487:I-C|11.03374:N-C|12.01775:D-C|12.03638:L-T|12.03638:I-T|12.036385:V-S|12.99525:N-T|13.03164:Q-D|13.06802:K-D|13.97926:D-T|14.015646:L-V|14.015646:I-V|14.01565:A-G|14.01565:Q-N|14.01565:E-D|14.015651:T-S|14.05203:K-N|14.974516:N-V|14.97452:Q-L|14.97452:Q-I|14.99966:E-N|15.0109:K-L|15.0109:K-I|15.958526:D-V|15.95853:E-L|15.95853:E-I|15.977161:C-S|15.994915:S-A|15.99492:Y-F|16.01354:M-D|16.02793:F-M|16.031296:L-P|16.031296:I-P|16.990166:N-P|16.99755:M-N|17.95642:M-L|17.95642:M-I|17.974176:D-P|18.02582:F-E|18.97345:F-K|19.00983:F-Q|19.0422:R-H|22.03197:H-D|23.01598:H-N|23.01598:W-Y|23.97485:H-L|23.97485:H-I|25.04939:Q-C|25.06063:R-M|25.08577:K-C|26.00442:Y-H|26.01565:P-A|26.0334:E-C|26.052031:L-S|26.052031:I-S|27.0109:Q-T|27.010901:N-S|27.04728:K-T|27.05852:R-E|27.99491:E-T|27.994911:D-S|28.00615:R-K|28.03129:M-C|28.0313:V-A|28.04253:R-Q|28.990166:Q-V|29.026546:K-V|29.974176:E-V|29.9782:W-R|29.9928:M-T|30.010565:S-G|30.010566:T-A|31.005816:Q-P|31.042196:K-P|31.972066:M-V|31.972076:C-A|31.989826:E-P|32.02285:Y-M|32.04147:F-D|33.02548:F-N|33.98435:F-L|33.98435:F-I|33.987716:M-P|34.02074:Y-E|34.04972:H-C|34.96837:Y-K|35.00475:Y-Q|36.01123:H-T|37.990496:H-V|39.0109:W-F|40.006146:H-P|40.0313:P-G|41.026551:Q-S|41.062931:K-S|41.07417:R-D|42.010561:E-S|42.046946:L-A|42.046946:I-A|42.04695:V-G|42.05818:R-N|43.005816:N-A|43.01705:R-L|43.01705:R-I|43.989826:D-A|44.008451:M-S|44.026216:T-G|44.05922:F-C|45.987726:C-G|46.02073:F-T|47.999996:F-V|48.03639:Y-D|49.0204:Y-N|49.0204:W-S|49.97927:Y-L|49.97927:Y-I|50.015646:F-P|50.026881:H-S|53.09192:R-C|55.03883:W-M|55.05343:R-T|56.062596:L-G|56.062596:I-G|57.021466:N-G|57.021466:Q-A|57.032696:R-V|57.03672:W-E|57.057846:K-A|57.98435:W-K|58.005476:D-G|58.005476:E-A|58.02073:W-Q|59.048346:R-P|60.003366:M-A|60.036381:F-S|60.05414:Y-C|62.01565:Y-T|63.994916:Y-V|66.010566:Y-P|66.021796:H-A|69.069081:R-S|71.037116:Q-G|71.05237:W-D|71.073496:K-G|72.021126:E-G|72.03638:W-N|72.99525:W-L|72.99525:W-I|74.019016:M-G|76.031296:F-A|76.031301:Y-S|80.037446:H-G|83.07012:W-C|85.03163:W-T|85.063996:R-A|87.010896:W-V|89.026546:W-P|90.046946:F-G|92.026216:Y-A|99.047281:W-S|99.079646:R-G|106.041866:Y-G|115.042196:W-A|129.057846:W-G|43.07252:Ethanolamine|67.09392:pyrrolidone|69.06674:dehydroalanine|70.051505:pyruvate|70.14092:putrescine|71.03711:Sarcosine|71.08262:beta-Alanine|71.08262:N-Methyl-Glycine|72.06738:D-lactic acid|72.06738:Lactic acid|73.098495:Serinol|83.09332:2,3-dehydro-2-aminobutyric acid|83.09332:hydroxy pyrrolidone|83.09332:homoserine lactone|83.09332:N-Methyl-dehydroalanine|85.066146:alpha-formylGlycine|85.10921:2-Aminoisobutyric acid|85.10921:D-3-methoxyalanine|85.10921:N-Methyl-Alanine|85.10921:N-methyl-beta-alanine|85.10921:D-2-Aminobutyric acid|85.10921:2-Aminobutyric acid|85.15226:isovalinol|85.15226:valinol|86.09726:2,3-Diaminopropionic acid|87.08202:D-Serine|87.08202:isoserine|96.13514:proline carboxamid|97.1199:norcoronamic acid|97.1199:2-methylamino-2-dehydrobutyric acid|97.1199:D-Proline|98.14773:3-methylvaleric acid|99.09272:N-formyl-Alanine|99.09272:D-N-formyl-Alanine|99.13578:N-dimethyl-Alanine|99.13578:Norvaline|99.13578:D-Norvaline|99.13578:D-Valine|99.13578:D-isovaline|99.13578:isovaline|99.13578:2-methyl-3-aminobutanoic acid|99.17884:Isoleucinol|99.17884:Leucinol|100.120536:2-hydroxyisovalerate|100.120536:D-2-hydroxyisovalerate|100.12384:2,4-diaminobutyric acid|100.12384:D-2,4-diaminobutyric acid|100.12384:(2S)-2,3-diaminobutyric acid|100.12384:(2R,3R)-2,3-diaminobutyric acid|100.12384:(2S,3S)-2,3-diaminobutyric acid|101.108596:4-amino-3-hydroxybutyric acid|101.108596:D-Threonine|101.108596:allo-Threonine|101.108596:D-allo-Threonine|101.108596:Homoserine|101.108596:D-Homoserine|101.108596:N-Methyl-D-Serine|101.108596:N-Methyl-Serine|101.13174:dehydro-cysteine|103.14761:D-Cysteine|104.110786:benzoic acid|110.16171:N-methylglutamine|110.18486:N-Methyl-Glycine-thiazole|111.10342:pyroglutamic acid|111.10342:4-oxo-proline|111.14648:coronamic acid|111.14648:homoproline|111.14648:D-homoproline|111.14648:3-methylproline|111.14648:4-methylproline|111.14648:5-methylproline|112.13124:keto-Leucine|112.13454:Hydroxy-cycloOrnithine|112.13454:D-Hydroxy-cycloOrnithine|113.07624:aziridine dicarboxylic acid|113.11929:N-formyl-D-aminobyric acid|113.11929:4-Hydroxyproline|113.11929:D-hydroxyproline|113.11929:3-Hydroxyproline|113.16237:D-Isoleucine|113.16237:allo-Isoleucine|113.16237:D-allo-Isoleucine|113.16237:D-tert-Leu|113.16237:tert-Leu|113.16237:D-Leucine|113.16237:D-N-methyl-norvaline|113.16237:D-N-Methylvaline|113.16237:N-Methyl-Valine|113.16237:2-methyl-3-aminopentanoic acid|113.20872:norspermidine|114.10406:hydroxyacetyl propionyl|114.10406:pentanedioic acid|114.10736:D-Asparagine|114.10736:N1-formyl-2,3-Diaminopropionic acid|114.14712:2-hydroxy-3-methyl-pentanoic acid|114.14712:D-2-hydroxy-3-methylpentanoic acid|114.14712:4-Methyl-D-2-hydroxy-valeric acid|114.15042:D-ornithine|114.15042:Ornithine|115.09213:D-aspartic acid|115.09213:N-formyl-isoserine|115.13518:D-beta-hydroxyvaline|115.13518:beta-hydroxyvaline|115.13518:O-methyl-threonine|115.13518:N-methylthreonine|117.108:4-Hydroxythreonine|117.17421:alpha-methylcysteine|117.17424:N-methylcysteine|118.13736:phenylacetic acid|120.11018:para-hydroxy-benzoic acid|121.09825:hydroxypicolinic acid|125.13:4-oxo-homoproline|125.13:N-Formyl-Proline|125.13:4-oxo-5-methylproline|127.10611:beta-ureido-dehydroAlanine|127.14589:N-Acetyl-2-aminoisobutyric acid|127.14589:N-formyl-Valine|127.14589:3-Hydroxy-5-methylproline|127.18895:homoisoleucine|127.18895:D-N-methyl-alloisoleucine|127.18895:N-Methyl-Isoleucine|127.18895:beta-methylisoleucine|127.18895:N-methyl-alloIsoleucine|127.18895:D-N-methyl-Leucine|127.18895:N-Methyl-Leucine|127.18895:alpha-ethylnorvaline|127.18895:Dolavaline|127.2353:spermidine|128.13394:D-N2-methyl-asparagine|128.13394:beta-methyl-asparagine|128.13394:N-methylasparagine|128.13394:N1-acetyl-2,3-Diaminopropionic acid|128.13394:D-Glutamine|128.177:D-Lysine|128.177:beta lysine|128.177:N-Hydroxy-histamine|129.1187:D-beta-methyl-aspartic acid|129.1187:beta-methyl-aspartic acid|129.1187:beta-methoxy-aspartic acid|129.1187:D-Glutamic Acid|129.1187:O-acetyl-Serine|129.16177:L-acosamine|129.16177:L-ristosamine|129.16177:3-hydroxyleucine|129.16177:gama-hydroxy-N-Methyl-Valine|129.16177:beta-hydroxy-N-Methyl-Valine|130.10676:Hydroxyasparagine|130.10676:D-HydroxyAsparagine|130.11006:alpha-guanidino Serine|130.14981:hydroxy-beta lysine|130.14981:N5-hydroxy ornithine|130.14981:D-N5-HydroxyOrnithine|131.09152:Hydroxyaspartic acid|131.09152:D-Hydroxyaspartic acid|131.20074:N,S-dimethylcysteine|132.11935:D-arabinose|132.11935:Arabinose|132.11935:lyxose|132.1624:L-Olivose|133.15199:D-PhenylGlycine|133.15199:phenylglycine|133.19507:phenylalaninol|135.55366:4-Chloro-Threonine|136.10959:2,3-dihydroxybenzoic acid|138.12877:dehydropyrrolidone|139.15658:2,3-dimethylpyroglutamic acid|140.19099:arginal|141.17247:4-oxovancosamine|141.17247:N-formyl-Isoleucine|141.17247:N-formyl-Leucine|141.17247:N-acetyl-isovaline|141.17247:N-Acetylvaline|141.17247:4-amino-2,2-dimethyl-3-oxopentanoic acid|141.21551:N,O-dimethyl-isoleucine|141.21551:O-acetyl-leucinol|141.21551:N,beta-dimethylLeucine|141.21554:N,gamma-alloisoleucine|141.55978:N-methylchloropyrrole|142.16052:D-beta-methylglutamine|142.16052:beta-methylglutamine|143.14528:2-Aminoadipic acid|143.14528:Glutamic Acid methyl ester|143.14528:D-Glutamic Acid methyl ester|143.14528:D-Glutamic Acid methyl ester|143.14528:3-Methyl-Glutamic acid|143.18834:L-actinosamine|143.18834:L-eremosamine|143.18834:N-methyl-hydroxyisoleucine|143.18834:norstatine|144.13334:D-beta-hydroxy-N2-methyl-asparagine|144.13334:beta-hydroxyglutamine|145.1181:methoxyaspartic acid|146.14592:L-rhamnose|147.17857:N-methyl-phenylglycine|147.17857:beta phenylalanine|147.17857:D-Phenylalanine|147.17857:D-beta-phenylalanine|147.20018:Methionine-S-oxide|147.60742:Chloro-Isoleucine|148.12028:2-hydroxyphenyl-2-oxo-ethanoic acid|148.16334:D-Phenyl-lactate|148.16334:Phenyl-lactate|149.1514:D-HydroxyPhenylGlycine|149.1514:HydroxyPhenylGlycine|151.14246:D-4-fluoroPhenylGlycine|151.14581:cysteic acid|151.14581:D-cysteic acid|153.1434:Hydroxyhistidine|153.22621:N-methyl homo vinylogous Valine|154.17451:capreomycidine|154.17451:enduracididine|154.17451:D-enduracididine|154.19437:Alanine-thiazole|155.19904:O-desmethyldolaproine|155.19904:N-acetyl-Leucine|155.2421:methyl-2-aminooctanoic acid|156.14404:N-formyl-Glutamine|156.14554:2-carboxyquinoxaline|156.18381:hydroxyisovalerylpropionyl|156.1871:3,4-dimethylglutamine|156.25003:N-trimethyl-leucine|156.25003:N-dimethyl-leucine|157.17517:D-Citrulline|157.17517:Citrulline|157.1904:D-Arginine|157.21492:isostatine|157.21492:statine|158.15991:N6-formyl-HydroxyOrnithine|158.15991:D-formyl-hydroxyOrnithine|159.14468:alpha-amino-hydroxyadipic acid|159.18928:N-methyl-2,3-dehydrophenylalanine|160.1725:O-methyl-L-rhamnose|161.20517:D-N-Methyl-Phenylalanine|161.20517:3-methylphenylalanine|161.20517:N-Methyl-Phenylalanine|161.20517:Homophenylalanine|162.14532:D-mannose|162.14532:beta-D-galactose|162.14532:D-galactose|162.14532:D-Glucose|162.14532:L-Glucose|163.11627:phosphinothricin|163.13492:N-hydroxy-dehydro-HydroxyPhenylGlycine|163.13492:D-N-hydroxy-dehydro-HydroxyPhenylGlycine|163.17798:N-methyl-HydroxyPhenylGlycine|163.17798:phenylserine|163.17798:D-Tyrosine|163.17798:beta-tyrosine|163.19958:Methionine sulfone|164.16275:4-hydroxy-D-phenyl-lactate|164.16604:propenoyl-alanyloxazole acid|165.1508:D-3,5-dihydroxyphenylglycine|165.1508:3,5-dihydroxyphenylglycine|166.01001:3,4-dichloro-proline|166.18523:cyclo alpha-ketoarginine|167.20973:2-carboxy-6-hydroxyoctahydroindole|167.25281:3-Desoxy-Methyl-4-butenyl-4-methyl threonine|168.22096:1-methoxy-beta-alanine-thiazole|169.22562:4-butenyl-4-methyl threonine|169.22562:Dolaproine|169.2753:guanylspermidine|170.17392:5-hydroxy-capreomycidine|170.21039:hydroxysecbutyl acetyl propionyl|170.21699:homoarginine|171.19844:N-methoxyacetyl-valine|171.2415:N-desmethyldolaisoleuine|172.18651:N-acetyl-HydroxyOrnithine|172.18651:D-N-acetyl-HydroxyOrnithine|172.23111:tryptophanol|175.23174:alpha-amino-phenyl-valeric acid|175.25334:beta,beta-dimethyl-Methionine-S-oxide|176.00485:N-methyldichloropyrrole-2-carboxylic acid|177.20456:beta-hydroxy-N-Methyl-Phenylalanine|177.20456:Homotyrosine|177.20456:N-methyltyrosine|178.19261:propenoyl-2-aminobutanoyloxazole acid|179.17738:3,4-dihydroxyphenylalanine|179.17738:beta-hydroxy-tyrosine|181.19327:Anticapsin|182.18462:D-homoarginine|182.22768:vinylogous arginine|183.2522:N-methyl-4-butenyl-4-methyl threonine|183.59647:3-chloro-4-hydroxyphenylglycine|184.19874:2,3-Dehydro-Tryptophan|184.2005:alpha-ketoarginine|185.22656:Dolapyrrolidone|185.26807:Dolaisoleucine|186.21461:D-Tryptophan|186.21638:hydrated alpha-ketoarginine|186.28082:Dolaphenine|187.19939:dehydro vinylogous tyrosine|188.18919:3,4-dihydroxyArginine|189.21527:N-acetylphenylalanine|189.21527:vinylogous tyrosine|190.20331:D-kynurenine|190.20331:kynurenine|190.24638:N-methyl-4-methylamino-phenylalanine|190.24638:N,O-dimethyl-tyrosinecarboxamid|191.23114:alpha-amino-hydroxyphenyl-valeric acid|191.23114:N-methyl-homotyrosine|191.23114:3-methyl-homotyrosine|191.23114:D-N,O-dimethyl-tyrosine|191.23114:N,O-dimethyl-tyrosine|193.20396:beta-methoxy-tyrosine|194.0632:di-chloro-N-methyl-dehydroLeucine|194.21033:O-sulfate-2-hydroxy-3-methylpentanoic acid|194.27814:methyloxazoline-isoleucine|196.07907:di-chloro-N-methyl-Leucine|197.27878:4-butenyl-4-methyl-N,4-methyl threonine|197.62304:chloro-tyrosine|200.19661:N-acetyl-N6-formyl-N6-hydroxyOrnithine|200.24119:N1-methyl-tryptophan|202.21402:phototryptophan|202.21402:5-hydroxytryptophan|204.27295:N-methyl-4-dimethylamino-phenylalanine|205.21467:vinylogous hydroxy tyrosine|205.25772:alpha-amino-methoxyphenyl-valeric acid|208.06703:Pyridylethylcysteine|208.17554:3-nitrotyrosine|210.08665:D-PhosphateAsparagine|210.25761:propenoyl-O-methylserinylthiazole acid|211.64961:D-3-chloro-N-methyl-Tyrosine|211.64961:Chloro-N-methyl-tyrosine|213.62245:beta-hydroxy-chloro-tyrosine|214.22317:3-amino-6-hydroxy-2-piperidone|216.23904:2,6-diamino-7-hydroxyazelaic acid|216.2406:N-methyl-5-hydroxytryptophan|216.2406:methoxytryptophan|216.24237:4-amino-7-guanidino-2,3-dihydroxyheptanoic acid|218.04154:3,5-dichloro-4-hydroxyphenylglycine|219.1982:DHP-methyloxazolinyl group|219.24124:N-methoxyacetyl-D-phenylalanine|220.65968:D-6’-chloro-tryptophan|221.2372:dihydroxyphenylthiazol group|226.07464:bromophenylalanine|228.2513:N-acetyltryptophan|228.29437:beta,beta,N-trimethyltryptophan|228.50825:tri-chloro-N-methyl-dehydroLeucine|230.22412:D-2-carboxy-tryptophan|230.29031:thiazolylphenylalanine|230.52412:tri-chloro-N-methyl-Leucine|234.68626:N-methyl-6-chloro-tryptophan|240.10124:beta-methyl-bromophenylalanine|242.07404:beta-hydroxy-bromophenylalanine|242.07404:bromotyrosine|242.32094:beta,beta,N1,N-tetramethyltryptophan|246.5235:tri-chloro-2-hydroxy-N-methyl-Leucine|246.5235:tri-chloro-5-hydroxy-N-methyl-Leucine|250.68567:N-methyl-6-chloro-5-hydroxytryptophan|256.10062:D-3-bromo-N-methyl-Tyrosine|258.27731:N1-carboxy-bichomotryptophan|259.26534:pyoverdin chromophore|259.26534:isopyoverdin chromophore|261.28122:5,6-dihydropyoverdin chromophore|263.68442:D-6-chloro-N2-formamidotryptophan|265.11069:5-bromo-tryptophan|266.38054:8,10-Dimethyl-9-hydroxy-7-methoxytridecadienoic acid|272.32704:4-propenoyl-2-tyrosylthiazole acid|279.13727:N-methyl-2-Bromo-tryptophan|281.11008:2-bromo-5-hydroxytryptophan|285.25958:azotobactins chromophore|303.10107:D-3-iodo-N-methyl-Tyrosine|310.26572:actinomycin chromophore|127.039515:L-aculose|129.055165:L-cinerulose A|131.070815:L-rhodinose|142.050414:rednose|145.05008:L-cinerulose B|145.086465:O-methyl-L-amicetose|145.086465:4-O-methyl-L-rhodinose|146.081714:L-daunosamine|146.081714:L-acosamine|146.081714:L-ristosamine|147.06573:D-digitoxose|147.06573:L-digitoxose|147.06573:2-deoxy-L-fucose|147.06573:D-olivose|147.06573:D-oliose|147.06573:L-boivinose (esperamicin A1 sugar 1)|158.081714:4-oxo-L-vancosamine|158.118098:D-forosamine|160.097363:L-actinosamine|160.097363:3-epi-L-vancosamine|160.097363:L-vancosamine|160.097363:L-vicenisamine|161.08138:D-chalcose|161.08138:D-mycarose|161.08138:3-O-methyl-L-olivose/L-oleandrose|161.08138:olivomose|162.076629:D-mycosamine|163.042887:4-deoxy-4-thio-D-digitoxose|163.060645:D-fucofuranose|163.060645:D-fucose|163.060645:L-rhamnose|163.060645:L-quinovose|163.060645:D-quinovose|174.113014:4-N-ethyl-4-amino-3-O-methoxy-2,4,5-trideoxypentose|174.113014:D-3-N-methyl-4-O-methyl-L-ristosamine|174.113014:N,N-dimethyl-L-pyrrolosamine|174.113014:D-desosamine|174.113014:L-megosamine|174.113014:nogalamine|174.113014:L-rhodosamine|174.113014:D-angolosamine|174.113014:kedarosamine|175.084454:L-noviose|175.09703:L-cladinose|176.092279:2'-N-methyl-D-fucosamine|177.058537:4-deoxy-4-methylthio-a-D-digitoxose|177.076295:D-digitalose|177.076295:3-O-methyl-rhamnose|177.076295:2-O-methyl-L-rhamnose|177.076295:6-deoxy-3-C-methyl-L-mannose|178.071544:4,6-dideoxy-4-hydroxylamino-D-glucose|179.05556:hexose|188.128664:3-N,N-dimethyl-L-eremosamine|188.128664:namenamicin sugar C|189.076295:chromose D (4-O-acetyl-β-D-oliose)|190.071544:4-O-carbamoyl-D-olivose|190.107929:D-ravidosamine|190.107929:3-N,N-dimethyl-D-mycosamine|191.091945:2,3-O-dimethyl-L-rhamnose|191.091945:2,4-O-dimethyl-L-rhamnose|191.091945:3,4-O-dimethyl-L-rhamnose|195.032717:2-thioglucose|203.091945:olivomycose (L-chromose B)|204.123579:4-N,N-dimethylamino-4-deoxy-5-C-methyl-l-rhamnose|205.107595:2,3,4-tri-O-methylrhamnose|217.107595:4-O-acetyl-L-arcanose|218.102844:3-N-acetyl-D-ravidosamine|218.102844:3-O-carbamoyl-L-noviose|219.123245:L-nogalose|232.118494:4-O-acetyl-D-ravidosamine|234.097759:3-O-carbamoyl-4-O-methyl-L-noviose|260.113409:3-N-acetyl-4-O-acetyl-D-ravidosamine|298.129059:3-(5'-methyl-2'-pyrrolylcarbonyl-)4-O-methyl-L-noviose|149.045094:D-arabinose|163.060094:L-rhamnose|163.060094:L-fucose|163.060094:D-rhamnose|178.071094:D-glucosamine|179.055094:D-glucose|179.055094:D-galactose|179.055094:D-mannose|193.035094:glucuronic acid|193.035094:D-galacturonic acid|193.071094:6-methoxy-D-glucose|193.071094:3-methoxy-D-mannose|202.071534:N-acetyl-D-glucosamine|220.082094:N-acetyl-D-galactose|237.061094:ketodeoxyoctonic acid|308.098074:N-5-acetylneuraminic acid|".split("|")
        for parsed_annotation in parsed_anntation_list:
            if len(parsed_annotation) < 3:
                continue

            mass = abs(float(parsed_annotation.split(":")[0]))
            analog_contraint_masses.append(mass)

    for repo_spectrum in dataset_query_spectra.spectrum_list:
        if match_parameters["FILTER_WINDOW"]:
            repo_spectrum.window_filter_peaks(50, 6)
        if match_parameters["FILTER_PRECURSOR"]:
            repo_spectrum.filter_precursor_peaks()

    for myspectrum in input_spectrum_collection.spectrum_list:
        if match_parameters["FILTER_WINDOW"]:
            myspectrum.window_filter_peaks(50, 6)
        if match_parameters["FILTER_PRECURSOR"]:
            myspectrum.filter_precursor_peaks()

        try:
            match_list = dataset_query_spectra.search_spectrum(myspectrum, 
                                                                match_parameters["PM_TOLERANCE"], 
                                                                match_parameters["FRAGMENT_TOLERANCE"], 
                                                                match_parameters["MIN_MATCHED_PEAKS"], 
                                                                match_parameters["MIN_COSINE"], 
                                                                analog_search=match_parameters["ANALOG_SEARCH"],
                                                                analog_constraint_masses=analog_contraint_masses,
                                                                top_k=top_k)
            for match in match_list:
                match["filename"] = relative_dataset_filepath
            dataset_match_list += match_list
        except:
            print("Error in Matching")

    print("Dataset matches: " + str(len(dataset_match_list)))

    return dataset_match_list

def get_parameters(params_obj):
    MIN_COSINE = 0.7
    MIN_MATCHED_PEAKS = 6
    PM_TOLERANCE = 2.0
    FRAGMENT_TOLERANCE = 2.0
    FILTER_PRECURSOR = True
    FILTER_WINDOW = True
    ANALOG_SEARCH = False
    ANALOG_CONSTRAINT = "NONE"
    SEARCH_RAW = False

    try:
        MIN_COSINE = float(params_obj["SCORE_THRESHOLD"][0])
    except:
        print("Param Not Found", "SCORE_THRESHOLD")

    try:
        MIN_MATCHED_PEAKS = int(params_obj["MIN_MATCHED_PEAKS"][0])
    except:
        print("Param Not Found", "MIN_MATCHED_PEAKS")

    try:
        PM_TOLERANCE = float(params_obj["tolerance.PM_tolerance"][0])
    except:
        print("Param Not Found", "PM_TOLERANCE")

    try:
        FRAGMENT_TOLERANCE = float(params_obj["tolerance.Ion_tolerance"][0])
    except:
        print("Param Not Found", "FRAGMENT_TOLERANCE")

    try:
        if params_obj["FILTER_PRECURSOR_WINDOW"][0] == "0":
            FILTER_PRECURSOR = False
    except:
        print("Param Not Found", "FILTER_PRECURSOR_WINDOW")

    try:
        if params_obj["WINDOW_FILTER"][0] == "0":
            FILTER_WINDOW = False
    except:
        print("Param Not Found", "WINDOW_FILTER")
    try:
        if params_obj["ANALOG_SEARCH"][0] == "1":
            ANALOG_SEARCH = True
    except:
        print("Param Not Found", "ANALOG_SEARCH")
    try:
        ANALOG_CONSTRAINT = params_obj["ANALOG_CONSTRAINT"][0]
    except:
        print("Param Not Found", "ANALOG_CONSTRAINT")
    try:
        if params_obj["SEARCH_RAW"][0] == "1":
            SEARCH_RAW = True
    except:
        print("Param Not Found", "SEARCH_RAW")

    parameters = {}
    parameters["MIN_COSINE"] = MIN_COSINE
    parameters["MIN_MATCHED_PEAKS"] = MIN_MATCHED_PEAKS
    parameters["PM_TOLERANCE"] = PM_TOLERANCE
    parameters["FRAGMENT_TOLERANCE"] = FRAGMENT_TOLERANCE
    parameters["FILTER_PRECURSOR"] = FILTER_PRECURSOR
    parameters["FILTER_WINDOW"] = FILTER_WINDOW
    parameters["ANALOG_SEARCH"] = ANALOG_SEARCH
    parameters["ANALOG_CONSTRAINT"] = ANALOG_CONSTRAINT
    parameters["SEARCH_RAW"] = SEARCH_RAW

    return parameters


"""Outputting all match summary for each dataset"""
def match_clustered(match_parameters, spectrum_collection, dataset_dict, all_datasets, output_matches_filename, output_filename_unique_files, output_filename_all_matches):
    all_matches = finding_matches_in_public_data(spectrum_collection, all_datasets, match_parameters)

    """Resolving to File Level"""
    dataset_files_count = defaultdict(lambda: 0)
    output_source_list = []
    output_match_list = []

    MetaDataServerStatus = trace_to_single_file.test_metadata_server()

    for dataset in all_matches:
        for match_object in all_matches[dataset]["matches"]:
            dataset_accession = dataset_dict[dataset]["dataset"]
            dataset_scan = match_object["scan"]
            current_filelist, current_match_list = trace_to_single_file.trace_filename_filesystem(all_datasets, dataset_accession, dataset_scan, enrichmetadata=MetaDataServerStatus)
            output_source_list += current_filelist
            output_match_list += current_match_list

    seen_files = set()
    output_unique_source_list = []
    for output_file_object in output_source_list:
        dataset_accession = output_file_object["dataset_id"]
        dataset_filename = output_file_object["filename"]

        key = dataset_accession + ":" + dataset_filename
        if key in seen_files:
            continue

        dataset_files_count[dataset_accession] += 1

        seen_files.add(key)

        output_unique_source_list.append(output_file_object)

    ming_fileio_library.write_list_dict_table_data(output_unique_source_list, output_filename_unique_files)
    ming_fileio_library.write_list_dict_table_data(output_match_list, output_filename_all_matches)


    """ Summary """
    output_map = {"specs_filename" : [],"specs_scan" : [], "dataset_filename" : [], "dataset_scan" : [], "score" : [], "dataset_id" : [], "dataset_title" : [], "dataset_description" : [], "dataset_organisms" : [], "matchedpeaks" : [], "mzerror" : [], "files_count": []}
    for dataset in all_matches:
        #For each dataset, lets try to find the clustering information
        if len(all_matches[dataset]["matches"]) == 0:
            continue

        match_object = None

        #If it is more than one match, we need to consolidate
        if len(all_matches[dataset]["matches"]) > 1:
            sorted_match_list = sorted(all_matches[dataset]["matches"], key=lambda match: float(match["cosine"]), reverse=True)
            match_object = sorted_match_list[0]
        else:
            match_object = all_matches[dataset]["matches"][0]

        output_map['specs_filename'].append("specs_ms.mgf")
        output_map['specs_scan'].append(match_object["queryscan"])
        output_map['dataset_id'].append(dataset_dict[dataset]["dataset"])
        output_map['dataset_title'].append(dataset_dict[dataset]["title"])
        output_map['dataset_description'].append(dataset_dict[dataset]["description"].replace("\n", "").replace("\t", ""))
        output_map['dataset_organisms'].append( dataset_dict[dataset]["species"].replace("<hr class='separator'\/>", "!") )
        output_map['dataset_filename'].append(match_object["filename"])
        output_map['dataset_scan'].append(match_object["scan"])
        output_map['score'].append(match_object["cosine"])
        output_map['matchedpeaks'].append(match_object["matchedpeaks"])
        output_map['mzerror'].append(match_object["mzerror"])
        output_map['files_count'].append(dataset_files_count[dataset])


    ming_fileio_library.write_dictionary_table_data(output_map, output_matches_filename)



def match_unclustered(match_parameters, spectrum_collection, dataset_dict, all_datasets, output_matches_filename, output_filename_unique_files, output_filename_all_matches):
    MetaDataServerStatus = trace_to_single_file.test_metadata_server()

    all_matches_by_dataset = finding_matches_in_public_data(spectrum_collection, all_datasets, match_parameters)

    dataset_matches_output_list = []
    output_filename_unique_files_list = []
    output_filename_all_matches_list = []
    for dataset in all_matches_by_dataset:
        #For each dataset, lets try to find the clustering information
        if len(all_matches_by_dataset[dataset]["matches"]) == 0:
            continue

        top_match = sorted(all_matches_by_dataset[dataset]["matches"], key=lambda match: match["cosine"], reverse=True)[0]

        output_dict = {}
        output_dict['specs_filename'] = "specs_ms.mgf"
        output_dict['specs_scan'] = top_match["queryscan"]
        output_dict['dataset_id'] = dataset_dict[dataset]["dataset"]
        output_dict['dataset_title'] = dataset_dict[dataset]["title"]
        output_dict['dataset_description'] = dataset_dict[dataset]["description"].replace("\n", "").replace("\t", "")
        output_dict['dataset_organisms'] = dataset_dict[dataset]["species"].replace(";", "!")
        output_dict['dataset_filename'] = top_match["filename"]
        output_dict['dataset_scan'] = top_match["scan"]
        output_dict['score'] = top_match["cosine"]
        output_dict['matchedpeaks'] = top_match["matchedpeaks"]
        output_dict['mzerror'] = top_match["mzerror"]
        output_dict['files_count'] = len(all_matches_by_dataset[dataset]["matches"])

        dataset_matches_output_list.append(output_dict)


        """Unique Filenames Calculation"""
        unique_files = list(set([match["filename"] for match in all_matches_by_dataset[dataset]["matches"]]))
        for source_file in unique_files:
            output_object = {}
            output_object["dataset_id"] = dataset_dict[dataset]["dataset"]
            output_object["cluster_scan"] = ""
            output_object["filename"] = source_file
            output_object["metadata"] = ""

            if MetaDataServerStatus:
                metadata_list = trace_to_single_file.get_metadata_information_per_filename(source_file)
                output_object["metadata"] = "|".join(metadata_list)

            output_filename_unique_files_list.append(output_object)

        for match in all_matches_by_dataset[dataset]["matches"]:
            output_object = {}
            output_object["dataset_id"] = dataset
            output_object["cluster_scan"] = match["queryscan"]
            output_object["filename"] = match["filename"]
            output_object["filescan"] = match["scan"]
            output_object["metadata"] = ""

            if MetaDataServerStatus:
                metadata_list = trace_to_single_file.get_metadata_information_per_filename(match["filename"])
                output_object["metadata"] = "|".join(metadata_list)

            output_filename_all_matches_list.append(output_object)

    ming_fileio_library.write_list_dict_table_data(dataset_matches_output_list, output_matches_filename)
    ming_fileio_library.write_list_dict_table_data(output_filename_unique_files_list, output_filename_unique_files)
    ming_fileio_library.write_list_dict_table_data(output_filename_all_matches_list, output_filename_all_matches)

def main():
    paramxml_input_filename = sys.argv[1]
    parallel_param_filename = sys.argv[2]
    output_matches_filename = sys.argv[3]
    output_filename_unique_files = sys.argv[4]
    output_filename_all_matches = sys.argv[5]

    params_obj = ming_proteosafe_library.parse_xml_file(open(paramxml_input_filename))

    output_map = {"specs_filename" : [],"specs_scan" : [], "dataset_filename" : [], "dataset_scan" : [], "score" : [], "dataset_id" : [], "dataset_title" : [], "dataset_description" : [], "matchedpeaks" : [], "mzerror" : []}

    match_parameters = get_parameters(params_obj)

    try:
       if params_obj["FIND_MATCHES_IN_PUBLIC_DATA"][0] != "1":
           ming_fileio_library.write_dictionary_table_data(output_map, output_matches_filename)
           exit(0)
    except:
       ming_fileio_library.write_dictionary_table_data(output_map, output_matches_filename)
       exit(0)

    #If we are doing parallel
    partition_total = 1
    partition_of_node = 0
    params_map = json.loads(open(parallel_param_filename).read())
    partition_total = params_map["total_paritions"]
    partition_of_node = params_map["node_partition"]

    dataset_dict = params_map["dataset_dict"]
    all_datasets = params_map["all_datasets"]

    SEARCH_RAW = False
    try:
        if params_obj["SEARCH_RAW"][0] == "1":
            SEARCH_RAW = True
    except:
        print("Param Not Found", "SEARCH_RAW")

    """Matchign Clustered Data"""
    if SEARCH_RAW:
        match_unclustered(match_parameters, get_spectrum_collection_from_param_obj(params_obj), dataset_dict, all_datasets, output_matches_filename, output_filename_unique_files, output_filename_all_matches)
    else:
        match_clustered(match_parameters, get_spectrum_collection_from_param_obj(params_obj), dataset_dict, all_datasets, output_matches_filename, output_filename_unique_files, output_filename_all_matches)



if __name__ == "__main__":
    main()
