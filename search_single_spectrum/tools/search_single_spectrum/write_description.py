import sys
import os
import proteosafe


param_obj = proteosafe.parse_xml_file(sys.argv[1])
output_filename = sys.argv[2]

output_sentences = []
output_sentences.append("<strong>Single Spectrum Search Workflow Description</strong><br><br>\n\n")
output_sentences.append("A single spectrum search was completed using the online workflow (https://ccms-ucsd.github.io/GNPSDocumentation/) on the GNPS website (http://gnps.ucsd.edu).")
if param_obj["FILTER_PRECURSOR_WINDOW"][0] == "1":
    output_sentences.append("The data was filtered by removing all MS/MS fragment ions within +/- 17 Da of the precursor m/z.")
if param_obj["WINDOW_FILTER"][0] == "1":
    output_sentences.append("MS/MS spectra were window filtered by choosing only the top 6 fragment ions in the +/- 50 Da window throughout the spectrum.")
output_sentences.append("The precursor ion mass tolerance was set to %s Da and a MS/MS fragment ion tolerance of %s Da." % (param_obj["tolerance.PM_tolerance"][0], param_obj["tolerance.Ion_tolerance"][0]))
if param_obj["FILTER_LIBRARY"][0] == "1":
    output_sentences.append("The library spectra were filtered in the same manner as the input data.")
output_sentences.append("All matches kept between input spectra and library spectra were required to have a score above %s and at least %s matched peaks." % (param_obj["SCORE_THRESHOLD"][0], param_obj["MIN_MATCHED_PEAKS"][0]))
output_sentences.append("<br><br>\n<strong>Citation</strong><br><br>\n")
output_sentences.append('Wang, Mingxun, et al. "MASST: A Web-based Basic Mass Spectrometry Search Tool for Molecules to Search Public Data." Preprint at https://doi.org/10.1101/591016')
output_sentences.append('<br><br>')

open(output_filename, "w").write(" ".join(output_sentences))
