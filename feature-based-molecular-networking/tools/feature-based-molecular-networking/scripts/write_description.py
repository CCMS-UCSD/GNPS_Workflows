# coding: utf-8
import sys
import os
import ming_proteosafe_library

def write_description(param_xml_filename, output_description_filename):
    param_obj = ming_proteosafe_library.parse_xml_file(open(param_xml_filename))
    output_filename = output_description_filename

    output_sentences = []
    #INTRODUCTION
    output_sentences.append('<strong>Molecular Networking and Spectral Library Search</strong><br><br>\n')
    output_sentences.append('A molecular network was created with the Feature-Based Molecular Networking (FBMN) workflow (<a href="https://www.nature.com/articles/s41592-020-0933-6">Nothias L-F, Petras D, Schmid R et al. Nature Methods 17, 905–908 (2020)</a>) on GNPS (<a href="https://gnps.ucsd.edu">https://gnps.ucsd.edu</a>, <a href="https://doi.org/10.1038/nbt.3597"> Wang M et al. Nat. Biotech. 2016</a>). \n')


    #FBMN PROCESSING
    output_sentences.append('The mass spectrometry data were first processed with %s (cite accordingly, see below in the <strong>Citations</strong> section) and the results were exported to GNPS for FBMN analysis.' % (param_obj["QUANT_TABLE_SOURCE"][0]))

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
    if param_obj["ANALOG_SEARCH"][0] == "0":
        output_sentences.append('The spectra in the network were then searched against GNPS spectral libraries (Cite <a href="https://doi.org/10.1038/nbt.3597"> Wang M, et al. Nature Biotech. 2016 </a> and <a href="https://doi.org/10.1002/jms.1777"> Horai, H. et al. J. Mass Spectrom. 45, 703-714 2010)</a>.')
    if param_obj["ANALOG_SEARCH"][0] == "1":
        output_sentences.append('The analogue search mode was used by searching against MS/MS spectra with a maximum difference of %s in the precursor ion value.' % (param_obj["MAX_SHIFT_MASS"][0]))
    if param_obj["FILTER_LIBRARY"][0] == "1":
        output_sentences.append('The library spectra were filtered in the same manner as the input data.')
    output_sentences.append('All matches kept between network spectra and library spectra were required to have a score above %s and at least %s matched peaks.' % (param_obj["SCORE_THRESHOLD"][0], param_obj["MIN_MATCHED_PEAKS_SEARCH"][0]))
    if param_obj["QUANT_FILE_NORM"][0] == "1":
        output_sentences.append('The row intensities of the feature quantification table were normalized to 1.')
    if param_obj["GROUP_COUNT_AGGREGATE_METHOD"][0] == "0":
        output_sentences.append('The group value of the metadata was calculated by summing the intensity of all files intensity within a group.')
    if param_obj["GROUP_COUNT_AGGREGATE_METHOD"][0] == "1":
        output_sentences.append('The group value of the metadata was calculated by using the mean value all files intensity within a group.')
    if param_obj["RUN_DEREPLICATOR"][0] == "1":
            output_sentences.append('The DEREPLICATOR was used to annotate MS/MS spectra (<a href="https://dx.doi.org/10.1038/s41467-018-06082-8">Mohimani, H. et al. Nat. Commun. 9, 4035 (2018)</a>).')
    if "additional_pairs" in param_obj:
            output_sentences.append('Additional edges were provided by the user.')

    #NETWORK VISUALIZATION
    output_sentences.append('The molecular networks were visualized using Cytoscape software (<a href="https://dx.doi.org/10.1101/gr.1239303">Shannon, P. et al. Genome Res. 13, 2498-2504 (2003)</a>). \n')

    #DATA DEPOSITION AND JOB ACCESSIBILITY
    output_sentences.append('<br><br>\n<strong>Data Deposition and Job Accessibility</strong><br><br>\n')
    output_sentences.append('The mass spectrometry data were deposited on public repository (provide the deposition accession number), such as <a href="https://massive.ucsd.edu">MassIVE</a> or <a href="https://www.ebi.ac.uk/metabolights/MetaboLights">MetaboLights</a>.\n')
    output_sentences.append('The molecular networking job can be publicly accessed at <a href="https://gnps.ucsd.edu/ProteoSAFe/status.jsp?task={}">https://gnps.ucsd.edu/ProteoSAFe/status.jsp?task={}</a> (we recommend sharing this link in your manuscript).' .format(param_obj["task"][0],param_obj["task"][0]))

    #CITATIONS
    output_sentences.append('<br><br>\n<strong>Citations</strong><br><br>\n')
    output_sentences.append('<strong>For Feature-Based Molecular Networking</strong>: Nothias LF, Petras D, Schmid R et al. Feature-based Molecular Networking in the GNPS Analysis Environment. bioRxiv 812404 (2019). <a href="https://doi.org/10.1101/812404"> https://doi.org/10.1101/812404</a>. \n')
    output_sentences.append('<br><br><strong>For the GNPS web-platform</strong>: Wang M et al. Sharing and community curation of mass spectrometry data with Global Natural Products Social Molecular Networking. Nature Biotechnology 34.8 (2016): 828-837. <a href="https://doi.org/10.1038/nbt.3597">https://doi.org/10.1038/nbt.3597</a>. \n')
    output_sentences.append('<br><br><strong>If Ion-Identity Molecular Networking was performed: Schmid R, Petras D, Nothias LF, et al. Ion Identity Molecular Networking in the GNPS Environment, BioRxiv (2020),  <a href="https://doi.org/10.1101/2020.05.11.08894">https://doi.org/10.1101/2020.05.11.088948</a>. \n')

    #PROCESSING CITATION
    if param_obj["QUANT_TABLE_SOURCE"][0] == "MZMINE2":
        output_sentences.append('<br><br> <strong>For MZmine2</strong>: Pluskal T et al. MZmine 2: modular framework for processing, visualizing, and analyzing mass spectrometry-based molecular profile data. BMC Bioinformatics 11, 395 (2010), <a href="https://doi.org/10.1186/1471-2105-11-395">https://doi.org/10.1186/1471-2105-11-395</a>. \n')
        output_sentences.append('Katajamaa M. et al, MZmine: toolbox for processing and visualization of mass spectrometry based molecular profile data. Bioinformatics 22, 634-636 (2006), <a href="https://doi.org/10.1093/bioinformatics/btk039">https://doi.org/10.1093/bioinformatics/btk039</a>. \n')
    if param_obj["QUANT_TABLE_SOURCE"][0] == "XCMS3":
        output_sentences.append('<br><br> <strong>For XCMS</strong>: Tautenhahn R et al. Highly sensitive feature detection for high resolution LC/MS. BMC Bioinformatics 9, 504 (2008), <a href="https://dx.doi.org/10.1186/1471-2105-9-504">https://dx.doi.org/10.1186/1471-2105-9-504</a> and other citations if applicable, such as the XCMS3 repository at <a href="https://github.com/sneumann/xcms">https://github.com/sneumann/xcms</a>. \n')
        output_sentences.append('If you used CAMERA in XCMS: Kuhl et al. CAMERA: An Integrated Strategy for Compound Spectra Extraction and Annotation of Liquid Chromatography/Mass Spectrometry Data Sets. Anal. Chem., 841283-289 (2012),<a href="https://doi.org/10.1021/ac202450g">https://doi.org/10.1021/ac202450g</a>. \n')
    if param_obj["QUANT_TABLE_SOURCE"][0] == "MSDIAL":
        output_sentences.append('<br><br> <strong>For MS-DIAL</strong>: Tsugawa H et al. MS-DIAL: data-independent MS/MS deconvolution for comprehensive metabolome analysis. Nature Methods 12, 523-526 (2015), <a href="https://doi.org/10.1038/nmeth.3393">https://doi.org/10.1038/nmeth.3393.</a> \n')
    if param_obj["QUANT_TABLE_SOURCE"][0] == "OPENMS":
        output_sentences.append('<br><br> <strong>For OpenMS</strong>: Rost HL et al. OpenMS: a flexible open-source software platform for mass spectrometry data analysis. Nature Methods 13, 741-748 (2016), <a href="https://doi.org/10.1038/nmeth.3959">https://doi.org/10.1038/nmeth.3959.</a> \n')
    if param_obj["QUANT_TABLE_SOURCE"][0] == "OPTIMUS":
        output_sentences.append('<br><br> <strong>For Optimus</strong>: Protsyuk I et al. 3D molecular cartography using LC-MS facilitated by Optimus and ili software. Nature Protocols 13, 134-154 (2018), <a href="https://doi.org/10.1038/nprot.2017.122">https://doi.org/10.1038/nprot.2017.122.</a> \n')
    if param_obj["QUANT_TABLE_SOURCE"][0] == "METABOSCAPE":
        output_sentences.append('<br><br> <strong>For MetaboScape</strong>: MetaboScape, Bruker Daltonics GmbH, Bremen, Germany, version [specify the version]. Software available at <a href="https://www.bruker.com/products/mass-spectrometry-and-separations/ms-software/metaboscape.html">https://www.bruker.com/products/mass-spectrometry-and-separations/ms-software/metaboscape.html.</a> \n')
    if param_obj["QUANT_TABLE_SOURCE"][0] == "PROGENESIS":
        output_sentences.append('<br><br> <strong>For Progenesis QI</strong>: Progenesis QI, Nonlinear Dynamics, Milford, MA, version [specify the version]. Software available at <a href="https://www.nonlinear.com/progenesis/qi/">https://www.nonlinear.com/progenesis/qi/</a>. \n')
    if param_obj["QUANT_TABLE_SOURCE"][0] == "MZTABM":
        output_sentences.append('<br><br> <strong>For mzTab-M</strong>: Hoffman et al. mzTab-M: A Data Standard for Sharing Quantitative Results in Mass Spectrometry Metabolomic. Analytical Chemistry 9153302-3310 (2019), <a href="https://doi.org/10.1021/acs.analchem.8b04310">https://doi.org/10.1021/acs.analchem.8b04310></a>. \n')
    if param_obj["QUANT_TABLE_SOURCE"][0] == "SIRIUS":
        output_sentences.append('<br><br> <strong>For SIRIUS</strong>: the processing was introduced in that preprint: Hoffman et al, Assigning confidence to structural annotations from mass spectra with COSMIC, BioRxiv 2021. <a href="https://www.biorxiv.org/content/10.1101/2021.03.18.435634v1">https://www.biorxiv.org/content/10.1101/2021.03.18.435634v1</a>. For other SIRIUS related citations, see <a href="https://boecker-lab.github.io/docs.sirius.github.io/#literature">https://boecker-lab.github.io/docs.sirius.github.io/#literature</a>.\n')


    #DEREPLICATOR ifitwas used
    if param_obj["RUN_DEREPLICATOR"][0] == "1":
        output_sentences.append('<br><br> <strong> For the DEREPLICATOR</strong>: Mohimani, H. et al. Dereplication of microbial metabolites through database search of mass spectra, Nature Communications 9, 4035 (2018), <a href="https://dx.doi.org/10.1038/s41467-018-06082-8">https://dx.doi.org/10.1038/s41467-018-06082-8.</a> \n')
        output_sentences.append('<br><br> <strong> For the DEREPLICATOR VarQuest</strong>: Gurevich, A. et al. Increased diversity of peptidic natural products revealed by modification-tolerant database search of mass spectra. Nature Microbiology 3, 319-327 (2018), <a href="https://dx.doi.org/10.1038/s41564-017-0094-2">https://dx.doi.org/10.1038/s41564-017-0094-2</a>.')

    #NETWORK VISUALIZER
    output_sentences.append('<br><br>\n<strong>Additional Citations</strong><br><br>\n')
    output_sentences.append('If you used the molecular network web-based visualiser:  Ono, K., Demchak, B. and Ideker, T. Cytoscape tools for the web age: D3.js and Cytoscape.js exporters. F1000Res. 3, 143 (2014), <a href="https://dx.doi.org/10.12688/f1000research.4510.2">https://dx.doi.org/10.12688/f1000research.4510.2</a>.')

    output_sentences.append('<br><br>\n<strong>Disclaimer</strong><br><br>\n')
    output_sentences.append('This description is generated to facilitate the report and the reproducibility of the analysis. It also provides the citation of the tools used. Note that if copy/pasted as is in your manuscript, it might be flagged as plagiarism by the editor. For that reason, we recommend cautiouness and using it as a guideline.')
    open(output_filename, "w").write(" ".join(output_sentences))

def main():
    write_description(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
