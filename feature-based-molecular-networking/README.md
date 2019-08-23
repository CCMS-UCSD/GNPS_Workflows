## File Formats for Different Tools

### MZMine2

Feature table should have three fixed columns

1. Row ID
2. Row m/z
3. Row retention time

Additionally, to denote abundances for each file, the filename plus the suffix "Peak area" must appear. There can exist other words between the filename and "Peak area" as those will be filtered out. 

MGF output should include...

### MS-DIAL

The feature output should include 3 rows that can be ignored and headers starting in row 4 with the following column headers:

1. Alignment ID
2. Average Mz
3. Average Rt(min)

Additionally, it is assumed there are additional columns where the per sample quant starts at column 22. 


### Metaboscape

The feature table should include columns with the following header:

1. FEATURE_ID
2. RT
3. PEPMASS
4. MaxIntensity

All sample headers are not including the file format extension ".d" (DDA) or ".tdf" (PASEF) 

### Progenesis

The feature table should include 2 rows that can be ignored and headers starting in row 3 with the following the following columns:

1. Compound
2. m/z
3. Retention time (min)

### OpenMS

TODO: include updated format description, see example as format is complicated. 


### XCMS3

The feature table should include a header row with the following headers:

1. Row.names - where the feature identifier is prefixed with "FT"
2. mzmed
3. rtmed

Following these headers are the samples. 
