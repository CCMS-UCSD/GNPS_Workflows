# coding: utf-8
import sys
import os
import ming_proteosafe_library

def write_description(param_xml_filename, output_description_filename):
    param_obj = ming_proteosafe_library.parse_xml_file(open(param_xml_filename))
    output_filename = output_description_filename

    output_sentences = []
    #INTRODUCTION
    output_sentences.append('<strong>Library Search/Molecular Networking GC workflow</strong><br><br>\n')
    output_sentences.append('A molecular network was created with the Library Search/Molecular Networking GC workflow at GNPS (<a href="https://gnps.ucsd.edu">https://gnps.ucsd.edu</a>, <a href="https://doi.org/10.1038/nbt.3597"> Wang M et al. Nat. Biotech. 2016</a>).')

    #SPECTRAL PROCESSING
    if param_obj["FILTER_PRECURSOR_WINDOW"][0] == "1":
        output_sentences.append('The data was filtered by removing all MS/MS fragment ions within +/- 17 Da of the precursor m/z.')
    if param_obj["WINDOW_FILTER"][0] == "1":
        output_sentences.append('MS/MS spectra were window filtered by choosing only the top 6 fragment ions in the +/- 50 Da window throughout the spectrum.')
    if float(param_obj["MIN_PEAK_INT"][0]) > 0.5:
        output_sentences.append('The minimum fragment ion intensity in the MS/MS spectra was set to %s' % (param_obj["MIN_PEAK_INT"][0]))

    #MOLECULAR NETWORKING
    output_sentences.append('The precursor ion mass tolerance was set to %s Da and the MS/MS fragment ion tolerance to %s Da.' % (param_obj["tolerance.PM_tolerance"][0], param_obj["tolerance.Ion_tolerance"][0]))
    output_sentences.append('A molecular network was then created where edges were filtered to have a cosine score above %s and more than %s matched peaks.' % (param_obj["PAIRS_MIN_COSINE"][0], param_obj["MIN_MATCHED_PEAKS"][0]))
    output_sentences.append('Further, edges between two nodes were kept in the network if and only if each of the nodes appeared in each others respective top %s most similar nodes.' % (param_obj["TOPK"][0]))
    output_sentences.append('Finally, the maximum size of a molecular family was set to %s, and the lowest scoring edges were removed from molecular families until the molecular family size was below this threshold.' % (param_obj["MAXIMUM_COMPONENT_SIZE"][0]))

    #SPECTRAL LIBRARY SEARCH
    if param_obj["FILTER_LIBRARY"][0] == "1":
        output_sentences.append('The library spectra were filtered in the same manner as the input data.')
    output_sentences.append('All matches kept between network spectra and library spectra were required to have a score above %s and at least %s matched peaks.' % (param_obj["SCORE_THRESHOLD"][0], param_obj["MIN_MATCHED_PEAKS"][0]))

    #NETWORK VISUALIZATION
    output_sentences.append('The molecular networks were visualized using Cytoscape software (<a href="https://dx.doi.org/10.1101/gr.1239303">Shannon, P. et al. Genome Res. 13, 2498-2504 (2003)</a>). \n')

    #CITATIONS
    output_sentences.append('<br><br>\n<strong>Citations</strong><br><br>\n')
    output_sentences.append('For the GNPS web-platform: Wang M et al. Sharing and community curation of mass spectrometry data with Global Natural Products Social Molecular Networking. Nature Biotechnology 34.8 (2016): 828-837. <a href="https://doi.org/10.1038/nbt.3597">https://doi.org/10.1038/nbt.3597</a>. \n')

    output_sentences.append('<br><br>\n<strong>Disclaimer</strong><br><br>\n')
    output_sentences.append('This description is generated to facilitate the report and the reproducibility of the analysis. It also provides the citation of the tools used. Note that if copy/pasted as is in your manuscript, it might be flagged as plagiarism by the editor. For that reason, we recommend cautiouness and using it as a guideline.')
    open(output_filename, "w").write(" ".join(output_sentences))

def main():
    write_description(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
