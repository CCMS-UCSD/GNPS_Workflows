import sys
import os
import ming_proteosafe_library


param_obj = ming_proteosafe_library.parse_xml_file(open(sys.argv[1]))
output_filename = sys.argv[2]

output_sentences = []
output_sentences.append("<strong>Network Description</strong><br><br>\n\n")
output_sentences.append("A molecular network was created with the feature based molecular networking workflow (https://ccms-ucsd.github.io/GNPSDocumentation/featurebasedmolecularnetworking/) on the GNPS website (http://gnps.ucsd.edu).")
if param_obj["FILTER_PRECURSOR_WINDOW"][0] == "1":
    output_sentences.append("The data was filtered by removing all MS/MS fragment ions within +/- 17 Da of the precursor m/z.")
if param_obj["WINDOW_FILTER"][0] == "1":
    output_sentences.append("MS/MS spectra were window filtered by choosing only the top 6 fragment ions in the +/- 50Da window throughout the spectrum.")
output_sentences.append("The precursor ion mass tolerance was set to %s Da and a MS/MS fragment ion tolerance of %s Da." % (param_obj["tolerance.PM_tolerance"][0], param_obj["tolerance.Ion_tolerance"][0]))
output_sentences.append("A network was then created where edges were filtered to have a cosine score above %s and more than %s matched peaks." % (param_obj["PAIRS_MIN_COSINE"][0], param_obj["MIN_MATCHED_PEAKS"][0]))
output_sentences.append("Further, edges between two nodes were kept in the network if and only if each of the nodes appeared in each other's respective top %s most similar nodes." % (param_obj["TOPK"][0]))
output_sentences.append("Finally, the maximum size of a molecular family was set to %s, and the lowest scoring edges were removed from molecular families until the molecular family size was below this threshold." % (param_obj["MAXIMUM_COMPONENT_SIZE"][0]))
output_sentences.append("The spectra in the network were then searched against GNPS' spectral libraries.")
if param_obj["FILTER_LIBRARY"][0] == "1":
    output_sentences.append("The library spectra were filtered in the same manner as the input data.")
output_sentences.append("All matches kept between network spectra and library spectra were required to have a score above %s and at least %s matched peaks." % (param_obj["SCORE_THRESHOLD"][0], param_obj["MIN_MATCHED_PEAKS_SEARCH"][0]))
output_sentences.append("<br><br>\n<strong>Citation</strong><br><br>\n")
output_sentences.append('Wang, Mingxun, et al. "Sharing and community curation of mass spectrometry data with Global Natural Products Social Molecular Networking." Nature Biotechnology 34.8 (2016): 828-837. PMID: 27504778, https://www.nature.com/articles/nbt.3597')

open(output_filename, "w").write(" ".join(output_sentences))
