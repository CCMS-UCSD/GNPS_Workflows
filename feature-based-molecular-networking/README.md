## Feature Based Molecular Networking 

For more informations on FBMN, see the workflow documentation on GNPS [https://ccms-ucsd.github.io/GNPSDocumentation/featurebasedmolecularnetworking/](https://ccms-ucsd.github.io/GNPSDocumentation/featurebasedmolecularnetworking/) and our preprint: Nothias, L.F. et al [Feature-based Molecular Networking in the GNPS Analysis Environment](https://www.biorxiv.org/content/10.1101/812404v1) bioRxiv 812404 (2019).

Representative input files for each supported tools are available at:
[https://github.com/CCMS-UCSD/GNPS_Workflows/tree/master/feature-based-molecular-networking/test/reference_input_file_for_formatter](https://github.com/CCMS-UCSD/GNPS_Workflows/tree/master/feature-based-molecular-networking/test/reference_input_file_for_formatter)

Formatter script for each tool supported can be found in:
[https://github.com/CCMS-UCSD/GNPS_Workflows/tree/master/feature-based-molecular-networking/tools/feature-based-molecular-networking/scripts](https://github.com/CCMS-UCSD/GNPS_Workflows/tree/master/feature-based-molecular-networking/tools/feature-based-molecular-networking/scripts)


## Requirements for each tool supported

Beside the specific requirements for each processing tool, it is possible to map any colum from the processing tool to the molecular networks using Cytoscape. See [https://ccms-ucsd.github.io/GNPSDocumentation/featurebasedmolecularnetworking-cytoscape/#import-supplementary-annotations-in-cytoscape](https://ccms-ucsd.github.io/GNPSDocumentation/featurebasedmolecularnetworking-cytoscape/#import-supplementary-annotations-in-cytoscape).

### MZMine

The feature quantification table (.CSV file, comma separated) should have three columns named:

1. row ID
2. row m/z
3. row retention time

Additionally, to denote abundances for each file, the column name should contain the filename (with the extension) plus the suffix "Peak area" must appear. Other words can be present between the filename and "Peak area" suffixe, and those will be filtered out. 

The MGF output should contain the "SCANS" header, and it must correspond to the identifier of the "row ID". It has to be unique, and can be non sequential.

### MS-DIAL

The feature quantification table (.TXT file, tab-separated) should include upper 3 rows that are ignored and headers starting in row 4 with the following column headers:

1. Alignment ID
2. Average Mz
3. Average Rt(min)

For ion mobility data, it must include a "Average drift time" and "Average CCS" columns.

Additionally, it is assumed there are additional columns where the per sample quant starts at column 22. The sample headers are not including the filename extension (such as ".mzML")

The MGF output should contain the "SCANS" header, and it must correspond to the identifier of the "row ID". It has to be unique, and can be non sequential.

### Metaboscape

The feature quantification table (.CSV file, comma separated) should include columns with the following header:

1. FEATURE_ID
2. RT
3. PEPMASS
4. MaxIntensity

For ion mobility data, it must include a "CCS" column.

All sample headers are not including the file format extension ".d" (DDA) or ".tdf" (PASEF) 

### Progenesis QI

The feature quantification table (.CSV file, comma separated) should include 2 rows that can be ignored and headers starting in row 3 with the following the following columns:

1. Compound
2. m/z
3. Retention time (min)

For ion mobility data, it must include a "CCS (angstrom^2)" column.

All sample headers are not including the filename extension (such as ".raw")

### OpenMS

The standard output of the TextExport tools applied on a consensusXML file is used (tab-separated). See this page for format description [https://abibuilder.informatik.uni-tuebingen.de/archive/openms/Documentation/release/latest/html/TOPP_TextExporter.html](https://abibuilder.informatik.uni-tuebingen.de/archive/openms/Documentation/release/latest/html/TOPP_TextExporter.html)

All sample headers should include the filename extension (such as ".mzML").

The MGF output should contain the "SCANS" header, and it must correspond to the identifier of the "row ID". It has to be unique, and can be non sequential.

### XCMS3

The feature quantification table (.TXT format, tab-separated) should include a header row with the following headers:

1. Row.names - where the feature identifier is prefixed with "FT"
2. mzmed
3. rtmed

Following these headers are the samples. 

The MGF output should contain the "SCANS" header, and it must correspond to the identifier of the "row ID". It has to be unique, and can be non sequential.
