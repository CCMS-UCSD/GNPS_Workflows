import sys
import os
import ming_proteosafe_library


param_obj = ming_proteosafe_library.parse_xml_file(open(sys.argv[1]))
output_filename = sys.argv[2]

output_sentences = []
#INTRODUCTION
output_sentences.append("<strong>Network Description</strong><br><br>\n\n")
output_sentences.append("A molecular network was created with the Feature-Based Molecular Networking (FBMN) workflow (Nothias LF et al. bioRxiv 2019, https://doi.org/10.1101/812404) on GNPS (http://gnps.ucsd.edu, Wang M et al. Nat. Biotech. 2016, https://doi.org/10.1038/nbt.3597).")
#PROCESSING MASS SPEC PART
output_sentences.append("The mass spectrometry data were first processed with %s (please cite accordingly) and the results were exported to GNPS for FBMN analysis." % (param_obj["QUANT_TABLE_SOURCE"][0]))
#SPECTRAL PROCESSING
if param_obj["FILTER_PRECURSOR_WINDOW"][0] == "1":
    output_sentences.append("The data was filtered by removing all MS/MS fragment ions within +/- 17 Da of the precursor m/z.")
if param_obj["WINDOW_FILTER"][0] == "1":
    output_sentences.append("MS/MS spectra were window filtered by choosing only the top 6 fragment ions in the +/- 50 Da window throughout the spectrum.")
if int(param_obj["MIN_PEAK_INT"][0]) >= 1:
    output_sentences.append("The minimum fragment ion intensity in the MS/MS spectra was set to %s." % (param_obj["MIN_PEAK_INT"][0]))
#MOLECULAR NETWORKING
output_sentences.append("The precursor ion mass tolerance was set to %s Da and the MS/MS fragment ion tolerance to %s Da." % (param_obj["tolerance.PM_tolerance"][0], param_obj["tolerance.Ion_tolerance"][0]))
output_sentences.append("A molecular network was then created where edges were filtered to have a cosine score above %s and more than %s matched peaks." % (param_obj["PAIRS_MIN_COSINE"][0], param_obj["MIN_MATCHED_PEAKS"][0]))
output_sentences.append("Further, edges between two nodes were kept in the network if and only if each of the nodes appeared in each other's respective top %s most similar nodes." % (param_obj["TOPK"][0]))
output_sentences.append("Finally, the maximum size of a molecular family was set to %s, and the lowest scoring edges were removed from molecular families until the molecular family size was below this threshold." % (param_obj["MAXIMUM_COMPONENT_SIZE"][0]))
#SPECTRAL LIBRARY SEARCH
if param_obj["ANALOG_SEARCH"][0] == "0":
    output_sentences.append("The spectra in the network were then searched against GNPS' spectral libraries (Cite Wang M, et al. Nature Biotech. 2016 https://doi.org/10.1038/nbt.3597 and Horai, H. et al. J. Mass Spectrom. 45, 703–714 (2010), https://doi.org/10.1002/jms.1777.")
if param_obj["ANALOG_SEARCH"][0] == "1":
    output_sentences.append("The analogue search mode was used by searching against MS/MS spectra with a maximum difference of %s in the precursor ion value." % (param_obj["MAX_SHIFT_MASS"][0]))
if param_obj["FILTER_LIBRARY"][0] == "1":
    output_sentences.append("The library spectra were filtered in the same manner as the input data.")
output_sentences.append("All matches kept between network spectra and library spectra were required to have a score above %s and at least %s matched peaks." % (param_obj["SCORE_THRESHOLD"][0], param_obj["MIN_MATCHED_PEAKS_SEARCH"][0]))
if param_obj["QUANT_FILE_NORM"][0] == "1":
    output_sentences.append("The row intensities of the feature quantification table were normalized to 1.")
if param_obj["GROUP_COUNT_AGGREGATE_METHOD"][0] == "0":
    output_sentences.append("The group value of the metadata was calculated by summing the intensity of all files intensity within a group.")
if param_obj["GROUP_COUNT_AGGREGATE_METHOD"][0] == "1":
    output_sentences.append("The group value of the metadata was calculated by using the mean value all files intensity within a group.")
if param_obj["RUN_DEREPLICATOR"][0] == "1":
        output_sentences.append("The DEREPLICATOR was used to annotate the MS/MS spectra (Mohimani, H. et al. Nat. Commun. 9, 4035 (2018), http://dx.doi.org/10.1038/s41467-018-06082-8)")
if param_obj["additional_pairs"][0] == "1":
        output_sentences.append("Additional edges were provided by the user.")
#NETWORK VISUALIZATION
output_sentences.append("The molecular networks were visualized using Cytoscape software (Shannon, P. et al. Genome Res. 13, 2498–2504 (2003), https://dx.doi.org/10.1101%2Fgr.1239303), and/or the Cytoscape tools for the web-based visualization F1000Res. 3, 143 (2014), http://dx.doi.org/10.12688/f1000research.4510.2.')
output_sentences.append("The molecular networking job can be accessed at %s .") % (param_obj["JOBID"][0]))
output_sentences.append("The mass spectrometry data were deposited on public repository (provide repository accession number), such as MassIVE (http://massive.ucsd.edu) or MetaboLights (https://www.ebi.ac.uk/metabolights/).")

#CITATIONS
output_sentences.append("<br><br>\n<strong>Citation</strong><br><br>\n")
output_sentences.append('For Feature-Based Molecular Networking: Nothias LF et al. Feature-based Molecular Networking in the GNPS Analysis Environment. bioRxiv 812404 (2019). https://doi.org/10.1101/812404')
output_sentences.append('For the GNPS web-platform: Wang M et al. "Sharing and community curation of mass spectrometry data with Global Natural Products Social Molecular Networking." Nature Biotechnology 34.8 (2016): 828-837. PMID: 27504778, https://doi.org/10.1038/nbt.3597')

#PROCESSING CITATION
if param_obj["QUANT_TABLE_SOURCE"][0] == "MZMINE2":
    output_sentences.append("Pluskal T et al. MZmine 2: modular framework for processing, visualizing, and analyzing mass spectrometry-based molecular profile data. BMC Bioinformatics 11, 395 (2010), https://doi.org/10.1093/bioinformatics/btk039.")
    output_sentences.append("Katajamaa M. et al, MZmine: toolbox for processing and visualization of mass spectrometry based molecular profile data. Bioinformatics 22, 634–636 (2006), https://doi.org/10.1186/1471-2105-11-395.")

if param_obj["QUANT_TABLE_SOURCE"][0] == "XCMS3":
        output_sentences.append("For XCMS: Tautenhahn R et al. Highly sensitive feature detection for high resolution LC/MS. BMC Bioinformatics 9, 504 (2008), http://dx.doi.org/10.1186/1471-2105-9-504. See the XCMS3 repository at https://github.com/sneumann/xcms.")
if param_obj["QUANT_TABLE_SOURCE"][0] == "MSDIAL":
        output_sentences.append("for MS-DIAL: Tsugawa H et al. MS-DIAL: data-independent MS/MS deconvolution for comprehensive metabolome analysis. Nature Methods 12, 523-526 (2015), https://doi.org/10.1038/nmeth.3393.")
if param_obj["QUANT_TABLE_SOURCE"][0] == "OPENMS":
        output_sentences.append("For OpenMS: Röst HL et al. OpenMS: a flexible open-source software platform for mass spectrometry data analysis. Nature Methods 13, 741–748 (2016), https://doi.org/10.1038/nmeth.3959")
if param_obj["QUANT_TABLE_SOURCE"][0] == "OPTIMUS":
        output_sentences.append("For Optimus: Protsyuk I et al. 3D molecular cartography using LC–MS facilitated by Optimus and’ili software. Nature Protocols 13, 134–154 (2018), https://doi.org/10.1038/nprot.2017.122")
if param_obj["QUANT_TABLE_SOURCE"][0] == "METABOSCAPE":
        output_sentences.append("For MetaboScape: MetaboScape, Bruker Daltonics GmbH, Bremen, Germany, version [specify the version]. Software available at https://www.bruker.com/products/mass-spectrometry-and-separations/ms-software/metaboscape.html.")
if param_obj["QUANT_TABLE_SOURCE"][0] == "PROGENESIS":
        output_sentences.append("For Progenesis QI: Progenesis QI, Nonlinear Dynamics, Milford, MA, version [specify the version]. Software available at https://www.nonlinear.com/progenesis/qi/")
if param_obj["QUANT_TABLE_SOURCE"][0] == "MZTABM":
        output_sentences.append("For mzTab-M: Hoffman et al. mzTab-M: A Data Standard for Sharing Quantitative Results in Mass Spectrometry Metabolomic. Analytical Chemistry 9153302-3310 (2019), https://doi.org/10.1021/acs.analchem.8b04310")

#DEREPLICATOR if used
if param_obj["RUN_DEREPLICATOR"][0] == "1":
        output_sentences.append("The DEREPLICATOR: Mohimani, H. et al. Dereplication of microbial metabolites through database search of mass spectra, Nature Communications 9, 4035 (2018), http://dx.doi.org/10.1038/s41467-018-06082-8)")
        output_sentences.append("The DEREPLICATOR VarQuest: Gurevich, A. et al. Increased diversity of peptidic natural products revealed by modification-tolerant database search of mass spectra. Nature Microbiology 3, 319–327 (2018), http://dx.doi.org/10.1038/s41564-017-0094-2)")

#NETWORK VISUALIZER
output_sentences.append("<br><br>\n<strong>Additional citations</strong><br><br>\n")
output_sentences.append('If you used the Cytoscape software:  Shannon, P. et al. Cytoscape: a software environment for integrated models of biomolecular interaction networks. Genome Res. 13, 2498–2504 (2003), https://dx.doi.org/10.1101%2Fgr.1239303')
output_sentences.append('If you used the network web-based visualiser:  Ono, K., Demchak, B. & Ideker, T. Cytoscape tools for the web age: D3.js and Cytoscape.js exporters. F1000Res. 3, 143 (2014), http://dx.doi.org/10.12688/f1000research.4510.2')

output_sentences.append("Nota bene: this description is generated to facilitate the report and citation of the tools. If it is pasted in your manuscript, it might be flagged as plagiarism by the editor, so we recommend cautiouness.")
open(output_filename, "w").write(" ".join(output_sentences))
