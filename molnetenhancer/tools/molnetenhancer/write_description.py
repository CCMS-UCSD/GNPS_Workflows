import sys
import os
import proteosafe

param_obj = proteosafe.parse_xml_file(open(sys.argv[1]))
output_filename = sys.argv[2]

NAP_TASK = param_obj["NAP_TASK"][0]
DEREPLICATOR_TASK = param_obj["DEREPLICATOR_TASK"][0]
VARQUEST_TASK = param_obj["VARQUEST_TASK"][0]
MS2LDA_TASK = param_obj["MS2LDA_TASK"][0]

included_tools = ["GNPS Library Search"]
if len(NAP_TASK) > 10:
    included_tools.append("Network Annotation Propogation")
if len(DEREPLICATOR_TASK) > 10:
    included_tools.append("Dereplicator")
if len(VARQUEST_TASK) > 10:
    included_tools.append("Varquest")

output_sentences = []
output_sentences.append("""<strong>MolNetEnhancer Workflow Description for chemical class annotation of molecular networks</strong><br><br>\n\n
To enhance chemical structural information within the molecular network, information from in silico structure annotations from {} 
were incorporated into the network using the GNPS MolNetEnhancer workflow (https://ccms-ucsd.github.io/GNPSDocumentation/molnetenhancer/) 
on the GNPS website (http://gnps.ucsd.edu). Chemical class annotations were performed using the ClassyFire chemical ontology.""".format(", ".join(included_tools)))

output_sentences.append("<br><br>\n<strong>Citation</strong><br><br>\n")
output_sentences.append('Ernst, Madeleine, et al. "MolNetEnhancer: Enhanced Molecular Networks by Integrating Metabolome Mining and Annotation Tools". Metabolites 9.7 (2019): 144. PMID: 31315242, https://www.mdpi.com/2218-1989/9/7/144')
output_sentences.append('<br><br>')
output_sentences.append('Wang, Mingxun, et al. "Sharing and community curation of mass spectrometry data with Global Natural Products Social Molecular Networking." Nature Biotechnology 34.8 (2016): 828-837. PMID: 27504778, https://www.nature.com/articles/nbt.3597')
output_sentences.append('<br><br>')
output_sentences.append('Feunang, Yannick Djoumbou, et al. "ClassyFire: Automated chemical classification with a comprehensive, computable taxonomy." J. Cheminform. 8 (2016): 61. PMID: 27867422, https://jcheminf.biomedcentral.com/articles/10.1186/s13321-016-0174-y')
output_sentences.append('<br><br>')
if len(NAP_TASK) > 10:
    output_sentences.append('Da Silva, Ricardo R., et al. "Propagating annotations of molecular networks using in silico fragmentation". PLoS Comput. Biol. 14, (2018): e1006089. PMID: 29668671, https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006089 ')
    output_sentences.append('<br><br>')
if len(DEREPLICATOR_TASK) > 10:
    output_sentences.append('Mohimani, Hosein, et al. "Dereplication of peptidic natural products through database search of mass spectra". Nat. Chem. Biol. 13, (2017):30–37. PMID: 27820803, https://www.nature.com/articles/nchembio.2219 ')
    output_sentences.append('<br><br>')
if len(VARQUEST_TASK) > 10:
    output_sentences.append('Gurevich, Alexey, et al. "Increased diversity of peptidic natural products revealed by modification-tolerant database search of mass spectra". Nat. Microbiol. 3, (2018): 319–327. PMID: 29358742, https://www.nature.com/articles/s41564-017-0094-2')
    output_sentences.append('<br><br>')
if len(MS2LDA_TASK) > 10:
    output_sentences.append('Wandy, Joe, et al. "Ms2lda. org: web-based topic modelling for substructure discovery in mass spectrometry." Bioinformatics 34.2 (2017): 317-318. PMID: 28968802, https://academic.oup.com/bioinformatics/article-lookup/doi/10.1093/bioinformatics/btx582')
    output_sentences.append('<br><br>')

open(output_filename, "w").write(" ".join(output_sentences))
