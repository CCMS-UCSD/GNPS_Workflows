#!/usr/bin/python


import sys
import getopt
import os
import ming_proteosafe_library
import argparse
import json
import csv

"""Generate annotations for each peak"""
def determine_delta_annotations(mass_delta, node_mz, list_of_annotations, ppm_accuracy):
    output_list_of_annotations = []

    for annotation in list_of_annotations:
        mass_of_annotation = annotation["mass"]
        try:
            ppm = (abs(mass_delta - mass_of_annotation)/node_mz) * 1000000
        except:
            ppm = 10000
        if ppm < ppm_accuracy:
            output_list_of_annotations.append(annotation["tag"])

    return output_list_of_annotations

def get_annotation_list():
    pairs_annotation_list = []

    parsed_anntation_list = "0.50097:z = 2|0.98402:NH3<->OH|1.00335:isotope_13C|1.007:H|1.9958:isotope_34S|1.99705:isotope_37Cl|1.99795:isotope_81Br|2.01565:H2|3.978:Na-H2O|4.0313:H4|4.95:Na-NH3|12:C|13.0078:CH|14.00307401:tertiary amine|14.0031:N|14.015650074:methanol (-H2O)|14.0157:CH2|15.010899047:secondary amine|15.0109:NH|15.0235:CH3|15.9949:O|16.0187:NH2|16.018724084:primary amine|16.0313:CH4|17.0027:OH|17.026547:adduct_rel_H_NH4 or NH3|18.0106:H2O|21.981942:adduct_rel_H_Na|21.986:Na-H|24:C2|25.0078:C2H|26.0031:CN|26.0157:C2H2|27.0109:CHN|27.0235:C2H3|27.9949:CO|28.0062:N2|28.0187:CH2N|28.0313:C2H4|29.0027:CHO|29.014:N2H|29.014:HN2|29.0266:CH3N|29.0391:C2H5|29.998:NO|30.0106:CH2O|30.0218:N2H2|30.0218:H2N2|30.0344:CH4N|30.047:C2H6|30.9737634:P|31.0058:HNO|31.0184:CH3O|31.0297:N2H3|31.0297:H3N2|31.0422:CH5N|31.9898:O2|32.0136:NH2O|32.0136:H2NO|32.0262:CH4O|32.0375:N2H4|32.0375:H4N2|32.9976:HO2|33.0215:NH3O|33.0215:H3NO|34.0054:O2H2|34.0054:H2O2|36:C3|37.0078:C3H|37.955882:adduct_rel_H_K|38.0031:C2N|38.0157:C3H2|39.0109:C2HN|39.0235:C3H3|39.9949:C2O|40.0062:CN2|40.0187:C2H2N|40.0313:C3H4|41.0027:C2HO|41.014:CHN2|41.0266:C2H3N|41.0391:C3H5|41.998:CNO|42.0093:N3|42.0106:C2H2O|42.0218:CH2N2|42.0344:C2H4N|42.047:C3H6|43.0058:CHNO|43.0171:HN3|43.0184:C2H3O|43.0297:CH3N2|43.0422:C2H5N|43.0548:C3H7|43.9898:CO2|44.0011:N2O|44.0136:CH2NO|44.0249:H2N3|44.0262:C2H4O|44.0375:CH4N2|44.0501:C2H6N|44.0626:C3H8|44.9976:CHO2|45.0089:HN2O|45.0215:CH3NO|45.0328:H3N3|45.034:C2H5O|45.0453:CH5N2|45.0579:C2H7N|45.9929:NO2|46.0054:CH2O2|46.0167:H2N2O|46.0293:CH4NO|46.0406:H4N3|46.0419:C2H6O|46.0532:CH6N2|47.0007:HNO2|47.0133:CH3O2|47.0248:H3N2O|47.0371:CH5NO|47.0484:H5N3|48.9925:HO3|49.0078:C4H|49.0164:H3NO2|50.0003:H2O3|50.0031:C3N|50.0157:C4H2|51.0109:C3HN|51.0235:C4H3|51.9949:C3O|52.0062:C2N2|52.0187:C3H2N|52.0313:C4H4|53.0027:C3HO|53.014:C2HN2|53.0266:C3H3N|53.0391:C4H5|53.998:C2NO|54.0093:CN3|54.0106:C3H2O|54.0218:C2H2N2|54.0344:C3H4N|54.047:C4H6|55.0058:C2HNO|55.0171:CHN3|55.0184:C3H3O|55.0297:C2H3N2|55.0422:C3H5N|55.0548:C4H7|55.9898:C2O2|56.0011:CN2O|56.0124:N4|56.0136:C2H2NO|56.0249:CH2N3|56.0262:C3H4O|56.0375:C2H4N2|56.0501:C3H6N|56.0626:C4H8|56.9976:C2HO2|57.0089:CHN2O|57.0202:HN4|57.0215:C2H3NO|57.0328:CH3N3|57.034:C3H5O|57.0453:C2H5N2|57.0579:C3H7N|57.0705:C4H9|57.9929:CNO2|58.0042:N3O|58.0054:C2H2O2|58.0167:CH2N2O|58.028:H2N4|58.0293:C2H4NO|58.0406:CH4N3|58.0419:C3H6O|58.0532:C2H6N2|58.0657:C3H8N|58.0783:C4H10|59.0007:CHNO2|59.012:HN3O|59.0133:C2H3O2|59.0246:CH3N2O|59.0359:H3N4|59.0371:C2H5NO|59.0484:CH5N3|59.0497:C3H7O|59.061:C2H7N2|59.0736:C3H9N|59.9847:CO3|59.996:N2O2|60:C5|60.0085:CH2NO2|60.0198:H2N3O|60.0211:C2H4O2|60.0324:CH4N2O|60.0437:H4N4|60.0449:C2H6NO|60.0563:CH6N3|60.0575:C3H8O|60.0688:C2H8N2|60.9925:CHO3|61.0038:HN2O2|61.0078:C5H|61.0164:CH3NO2|61.0277:H3N3O|61.0289:C2H5O2|61.0402:CH5N2O|61.0515:H5N4|61.0528:C2H7NO|61.0641:CH7N3|61.9475268:PP|61.9475268:pyrophosphate|61.9878:NO3|62.0003:CH2O3|62.0031:C4N|62.0116:H2N2O2|62.0157:C5H2|62.0242:CH4NO2|62.0368:H4N3O|62.0368:C2H6O2|62.048:CH6N2O|62.0575:C4H8O|62.0594:H6N4|62.9956:HNO3|63.0082:CH3O3|63.0109:C4HN|63.0195:H3N2O2|63.0235:C5H3|63.032:CH5NO2|63.0433:H5N3O|63.9796:O4|63.9949:C4O|64.0034:H2NO3|64.0062:C3N2|64.016:CH4O3|64.0187:C4H2N|64.0273:H4N2O2|64.0313:C5H4|64.9874:HO4|65.0027:C4HO|65.0113:N3NO3|65.014:C3HN2|65.0266:C4H3N|65.0391:C5H5|65.9953:H2O4|65.998:C3NO|66.0093:C2N3|66.0106:C4H2O|66.0218:C3H2N2|66.0344:C5H6|67.0058:C3HNO|67.0171:C2HN3|67.0184:C4H3O|67.0297:C3H3N2|67.0422:C4H5N|67.0548:C5H7|67.9898:C3O2|68.0011:C2N2O|68.0124:CN4|68.0136:C3N2NO|68.0249:C2H2N3|68.0262:C4H4O|68.0375:C3H4N2|68.05011:C4H6N|68.0626:C5H8|68.9976:C3HO2|69.0089:C2HN2O|69.0202:CHN4|69.0215:C3H3NO|69.0328:C2H3N3|69.034:C4H5O|69.0453:C3H5N2|69.0579:C4H7N|69.0705:C5H9|69.9929:C2NO2|70.0042:CN3O|70.0054:C3H2O2|70.0167:C2H2N2O|70.028:CH2N4|70.0293:C3H4NO|70.0406:C2H4N3|70.0419:C4H6O|70.0532:C3H6N2|70.0657:C4H8N|70.0783:C5H10|71.0007:C2HNO2|71.012:CHN3O|71.0133:C3H3O2|71.0246:C2H3N2O|71.0359:CH3N4|71.0371:C3H5NO|71.0484:C2H5N3|71.0497:C4H7O|71.061:C3H7N2|71.0736:C4H9N|71.0861:C5H11|71.9847:C2O3|71.996:CN2O2|72:C6|72.0073:N40|72.0085:C2H2NO2|72.0198:CH2N3O|72.0211:C3H492|72.0324:C2H4N2O|72.0449:C3H6NO|72.0497:CH4N4|72.0563:C2H6N3|72.0688:C3H8N2|72.0814:C4H10N|72.0939:C5H12|72.9925:C2HO3|73.0038:CHN2O2|73.0078:C6H|73.0151:HN40|73.0164:C2H3NO2|73.0277:CH3N3O|73.0289:C3H5O2|73.0402:C2H5N2O|73.0515:CH5N4|73.0528:C3H7NO|73.0641:C2H7N3|73.0653:C4H9O|73.0767:C3H9N2|73.0892:C4H11N|73.9878:CNO3|73.9991:N3O2|74.0003:C2H2O3|74.0031:C5N|74.0116:CH2N2O2|74.0157:C6H2|74.0229:H2N40|74.0242:C2H4NO2|74.0355:CH4N3O|74.0368:C3H6O2|74.0433:CH5N3O|74.048:C2H6N2O|74.0594:CH6N4|74.0606:C3H8NO|74.0719:C2H8N3|74.0732:C4H10O|74.0845:C3H10N2|74.9956:CHNO3|75.0069:HN3O2|75.0082:C2H3O3|75.0109:C5HN|75.0195:CH3N2O2|75.0235:C6H3|75.0308:H3N4O|75.032:C2H5NO2|75.0446:C3H7O2|75.0559:C2H7N2O|75.0672:CH7N4|75.0684:C3H9NO|75.0798:C2H9N3|75.9796:CO4|75.9949:C5O|76.0034:CH2NO3|76.0062:C4N2|76.016:C4H4O3|76.017:H2N3O2|76.0187:C5H2N|76.0273:CH4N2O2|76.0313:C6H4|76.0386:H4N4O|76.0399:C2H6NO2|76.0511:CH6N3O|76.0524:C3H8O2|76.0637:C2H8N2O|76.0653:C6H9O|76.075:CH8N4|76.9874:CHO4|76.9909:N2O3|76.9987:HN2O3|77.0027:C5HO|77.0113:CH3NO3|77.014:C4HN2|77.0226:H3N3O2|77.0238:C2H5O3|77.0266:C5H3N|77.0351:CH5N2O2|77.0391:C6H5|77.0464:H5N4O|77.059:CH7N3O|77.9827:NO4|77.9953:CH2O4|77.998:C4NO|78.0065:H2N2O3|78.0093:C3N3|78.0106:C5H2O|78.0191:CH4NO3|78.0218:C4H2N2|78.0304:H4N3O2|78.0317:C2H6O3|78.0344:C5H4N|78.0429:CH6N2O2|78.047:C6H6|78.0542:H6N4O|78.9905:HNO4|79.0031:CH3O4|79.0058:C4HNO|79.0144:H3N2O3|79.0171:C3HN3|79.0184:C5H3O|79.0269:CH5NO3|79.0297:C4H3N2|79.0382:H5N3O2|79.0422:C5H5N|79.0548:C6H7|79.95681572:SO3|79.95681572:sulfate (-H2O)|79.966332357:phosphate|79.96633236:HPO3|79.9898:C4O2|79.9983:H2NO4|80.0011:C3N2O|80.0124:C2N4|80.0136:C4H2NO|80.0222:H4N2O3|80.0249:C3H2N3|80.0262:C5H4O|80.0375:C4H4N2|80.0501:C5H6N|80.0626:C6H8|80.109:CH4O4|80.9976:C4HO2|81.0062:H3NO4|81.0089:C3HN2O|81.0202:C2HN4|81.0215:C4H3NO|81.0328:C3H3N3|81.034:C5H5O|81.0453:C4H5N2|81.0579:C5H7N|81.0705:C6H9|81.9929:C3NO2|82.0042:C2N3O|82.0054:C4H2O2|82.0167:C3H2N2O|82.028:C2H2N4|82.0293:C4H4NO|82.0406:C3H4N3|82.0419:C5H6O|82.0532:C4H6N2|82.0657:C5H8N|82.0783:C6H10|83.0007:C3HNO2|83.012:C2HN3O|83.0133:C4H3O2|83.0246:C3H3N2O|83.0359:C2H3N4|83.0371:C4H5NO|83.0484:C3H5N3|83.0497:C5H7O|83.061:C4H7N2|83.0736:C5H9N|83.0861:C6H11|83.9847:C3O3|83.996:C2N2O2|84:C7|84.0073:CN4O|84.0085:C3H2NO2|84.0198:C2H2N3O|84.0211:C4H4O2|84.0308:CH3N4O|86.00039399:C3H5NO2_Serine|87.03202848:C4H7NO2_Threonine|97.05276391:C11H10N2O_Tryptophan|99.06841398:C9H9NO2_Tyrosine|101.0476785:C5H9NO_Valine|101.0476785:C4H7NO2|103.0091856:C4H4O2_acetotacetate (-H2O)|103.0091856:C3H5NOS|110.0354368:C3H5O_acetone (-H)|110.0354368:C4H4N3O|111.0194524:C10H12N5O6P_adenylate (-H2O)|111.0194524:C4H3N2O2|113.0840641:C10H15N2O3S_biotinyl (-H)|113.0840641:C6H11NO|114.0429275:C10H14N2O2S_biotinyl (-H2O)|114.0429275:C4H6N2O2|115.0269431:CH2ON_carbamoyl P transfer (-H2PO4)|115.0269431:C4H5NO3|125.0351025:C21H34N7O16P3S_co-enzyme A (-H)|125.0351025:C5H5N2O2|128.0585776:C21H33N7O15P3S_co-enzyme A (-H2O)|128.0585776:C5H8N2O2|128.0949631:C10H15N3O5S_glutathione (-H2O)|128.0949631:C6H12N2O|129.0425932:C5H7_isoprene addition (-H)|129.0425932:C5H7NO3|131.0404858:C3H2O3_malonyl group (-H2O)|131.0404858:C5H9NOS|132.042258856:C5H8O4_D-Ribose (-H2O) (ribosylation)|132.0422589:C16H30O_palmitoylation (-H2O)|132.0422589:C5H8O4|134.0466702:C8H8NO5P_pyridoxal phosphate (-H2O)|134.0466702:C5H4N5|137.0589119:CH3N2O_urea addition (-H)|137.0589119:C6H7N3O|147.068414:C5H4N5_adenine (-H)|147.068414:C9H9NO|150.0415848:C10H11N5O3_adenosine (-H2O)|150.0415848:C5H4N5O|156.1011111:C10H13N5O9P2_Adenosine 5'-diphosphate (-H2O)|156.1011111:C6H12N4O|160.9404898:C10H12N5O6P_Adenosine 5'monophosphate (-H2O)|160.9404898:H3O6P2|162.05282357:C6H10O5_C6H10O5|162.05282357:C6H10O5_monosaccharide (-H2O)|162.0528236:C9H13N3O10P2_cytidine 5' diphosphate (-H2O)|162.0528236:C6H10O5|163.0633286:C9H12N3O7P_cytidine 5' monophsophate (-H2O)|163.0633286:C9H9NO2|176.0320881:C4H4N3O_cytosine (-H)|176.0320881:C6H8O6|176.032088136:C6H8O6_Glucuronic Acid (-H2O)|178.0477382:C10H13N5O10P2_Guanosine 5- diphosphate (-H2O)|178.0477382:C6H10O6|178.04773821:C6H10O6_C6H10O6|186.079313:C10H12N5O7P_Guanosine 5- monophosphate (-H2O)|186.079313:C11H10N2O|222.0132859:C5H4N5O_guanine (-H)|222.0132859:C6H10N2O3S2|224.079707:C10H11N5O4_guanosine (-H2O)|224.079707:C10H12N2O4|226.0589716:C10H14N2O10P2_deoxythymidine 5' diphosphate (-H2O)|226.0589716:C9H10N2O5|226.0775996:C10H12N2O4_thymidine (-H2O)|226.0775996:C10H14N2O2S|229.0140109:C5H5N2O2_thymine (-H)|229.0140109:C8H8NO5P|238.2296658:C10H13N2O7P_thymidine 5' monophosphate (-H2O)|238.2296658:C16H30O|242.0191559:C9H12N2O11P2_uridine 5' diphosphate (-H2O)|242.0191559:C6H11O8P|242.019155927:C6H11O8P_glucose-N-Phosphate (-H2O)|243.0803393:C9H11N2O8P_uridine 5' monophosphate (-H2O)|243.0803393:C10H15N2O3S|249.0861894:C4H3N2O2_uracil (-H)|249.0861894:C10H11N5O3|265.081104:C9H10N2O5_uridine (-H2O)|265.081104:C10H11N5O4|289.0732426:C10H15N3O5S|304.0460394:C10H13N2O7P|305.0412884:C9H12N3O7P|306.0253039:C9H11N2O8P|329.0525217:C10H12N5O6P|340.10056178:C12H20O11_disaccharide (-H2O)|340.1005618:H2O_condensation/dehydration|340.1005618:C12H20O11|345.0474364:H3O6P2_diphosphate|345.0474364:C10H12N5O7P|384.0123717:C10H14N2O10P2|385.0076207:C9H13N3O10P2|385.9916363:C9H12N2O11P2|409.0188541:C10H13N5O9P2|425.0137687:C10H13N5O10P2|486.1584707:C18H30O15|486.15847071:C18H30O15_trisaccharide (-H2O)|748.0968259:C21H33N7O15P3S|765.0995656:C21H34N7O16P3S".split("|")

    for parsed_annotation in parsed_anntation_list:
        if len(parsed_annotation) < 3:
            continue

        mass = abs(float(parsed_annotation.split(":")[0]))
        tag = parsed_annotation.split(":")[1]

        tag_dict = {"mass" : mass, "tag" : tag}
        pairs_annotation_list.append(tag_dict)

    return pairs_annotation_list

def main():
    parser = argparse.ArgumentParser(description='Creates alan table')
    parser.add_argument('param_xml', help='param_xml')
    parser.add_argument('path_to_spectra_filename', help='path_to_spectra_filename')
    parser.add_argument('input_clusterinfosummary', help='input_clusterinfosummary')
    parser.add_argument('input_edges', help='input_edges')
    parser.add_argument('output_selfloop_edges', help='output_filtered_edges')
    parser.add_argument('output_display_edges', help='output_display_edges')
    parser.add_argument('output_bidirection_display_edges', help='output_bidirection_display_edges')
    args = parser.parse_args()

    """Creating information for the clusters in the network"""
    cluster_to_object = {}
    for row in csv.DictReader(open(args.input_clusterinfosummary), delimiter='\t'):
        cluster_index = row["cluster index"]
        cluster_to_object[cluster_index] = row

    """Set of Annotation Edges"""
    list_of_annotations = get_annotation_list()

    #Creating output for self loop edges
    included_nodes_in_edges = set()
    edges_list = []
    for row in csv.reader(open(args.input_edges), delimiter='\t'):
        node1 = row[0]
        node2 = row[1]
        delta = row[2]
        score2 = row[3]
        cosine = row[4]
        score3 = row[5]
        component = row[6]

        included_nodes_in_edges.add(node1)
        included_nodes_in_edges.add(node2)

        edge_dict = {}
        edge_dict["CLUSTERID1"] = node1
        edge_dict["CLUSTERID2"] = node2
        edge_dict["DeltaMZ"] = delta
        edge_dict["MEH"] = score2
        edge_dict["Cosine"] = cosine
        edge_dict["OtherScore"] = score3
        edge_dict["ComponentIndex"] = component

        edge_annotation = determine_delta_annotations(float(delta), float(cluster_to_object[node1]["parent mass"]), list_of_annotations, 10.0)
        edge_annotation_string  = " "
        if len(edge_annotation) > 0:
            edge_annotation_string = ":".join(edge_annotation)
        if len(edge_annotation) == 0:
            edge_annotation_string = " "

        edge_dict["EdgeAnnotation"] = edge_annotation_string

        edges_list.append(edge_dict)

    for row in csv.DictReader(open(args.input_clusterinfosummary), delimiter='\t'):
        cluster_index = row["cluster index"]
        if not(cluster_index in included_nodes_in_edges):
            edge_dict = {}
            edge_dict["CLUSTERID1"] = cluster_index
            edge_dict["CLUSTERID2"] = cluster_index
            edge_dict["DeltaMZ"] = "0.0"
            edge_dict["MEH"] = "1.0"
            edge_dict["Cosine"] = "1.0"
            edge_dict["OtherScore"] = "1.0"
            edge_dict["ComponentIndex"] = "-1"
            edge_dict["EdgeAnnotation"] = ""

            edges_list.append(edge_dict)

    field_names = ["CLUSTERID1", "CLUSTERID2", "DeltaMZ", "MEH", "Cosine", "OtherScore", "ComponentIndex", "EdgeAnnotation"]
    output_selfloop_writer = csv.DictWriter(open(args.output_selfloop_edges, "w"), fieldnames=field_names, delimiter='\t')
    output_selfloop_writer.writeheader()
    for edge_dict in edges_list:
        output_selfloop_writer.writerow(edge_dict)

    #Creating display objects
    display_edge_list = []
    bidirection_display_edge_list = []
    for row in csv.reader(open(args.input_edges), delimiter='\t'):
        node1 = row[0]
        node2 = row[1]
        delta = row[2]
        score2 = row[3]
        cosine = row[4]
        score3 = row[5]
        component = row[6]

        edge_dict = {}
        edge_dict["Node1"] = node1
        edge_dict["Node2"] = node2
        edge_dict["MzDiff"] = delta
        edge_dict["Cos_Score"] = cosine
        edge_dict["FileName"] = args.path_to_spectra_filename

        reverse_edge_dict = {}
        reverse_edge_dict["Node2"] = node1
        reverse_edge_dict["Node1"] = node2
        reverse_edge_dict["MzDiff"] = delta
        reverse_edge_dict["Cos_Score"] = cosine
        reverse_edge_dict["FileName"] = args.path_to_spectra_filename

        display_edge_list.append(edge_dict)
        bidirection_display_edge_list.append(edge_dict)
        bidirection_display_edge_list.append(reverse_edge_dict)


    field_names = ["Node1", "Node2", "MzDiff", "Cos_Score", "FileName"]
    output_display_edges_writer = csv.DictWriter(open(args.output_display_edges, "w"), fieldnames=field_names, delimiter='\t')
    output_display_edges_writer.writeheader()
    output_bidirection_display_edges_writer = csv.DictWriter(open(args.output_bidirection_display_edges, "w"), fieldnames=field_names, delimiter='\t')
    output_bidirection_display_edges_writer.writeheader()


    for edge_dict in display_edge_list:
        output_display_edges_writer.writerow(edge_dict)

    for edge_dict in bidirection_display_edge_list:
        output_bidirection_display_edges_writer.writerow(edge_dict)

if __name__ == "__main__":
    main()
