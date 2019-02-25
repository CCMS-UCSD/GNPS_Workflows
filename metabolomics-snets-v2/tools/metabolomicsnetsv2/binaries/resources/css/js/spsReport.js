////////////////////////////////////////////////////////////////////////////////
// spsReport dynamic generation
//
// By jcanhita@eng.ucsd.edu on nov/2011
//
////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////////////

// report entry point & internal components
var INITIAL_PAGE = "index.html";

var PAGE_FIELD_CELLS_PER_LINE     = "cellsPerLine";
var PAGE_FIELD_SERVER             = "serverLocation";
var PAGE_FIELD_TABLES_DIR         = "tablesDir";
var PAGE_FIELD_PROJECT_DIR        = "projectDir";
var PAGE_FIELD_FASTA_FILENAME     = "fastaFilename";
var PAGE_FIELD_SPECS_MS_FILENAME  = "msFilename";
var PAGE_FIELD_NO_CLUSTERS        = "noClusters";
var PAGE_FIELD_TABLES_LOAD        = "tableLoad";
var PAGE_FIELD_TABLES_RELOAD      = "tableReload";
var PAGE_FIELD_SERVER_UPDATE      = "serverUpdate";
var PAGE_FIELD_SERVER_IMAGES      = "serverImages";
var PAGE_FIELD_DYNAMIC            = "dynamic";

// table ID for reportServer
var TABLE_PROTEIN_ID  = 2;
var TABLE_CONTIG_ID   = 3;
var TABLE_CLUSTER_ID  = 4;
var TABLE_SPECTRA_ID  = 5;
var TABLE_COVERAGE_ID = 6;

// table in field separators.
var TABLE_SEP_L1 = "|";
var TABLE_SEP_L2 = "@";
var TABLE_SEP_L3 = "&";
var TABLE_SEP_L4 = "!";

// IDs for objects
var PEP_ELEM_PREFIX = "PEP";  // peptide element in protein coverage page
var INP_ELEM_PREFIX = "INP";  // peptide input element in protein coverage page

// CSV file separator
var CSV_SEP = ";";

// number of elements per page
var PAGE_LENGTH = 10;

// Cells per line in protein coverage reports pages
var CELLS_PER_LINE = 20;

// Is the report dynamic?
var DYNAMIC = true;

// Load tables from server
var TABLES_LOAD = true;

// Reload each table when drawing a table?
var TABLES_RELOAD = false;

// Commit table updated to the server?
var SERVER_UPDATE = true ; //false;

// Specifies if the images may be aquired from the server
var SERVER_IMAGES = true;

// Amino acids per line in protein sequence, in proteins page
var AAS_PER_LINE = 50;

// Amino acids group size in protein sequence, in proteins page
var AAS_GROUP_SIZE = 10;

// Server location.
var SERVER = ""; //"http://usa.ucsd.edu:8080/cgi-bin/";

// if icons in navigation bar are shown
var SHOW_NAVIGATION_BAR_ICONS = true;

// define if the image cache is used
var USE_IMAGE_CACHE = true;

// data structure type used to implement the cache
var IMAGE_CACHE_BST = true;

// Project directory on server.
var PROJECT_DIR = ".";

// tables directory
var TABLES_DIR = "ReportData";

// Fasta filename in project directory subtree.
var GLOBAL_FASTA_FILENAME = "";

// Specs MS filename
var GLOBAL_SPECS_MS_FILENAME = "spectra/specs_ms.pklbin";

// Specifies if clusters layer is to be rendered
var GLOBAL_NO_CLUSTERS = 0;

// Status file filename
var STATUS_FILENAME = "status.txt";

// relauch script name
var RELAUNCH_SCRIPT = "relauncher.sh";

// status to keep pooling
var STATUS_RETRIEVE = "Running";

// status to allow navigation
var STATUS_OK = "Finished";

// status error
var STATUS_ERROR = "Error";

// cookie name prefix
var COOKIE_NEW_PREFIX = 'spsReport';

// tag delimiters
var TAG_OPEN  = '<';
var TAG_CLOSE = '>';

////////////////////////////////////////////////////////////////////////////////
// Report table column headers

var REPORT_HEADER_PROTEINS_0  = "Protein";
var REPORT_HEADER_PROTEINS_1  = "Description";
var REPORT_HEADER_PROTEINS_2  = "Contigs";
var REPORT_HEADER_PROTEINS_3  = "Spectra";
var REPORT_HEADER_PROTEINS_4  = "Amino acids";
var REPORT_HEADER_PROTEINS_5  = "Coverage (%)";

var REPORT_HEADER_CONTIGS_0   = "Index";
var REPORT_HEADER_CONTIGS_1   = "Spectra";
var REPORT_HEADER_CONTIGS_2   = "Tool";
var REPORT_HEADER_CONTIGS_3   = "Contig";
var REPORT_HEADER_CONTIGS_4   = "Contig sequence";
var REPORT_HEADER_CONTIGS_5   = "Protein";

var REPORT_HEADER_CLUSTERS_0  = "Index";
var REPORT_HEADER_CLUSTERS_1  = "Tool";
var REPORT_HEADER_CLUSTERS_2  = "Spectrum";
var REPORT_HEADER_CLUSTERS_3  = "Peptide";
var REPORT_HEADER_CLUSTERS_4  = "Mass (m)";
var REPORT_HEADER_CLUSTERS_5  = "Charge (z)";
var REPORT_HEADER_CLUSTERS_6  = "B (%)";
var REPORT_HEADER_CLUSTERS_7  = "Y (%)";
var REPORT_HEADER_CLUSTERS_8  = "BY Intensity (%)";
var REPORT_HEADER_CLUSTERS_9  = "Model";

var REPORT_HEADER_SPECTRA_0  = "Index";
var REPORT_HEADER_SPECTRA_1  = "Scan";
var REPORT_HEADER_SPECTRA_2  = "Tool";
var REPORT_HEADER_SPECTRA_3  = "Spectrum";
var REPORT_HEADER_SPECTRA_4  = "Sequences";
var REPORT_HEADER_SPECTRA_5  = "Protein";
var REPORT_HEADER_SPECTRA_6  = "Contig";
var REPORT_HEADER_SPECTRA_7  = "Mass (m)";
var REPORT_HEADER_SPECTRA_8  = "Charge (z)";
var REPORT_HEADER_SPECTRA_9  = "B (%)";
var REPORT_HEADER_SPECTRA_10  = "Y (%)";
var REPORT_HEADER_SPECTRA_11 = "BY Intensity (%)";
var REPORT_HEADER_SPECTRA_12 = "Model";

// Sequence names
var REPORT_SEQ_NAME_REFERENCE = "Reference";
var REPORT_SEQ_NAME_HOMOLOG   = "Homolog";
var REPORT_SEQ_NAME_DENOVO    = "de Novo";
var REPORT_SEQ_NAME_USER      = "User";

// buttons
var REPORT_BUTTON_UPDATE      = "Update";
var REPORT_BUTTON_ALIGN       = "Re-align";

////////////////////////////////////////////////////////////////////////////////
// Table fields' contents

// Proteins table
var TABLE_PROTEINS_FIELD_ID       = 0;
var TABLE_PROTEINS_FIELD_NAME     = 1;
var TABLE_PROTEINS_FIELD_DESC     = 2;
var TABLE_PROTEINS_FIELD_CONTIGS  = 3;
var TABLE_PROTEINS_FIELD_SPECTRA  = 4;
var TABLE_PROTEINS_FIELD_AAS      = 5;
var TABLE_PROTEINS_FIELD_COVERAGE = 6;
var TABLE_PROTEINS_FIELD_SEQUENCE = 7;

var TAG_TABLE_PROTEINS_FIELD_ID       = makeTag(TABLE_PROTEINS_FIELD_ID);
var TAG_TABLE_PROTEINS_FIELD_NAME     = makeTag(TABLE_PROTEINS_FIELD_NAME);
var TAG_TABLE_PROTEINS_FIELD_DESC     = makeTag(TABLE_PROTEINS_FIELD_DESC);
var TAG_TABLE_PROTEINS_FIELD_CONTIGS  = makeTag(TABLE_PROTEINS_FIELD_CONTIGS);
var TAG_TABLE_PROTEINS_FIELD_SPECTRA  = makeTag(TABLE_PROTEINS_FIELD_SPECTRA);
var TAG_TABLE_PROTEINS_FIELD_AAS      = makeTag(TABLE_PROTEINS_FIELD_AAS);
var TAG_TABLE_PROTEINS_FIELD_COVERAGE = makeTag(TABLE_PROTEINS_FIELD_COVERAGE);


// Contigs table
var TABLE_CONTIGS_FIELD_ID            = 0;
var TABLE_CONTIGS_FIELD_PROTEIN       = 1;
var TABLE_CONTIGS_FIELD_SPECTRA       = 2;
var TABLE_CONTIGS_FIELD_SEQ_REF       = 3;
var TABLE_CONTIGS_FIELD_SEQ_HOM       = 4;
var TABLE_CONTIGS_FIELD_SEQ_NOVO      = 5;
var TABLE_CONTIGS_FIELD_SEQ_USER      = 6;
var TABLE_CONTIGS_FIELD_PROTEIN_NAME  = 7;
var TABLE_CONTIGS_FIELD_PROTEIN_DESC  = 8;
var TABLE_CONTIGS_FIELD_MASS_REF      = 10;
var TABLE_CONTIGS_FIELD_MASS_HOM      = 11;
var TABLE_CONTIGS_FIELD_OFF_REF       = 12;
var TABLE_CONTIGS_FIELD_OFF_HOM       = 13;
var TABLE_CONTIGS_FIELD_REVERSE       = 14;
var TABLE_CONTIGS_FIELD_FILE_ABRUIJN  = 15;
var TABLE_CONTIGS_FIELD_FILE_STARS    = 16;
var TABLE_CONTIGS_FIELD_FILE_SEQS     = 17;
var TABLE_CONTIGS_FIELD_TOOL          = 18;

var TAG_TABLE_CONTIGS_FIELD_ID            = makeTag(TABLE_CONTIGS_FIELD_ID);
var TAG_TABLE_CONTIGS_FIELD_PROTEIN       = makeTag(TABLE_CONTIGS_FIELD_PROTEIN);
var TAG_TABLE_CONTIGS_FIELD_SPECTRA       = makeTag(TABLE_CONTIGS_FIELD_SPECTRA);
var TAG_TABLE_CONTIGS_FIELD_SEQ_REF       = makeTag(TABLE_CONTIGS_FIELD_SEQ_REF);
var TAG_TABLE_CONTIGS_FIELD_SEQ_HOM       = makeTag(TABLE_CONTIGS_FIELD_SEQ_HOM);
var TAG_TABLE_CONTIGS_FIELD_SEQ_NOVO      = makeTag(TABLE_CONTIGS_FIELD_SEQ_NOVO);
var TAG_TABLE_CONTIGS_FIELD_SEQ_USER      = makeTag(TABLE_CONTIGS_FIELD_SEQ_USER);
var TAG_TABLE_CONTIGS_FIELD_PROTEIN_NAME  = makeTag(TABLE_CONTIGS_FIELD_PROTEIN_NAME);
var TAG_TABLE_CONTIGS_FIELD_PROTEIN_DESC  = makeTag(TABLE_CONTIGS_FIELD_PROTEIN_DESC);
var TAG_TABLE_CONTIGS_FIELD_MASS_REF      = makeTag(TABLE_CONTIGS_FIELD_MASS_REF);
var TAG_TABLE_CONTIGS_FIELD_MASS_HOM      = makeTag(TABLE_CONTIGS_FIELD_MASS_HOM);
var TAG_TABLE_CONTIGS_FIELD_OFF_REF       = makeTag(TABLE_CONTIGS_FIELD_OFF_REF);
var TAG_TABLE_CONTIGS_FIELD_OFF_HOM       = makeTag(TABLE_CONTIGS_FIELD_OFF_HOM);
var TAG_TABLE_CONTIGS_FIELD_REVERSE       = makeTag(TABLE_CONTIGS_FIELD_REVERSE);
var TAG_TABLE_CONTIGS_FIELD_FILE_ABRUIJN  = makeTag(TABLE_CONTIGS_FIELD_FILE_ABRUIJN);
var TAG_TABLE_CONTIGS_FIELD_FILE_STARS    = makeTag(TABLE_CONTIGS_FIELD_FILE_STARS);
var TAG_TABLE_CONTIGS_FIELD_FILE_SEQS     = makeTag(TABLE_CONTIGS_FIELD_FILE_SEQS);
var TAG_TABLE_CONTIGS_FIELD_TOOL          = makeTag(TABLE_CONTIGS_FIELD_TOOL);

// Cluster table
var TABLE_CLUSTER_FIELD_ID            = 0;
var TABLE_CLUSTER_FIELD_CONTIG        = 1;
var TABLE_CLUSTER_FIELD_PROTEIN       = 2;
var TABLE_CLUSTER_FIELD_REFERENCE     = 3;
var TABLE_CLUSTER_FIELD_HOMOLOG       = 4;
var TABLE_CLUSTER_FIELD_DENOVO        = 5;
var TABLE_CLUSTER_FIELD_USER          = 6;
var TABLE_CLUSTER_FIELD_MASS          = 7;
var TABLE_CLUSTER_FIELD_CHARGE        = 8;
var TABLE_CLUSTER_FIELD_B_PER         = 9;
var TABLE_CLUSTER_FIELD_Y_PER         = 10;
var TABLE_CLUSTER_FIELD_BY_INT        = 11;
var TABLE_CLUSTER_FIELD_PROTEIN_NAME  = 12;
var TABLE_CLUSTER_FIELD_TOOL          = 13;
var TABLE_CLUSTER_FIELD_MODEL_NAME    = 14;
var TABLE_CLUSTER_FIELD_MODEL         = 15;
var TABLE_CLUSTER_FIELD_MASS_SHIFT    = 16;


var TAG_TABLE_CLUSTER_FIELD_ID        = makeTag(TABLE_CLUSTER_FIELD_ID);
var TAG_TABLE_CLUSTER_FIELD_CONTIG    = makeTag(TABLE_CLUSTER_FIELD_CONTIG);
var TAG_TABLE_CLUSTER_FIELD_TOOL      = makeTag(TABLE_CLUSTER_FIELD_TOOL);
var TAG_TABLE_CLUSTER_FIELD_REFERENCE = makeTag(TABLE_CLUSTER_FIELD_REFERENCE);
var TAG_TABLE_CLUSTER_FIELD_HOMOLOG   = makeTag(TABLE_CLUSTER_FIELD_HOMOLOG);
var TAG_TABLE_CLUSTER_FIELD_DENOVO    = makeTag(TABLE_CLUSTER_FIELD_DENOVO);
var TAG_TABLE_CLUSTER_FIELD_USER      = makeTag(TABLE_CLUSTER_FIELD_USER);
var TAG_TABLE_CLUSTER_FIELD_MASS      = makeTag(TABLE_CLUSTER_FIELD_MASS);
var TAG_TABLE_CLUSTER_FIELD_CHARGE    = makeTag(TABLE_CLUSTER_FIELD_CHARGE);
var TAG_TABLE_CLUSTER_FIELD_B_PER     = makeTag(TABLE_CLUSTER_FIELD_B_PER);
var TAG_TABLE_CLUSTER_FIELD_Y_PER     = makeTag(TABLE_CLUSTER_FIELD_Y_PER);
var TAG_TABLE_CLUSTER_FIELD_BY_INT    = makeTag(TABLE_CLUSTER_FIELD_BY_INT);
var TAG_TABLE_CLUSTER_FIELD_MODEL     = makeTag(TABLE_CLUSTER_FIELD_MODEL);
var TAG_TABLE_CLUSTER_FIELD_MASS_SHIFT= makeTag(TABLE_CLUSTER_FIELD_MASS_SHIFT);
var TAG_TABLE_CLUSTER_FIELD_MODEL_NAME= makeTag(TABLE_CLUSTER_FIELD_MODEL_NAME);

var TAG_CLUSTER_PEPTIDE_ALL  = makeTag(TABLE_CLUSTER_FIELD_REFERENCE + '|' + TABLE_CLUSTER_FIELD_HOMOLOG + '|' + TABLE_CLUSTER_FIELD_DENOVO);

// Spectra table
var TABLE_SPECTRA_FIELD_ID              = 0;
var TABLE_SPECTRA_FIELD_IDX             = 1;
var TABLE_SPECTRA_FIELD_SCAN            = 2;
var TABLE_SPECTRA_FIELD_CLUSTER         = 3;
var TABLE_SPECTRA_FIELD_PROTEIN_NAME    = 4;
var TABLE_SPECTRA_FIELD_PKLBIN_IDX      = 5;
var TABLE_SPECTRA_FIELD_PKLBIN_FILENAME = 6;
var TABLE_SPECTRA_FIELD_SEQ_REFERENCE   = 7;
var TABLE_SPECTRA_FIELD_SEQ_HOMOLOG     = 8;
var TABLE_SPECTRA_FIELD_SEQ_DENOVO      = 9;
var TABLE_SPECTRA_FIELD_SEQ_USER        = 10;
var TABLE_SPECTRA_FIELD_MASS            = 11;
var TABLE_SPECTRA_FIELD_CHARGE          = 12;
var TABLE_SPECTRA_FIELD_B_PER           = 13;
var TABLE_SPECTRA_FIELD_Y_PER           = 14;
var TABLE_SPECTRA_FIELD_BY_INTENSITY    = 15;
var TABLE_SPECTRA_FIELD_INPUT_FILENAME  = 16;
var TABLE_SPECTRA_FIELD_CONTIG_INDEX    = 17;
var TABLE_SPECTRA_FIELD_PROTEIN_INDEX   = 18;
var TABLE_SPECTRA_FIELD_TOOL            = 19;
var TABLE_SPECTRA_FIELD_MODEL           = 20;



var TAG_TABLE_SPECTRA_FIELD_ID              = makeTag(TABLE_SPECTRA_FIELD_ID);
var TAG_TABLE_SPECTRA_FIELD_IDX             = makeTag(TABLE_SPECTRA_FIELD_IDX);
var TAG_TABLE_SPECTRA_FIELD_SCAN            = makeTag(TABLE_SPECTRA_FIELD_SCAN);
var TAG_TABLE_SPECTRA_FIELD_CLUSTER         = makeTag(TABLE_SPECTRA_FIELD_CLUSTER);
var TAG_TABLE_SPECTRA_FIELD_PROTEIN_NAME    = makeTag(TABLE_SPECTRA_FIELD_PROTEIN_NAME);
var TAG_TABLE_SPECTRA_FIELD_PKLBIN_IDX      = makeTag(TABLE_SPECTRA_FIELD_PKLBIN_IDX);
var TAG_TABLE_SPECTRA_FIELD_PKLBIN_FILENAME = makeTag(TABLE_SPECTRA_FIELD_PKLBIN_FILENAME);
var TAG_TABLE_SPECTRA_FIELD_SEQ_REFERENCE   = makeTag(TABLE_SPECTRA_FIELD_SEQ_REFERENCE);
var TAG_TABLE_SPECTRA_FIELD_SEQ_HOMOLOG     = makeTag(TABLE_SPECTRA_FIELD_SEQ_HOMOLOG);
var TAG_TABLE_SPECTRA_FIELD_SEQ_DENOVO      = makeTag(TABLE_SPECTRA_FIELD_SEQ_DENOVO);
var TAG_TABLE_SPECTRA_FIELD_SEQ_USER        = makeTag(TABLE_SPECTRA_FIELD_SEQ_USER);
var TAG_TABLE_SPECTRA_FIELD_MASS            = makeTag(TABLE_SPECTRA_FIELD_MASS);
var TAG_TABLE_SPECTRA_FIELD_CHARGE          = makeTag(TABLE_SPECTRA_FIELD_CHARGE);
var TAG_TABLE_SPECTRA_FIELD_B_PER           = makeTag(TABLE_SPECTRA_FIELD_B_PER);
var TAG_TABLE_SPECTRA_FIELD_Y_PER           = makeTag(TABLE_SPECTRA_FIELD_Y_PER);
var TAG_TABLE_SPECTRA_FIELD_BY_INTENSITY    = makeTag(TABLE_SPECTRA_FIELD_BY_INTENSITY);
var TAG_TABLE_SPECTRA_FIELD_INPUT_FILENAME  = makeTag(TABLE_SPECTRA_FIELD_INPUT_FILENAME);
var TAG_TABLE_SPECTRA_FIELD_CONTIG_INDEX    = makeTag(TABLE_SPECTRA_FIELD_CONTIG_INDEX);
var TAG_TABLE_SPECTRA_FIELD_PROTEIN_INDEX   = makeTag(TABLE_SPECTRA_FIELD_PROTEIN_INDEX);
var TAG_TABLE_SPECTRA_FIELD_TOOL            = makeTag(TABLE_SPECTRA_FIELD_TOOL);
var TAG_TABLE_SPECTRA_FIELD_MODEL           = makeTag(TABLE_SPECTRA_FIELD_MODEL);

var TAG_SPECTRA_PEPTIDE_ALL  = makeTag(TABLE_SPECTRA_FIELD_SEQ_REFERENCE + '|' + TABLE_SPECTRA_FIELD_SEQ_HOMOLOG + '|' + TABLE_SPECTRA_FIELD_SEQ_DENOVO);

// Proteins coverage table
var TABLE_COVERAGE_FIELD_ID              = 0;
var TABLE_COVERAGE_FIELD_NAME            = 1;
var TABLE_COVERAGE_FIELD_SEQ_REFERENCE   = 2;
var TABLE_COVERAGE_FIELD_PROT_SEQUENCE   = 3;
var TABLE_COVERAGE_CSPS_DATA             = 4;
var TABLE_COVERAGE_SPS_DATA              = 5;

////////////////////////////////////////////////////////////////////////////////
// Object types in report elements
var REPORT_CELL_TYPE_IOD              = "iod";
var REPORT_CELL_TYPE_STRING           = "str";
var REPORT_CELL_TYPE_STRING_MULTIPLE  = "strM";
var REPORT_CELL_TYPE_BOX              = "box";

////////////////////////////////////////////////////////////////////////////////
// Image id tags prefixes:
//
// image shown (src)       ->  im_ , imc_
// image on demand (href)  ->  io_ , ioc_
//
var IMAGE_ICON_ID_PREFIX        = "im_";
var IMAGE_ICON_CTRL_ID_PREFIX   = "imc_";
var IMAGE_LARGE_ID_PREFIX       = "io_";
var IMAGE_LARGE_CTRL_ID_PREFIX  = "ioc_";

////////////////////////////////////////////////////////////////////////////////
// System internal tags

var INTERNAL_ROW      = "row";
var INTERNAL_COL      = "col";
var INTERNAL_PROJDIR  = "projectdir";
var INTERNAL_MS_FNAME = "msFilename";

var TAG_INTERNAL_ROW      = makeTag(INTERNAL_ROW);
var TAG_INTERNAL_COL      = makeTag(INTERNAL_COL);
var TAG_INTERNAL_PROJDIR  = makeTag(INTERNAL_PROJDIR);
var TAG_INTERNAL_MS_FNAME = makeTag(INTERNAL_MS_FNAME);

// Helpers

var ASPAS = "\"";

var stIsIE = /*@cc_on!@*/false;


////////////////////////////////////////////////////////////////////////////////
// renderers & server objects
var SPS_REPORTS       = "spsReports.cgi";
var CONTIG_RENDERER   = "contplot.cgi";
var SPECTRUM_RENDERER = "specplot.cgi";

// spsReports parameters names
var REPORT_SERVER_PAR_GET     = "--get";
var REPORT_SERVER_PAR_UPDATE  = "--update";
var REPORT_SERVER_PAR_LAUNCH  = "--launch";
var REPORT_SERVER_PAR_STATUS  = "--status";

var REPORT_SERVER_PAR_REQUEST_ID    = "--request-id";
var REPORT_SERVER_PAR_TABLE         = "--table";
var REPORT_SERVER_PAR_FILTER_FIELD  = "--filter-field";
var REPORT_SERVER_PAR_FILTER_DATA   = "--filter-data";
var REPORT_SERVER_PAR_SORT_FIELD    = "--sort-column";
var REPORT_SERVER_PAR_SORT_REVERSE  = "--sort-reverse";
var REPORT_SERVER_PAR_UPDATE_FIELD  = "--update-field";
var REPORT_SERVER_PAR_UPDATE_DATA   = "--update-data";
var REPORT_SERVER_PAR_CLEAR_DATA    = "--clear-data";

var REPORT_SERVER_PAR_PROJECT_DIR   = "--project-dir";
var REPORT_SERVER_PAR_TABLES_DIR    = "--tables-dir";
var REPORT_SERVER_PAR_FILENAME      = "--filename";
var REPORT_SERVER_PAR_DESCRIPTION   = "--description";
var REPORT_SERVER_PAR_SEQUENCE      = "--sequence";
var REPORT_SERVER_PAR_ID            = "--ID";

// Renderers' parameters names (contplot)
var CONTPLOT_PAR_STAR           = "--star";
var CONTPLOT_PAR_ABRUIJN        = "--abruijn";
var CONTPLOT_PAR_SEQS           = "--seqs";
var CONTPLOT_PAR_TITLE          = "--title";
var CONTPLOT_PAR_NO_TITLE       = "--notitle";
var CONTPLOT_PAR_ZOOM           = "--zoom";
var CONTPLOT_PAR_CONTIG         = "--contig";
var CONTPLOT_PAR_MASS_REF       = "--mass-reference";
var CONTPLOT_PAR_MASS_HOM       = "--mass-homolog";
var CONTPLOT_PAR_OFF_REF        = "--offset-reference";
var CONTPLOT_PAR_OFF_HOM        = "--offset-homolog";
var CONTPLOT_PAR_REVERSE        = "--reverse";
var CONTPLOT_PAR_TARGET         = "--target";
var CONTPLOT_PAR_ENCODING       = "--encoding";
var CONTPLOT_PAR_SEQ_REFERENCE  = "--reference";
var CONTPLOT_PAR_SEQ_HOMOLOG    = "--homolog";
var CONTPLOT_PAR_SEQ_DENOVO     = "--denovo";
var CONTPLOT_PAR_SEQ_USER       = "--user";
var CONTPLOT_PAR_IMAGE_LIMIT_X  = "--image-stretch-width";
var CONTPLOT_PAR_IMAGE_LIMIT_Y  = "--image-stretch-height";


// Renderers' parameters names (specplot)
var SPECPLOT_PAR_PKLBIN         = "--pklbin";
var SPECPLOT_PAR_SPECTURM       = "--spectrum";
var SPECPLOT_PAR_PEPTIDE        = "--peptide";
var SPECPLOT_PAR_TARGET         = "--target";
var SPECPLOT_PAR_ENCODING       = "--encoding";
var SPECPLOT_PAR_ZOOM           = "--zoom";
var SPECPLOT_PAR_TITLE          = "--title";
var SPECPLOT_PAR_NOTITLE        = "--notitle";
var SPECPLOT_PAR_MODEL          = "--annotation-model";
var SPECPLOT_PAR_MASS_SHIFT     = "--shift-value";



// renderers' parameters values (contplot) " +  + "
var CONTPLOT_VAL_STAR           = TAG_TABLE_CONTIGS_FIELD_FILE_STARS;
var CONTPLOT_VAL_ABRUIJN        = TAG_TABLE_CONTIGS_FIELD_FILE_ABRUIJN;
var CONTPLOT_VAL_SEQS           = TAG_TABLE_CONTIGS_FIELD_FILE_SEQS;
var CONTPLOT_VAL_TITLE          = "\"Contig " + TAG_TABLE_CONTIGS_FIELD_ID + ASPAS;
var CONTPLOT_VAL_CONTIG         = TAG_TABLE_CONTIGS_FIELD_ID;
var CONTPLOT_VAL_MASS_REF       = ASPAS + TAG_TABLE_CONTIGS_FIELD_MASS_REF + ASPAS;
var CONTPLOT_VAL_MASS_HOM       = ASPAS + TAG_TABLE_CONTIGS_FIELD_MASS_HOM + ASPAS;
var CONTPLOT_VAL_OFF_REF        = TAG_TABLE_CONTIGS_FIELD_OFF_REF;
var CONTPLOT_VAL_OFF_HOM        = TAG_TABLE_CONTIGS_FIELD_OFF_HOM;
var CONTPLOT_VAL_REVERSE        = "";
var CONTPLOT_VAL_TARGET         = "cout";
var CONTPLOT_VAL_ENCODING       = "uu64";
var CONTPLOT_VAL_SEQ_REFERENCE  = ASPAS + TAG_TABLE_CONTIGS_FIELD_SEQ_REF + ASPAS;
var CONTPLOT_VAL_SEQ_HOMOLOG    = ASPAS + TAG_TABLE_CONTIGS_FIELD_SEQ_HOM + ASPAS;
var CONTPLOT_VAL_SEQ_DENOVO     = ASPAS + TAG_TABLE_CONTIGS_FIELD_SEQ_NOVO + ASPAS;
var CONTPLOT_VAL_SEQ_USER       = ASPAS + TAG_TABLE_CONTIGS_FIELD_SEQ_USER + ASPAS;
var CONTPLOT_VAL_NO_TITLE       = "";
var CONTPLOT_VAL_ZOOM           = "0.4";
var CONTPLOT_VAL_IMAGE_LIMIT_Y  = "-1";
var CONTPLOT_VAL_IMAGE_LIMIT_X  = "-1"
var CONTPLOT_VAL_IMAGE_LIMIT_X_SMALL  = "300"


// renderers' parameters values (specplot)
var SPECPLOT_VAL_TARGET         = "cout";
var SPECPLOT_VAL_ENCODING       = "uu64";

// renderers' parameters values (specplot for cluster)
var SPECPLOT_VAL_CLUSTER_NOTITLE        = "";
var SPECPLOT_VAL_CLUSTER_TITLE          = "\"Consensus Spectrum " + TAG_TABLE_CLUSTER_FIELD_ID + " (contig " + TAG_TABLE_CLUSTER_FIELD_CONTIG + ")\"";
var SPECPLOT_VAL_CLUSTER_PKLBIN         = TAG_INTERNAL_PROJDIR + "/" + TAG_INTERNAL_MS_FNAME;
var SPECPLOT_VAL_CLUSTER_SPECTURM       = TAG_TABLE_CLUSTER_FIELD_ID;
var SPECPLOT_VAL_CLUSTER_ZOOM           = "0.35";
var SPECPLOT_VAL_CLUSTER_PEPTIDE_ALL    = ASPAS + TAG_CLUSTER_PEPTIDE_ALL + ASPAS;  // <3|4|5>
var SPECPLOT_VAL_CLUSTER_PEPTIDE_REF    = ASPAS + TAG_TABLE_CLUSTER_FIELD_REFERENCE + ASPAS;
var SPECPLOT_VAL_CLUSTER_PEPTIDE_HOM    = ASPAS + TAG_TABLE_CLUSTER_FIELD_HOMOLOG + ASPAS;
var SPECPLOT_VAL_CLUSTER_PEPTIDE_NOVO   = ASPAS + TAG_TABLE_CLUSTER_FIELD_DENOVO + ASPAS;
var SPECPLOT_VAL_CLUSTER_PEPTIDE_USER   = ASPAS + TAG_TABLE_CLUSTER_FIELD_USER + ASPAS;
var SPECPLOT_VAR_CLUSTER_MODEL          = ASPAS + TAG_TABLE_CLUSTER_FIELD_MODEL + ASPAS;
var SPECPLOT_VAR_CLUSTER_MASS_SHIFT     = ASPAS + TAG_TABLE_CLUSTER_FIELD_MASS_SHIFT + ASPAS;

// renderers' parameters values (specplot for input spectra)
var SPECPLOT_VAL_SPECTRA_NOTITLE        = "";
var SPECPLOT_VAL_SPECTRA_TITLE          = "\"Spectrum Scan " + TAG_TABLE_SPECTRA_FIELD_SCAN + ASPAS;
//var SPECPLOT_VAL_SPECTRA_PKLBIN         = TAG_INTERNAL_PROJDIR + "/" + TAG_TABLE_SPECTRA_FIELD_PKLBIN_FILENAME;
var SPECPLOT_VAL_SPECTRA_PKLBIN         = TAG_TABLE_SPECTRA_FIELD_PKLBIN_FILENAME;
var SPECPLOT_VAL_SPECTRA_SPECTURM       = TAG_TABLE_SPECTRA_FIELD_IDX;
var SPECPLOT_VAL_SPECTRA_ZOOM           = "0.35";
var SPECPLOT_VAL_SPECTRA_PEPTIDE_ALL    = ASPAS + TAG_SPECTRA_PEPTIDE_ALL + ASPAS;
var SPECPLOT_VAL_SPECTRA_PEPTIDE_REF    = ASPAS + TAG_TABLE_SPECTRA_FIELD_SEQ_REFERENCE + ASPAS;
var SPECPLOT_VAL_SPECTRA_PEPTIDE_HOM    = ASPAS + TAG_TABLE_SPECTRA_FIELD_SEQ_HOMOLOG + ASPAS;
var SPECPLOT_VAL_SPECTRA_PEPTIDE_NOVO   = ASPAS + TAG_TABLE_SPECTRA_FIELD_SEQ_DENOVO + ASPAS;
var SPECPLOT_VAL_SPECTRA_PEPTIDE_USER   = ASPAS + TAG_TABLE_SPECTRA_FIELD_SEQ_USER + ASPAS;


// renderers' parameters conditions (contplot)
var CONTPLOT_COND_STAR           = "";
var CONTPLOT_COND_ABRUIJN        = "";
var CONTPLOT_COND_SEQS           = "";
var CONTPLOT_COND_TITLE          = "";
var CONTPLOT_COND_CONTIG         = TAG_TABLE_CONTIGS_FIELD_ID;
var CONTPLOT_COND_MASS_REF       = TAG_TABLE_CONTIGS_FIELD_MASS_REF;
var CONTPLOT_COND_MASS_HOM       = TAG_TABLE_CONTIGS_FIELD_MASS_HOM;
var CONTPLOT_COND_OFF_REF        = TAG_TABLE_CONTIGS_FIELD_OFF_REF;
var CONTPLOT_COND_OFF_HOM        = TAG_TABLE_CONTIGS_FIELD_OFF_HOM;
var CONTPLOT_COND_REVERSE        = TAG_TABLE_CONTIGS_FIELD_REVERSE;
var CONTPLOT_COND_TARGET         = "";
var CONTPLOT_COND_ENCODING       = "";
var CONTPLOT_COND_SEQ_REFERENCE  = TAG_TABLE_CONTIGS_FIELD_SEQ_REF;
var CONTPLOT_COND_SEQ_HOMOLOG    = TAG_TABLE_CONTIGS_FIELD_SEQ_HOM;
var CONTPLOT_COND_SEQ_DENOVO     = TAG_TABLE_CONTIGS_FIELD_SEQ_NOVO;
var CONTPLOT_COND_SEQ_USER       = TAG_TABLE_CONTIGS_FIELD_SEQ_USER;
var CONTPLOT_COND_NO_TITLE       = "";
var CONTPLOT_COND_ZOOM           = "";
var CONTPLOT_COND_IMAGE_LIMIT_X  = "";
var CONTPLOT_COND_IMAGE_LIMIT_Y  = "";


// renderers' parameters conditions (specplot)
var SPECPLOT_COND_TARGET         = "";
var SPECPLOT_COND_ENCODING       = "";

// renderers' parameters condition (specplot for cluster)
var SPECPLOT_COND_CLUSTER_NOTITLE        = "";
var SPECPLOT_COND_CLUSTER_TITLE          = "";
var SPECPLOT_COND_CLUSTER_PKLBIN         = "";
var SPECPLOT_COND_CLUSTER_SPECTURM       = "";
var SPECPLOT_COND_CLUSTER_ZOOM           = "";
var SPECPLOT_COND_CLUSTER_PEPTIDE_ALL    = "";
var SPECPLOT_COND_CLUSTER_PEPTIDE_REF    = "";
var SPECPLOT_COND_CLUSTER_PEPTIDE_HOM    = "";
var SPECPLOT_COND_CLUSTER_PEPTIDE_NOVO   = "";
var SPECPLOT_COND_CLUSTER_PEPTIDE_USER   = "";
var SPECPLOT_COND_CLUSTER_PEPTIDE_USER   = "";
var SPECPLOT_COND_CLUSTER_PEPTIDE_USER   = "";
var SPECPLOT_COND_CLUSTER_MODEL          = TAG_TABLE_CLUSTER_FIELD_MODEL;
var SPECPLOT_COND_CLUSTER_MASS_SHIFT     = TAG_TABLE_CLUSTER_FIELD_MASS_SHIFT;

// renderers' parameters condition (specplot for input spectra)
var SPECPLOT_COND_SPECTRA_NOTITLE        = "";
var SPECPLOT_COND_SPECTRA_TITLE          = "";
var SPECPLOT_COND_SPECTRA_PKLBIN         = "";
var SPECPLOT_COND_SPECTRA_SPECTURM       = "";
var SPECPLOT_COND_SPECTRA_ZOOM           = "";
var SPECPLOT_COND_SPECTRA_PEPTIDE_ALL    = "";
var SPECPLOT_COND_SPECTRA_PEPTIDE_REF    = "";
var SPECPLOT_COND_SPECTRA_PEPTIDE_HOM    = "";
var SPECPLOT_COND_SPECTRA_PEPTIDE_NOVO   = "";
var SPECPLOT_COND_SPECTRA_PEPTIDE_USER   = "";


////////////////////////////////////////////////////////////////////////////////
// page elements
var DIV_PAGE_MAIN  = "mainDiv2";
var DIV_PAGE_DATA  = "mainDiv";

// page type IDs
var PAGE_INITIAL              = 10;
var PAGE_PROTEINS             = 20;
var PAGE_PROTEIN              = 30;
var PAGE_PROTEIN_COVERAGE     = 40;
var PAGE_CONTIGS              = 50;
var PAGE_CONTIG               = 60;
var PAGE_CLUSTER              = 70;
var PAGE_SPECTRA              = 80;
var PAGE_PROTEIN_COVERAGE_CSV = 90;


////////////////////////////////////////////////////////////////////////////////
// Message to be displayed on connection error.
var CONN_ERR = "XMLHTTP not available. Could not connect to server.";

////////////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////////////


// Global image ID. Used to generate unique IDs for images for image placement upon arrival from server
var globalImage = 0;

// Current protein coverage. Used to gather sequence in protein coverage pages to send to server for reprocessing.
var globalProteinLength = -1;

// status variables
var globalStatus      = "";
var globalStatusPrev  = "";

// Global request ID, used to fool "smart" browsers that cache AJAX requests
var requestID = 0;

// the tables
var TablesAll;

////////////////////////////////////////////////////////////////////////////////
// Images
////////////////////////////////////////////////////////////////////////////////

var iconHome = "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";

var iconProteinList = "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";

var iconProtein = "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";

var iconProteinCoverage = "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";

var iconContig = "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";

var iconContigList = "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";

var loadingImage = "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";

var loadingImage2 = "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";

var workingImage = "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";

var imageNa = "R0lGODlh3ADdAHAAACwAAAAA3ADdAIcAAAAAADMAAGYAAJkAAMwAAP8AKwAAKzMAK2YAK5kAK8wAK/8AVQAAVTMAVWYAVZkAVcwAVf8AgAAAgDMAgGYAgJkAgMwAgP8AqgAAqjMAqmYAqpkAqswAqv8A1QAA1TMA1WYA1ZkA1cwA1f8A/wAA/zMA/2YA/5kA/8wA//8zAAAzADMzAGYzAJkzAMwzAP8zKwAzKzMzK2YzK5kzK8wzK/8zVQAzVTMzVWYzVZkzVcwzVf8zgAAzgDMzgGYzgJkzgMwzgP8zqgAzqjMzqmYzqpkzqswzqv8z1QAz1TMz1WYz1Zkz1cwz1f8z/wAz/zMz/2Yz/5kz/8wz//9mAABmADNmAGZmAJlmAMxmAP9mKwBmKzNmK2ZmK5lmK8xmK/9mVQBmVTNmVWZmVZlmVcxmVf9mgABmgDNmgGZmgJlmgMxmgP9mqgBmqjNmqmZmqplmqsxmqv9m1QBm1TNm1WZm1Zlm1cxm1f9m/wBm/zNm/2Zm/5lm/8xm//+ZAACZADOZAGaZAJmZAMyZAP+ZKwCZKzOZK2aZK5mZK8yZK/+ZVQCZVTOZVWaZVZmZVcyZVf+ZgACZgDOZgGaZgJmZgMyZgP+ZqgCZqjOZqmaZqpmZqsyZqv+Z1QCZ1TOZ1WaZ1ZmZ1cyZ1f+Z/wCZ/zOZ/2aZ/5mZ/8yZ///MAADMADPMAGbMAJnMAMzMAP/MKwDMKzPMK2bMK5nMK8zMK//MVQDMVTPMVWbMVZnMVczMVf/MgADMgDPMgGbMgJnMgMzMgP/MqgDMqjPMqmbMqpnMqszMqv/M1QDM1TPM1WbM1ZnM1czM1f/M/wDM/zPM/2bM/5nM/8zM////AAD/ADP/AGb/AJn/AMz/AP//KwD/KzP/K2b/K5n/K8z/K///VQD/VTP/VWb/VZn/Vcz/Vf//gAD/gDP/gGb/gJn/gMz/gP//qgD/qjP/qmb/qpn/qsz/qv//1QD/1TP/1Wb/1Zn/1cz/1f///wD//zP//2b//5n//8z///8AAAAAAAAAAAAAAAAI/wD3CRxIsKDBgwgTKlzIsKHDhxAjSpxIsaLFixgzatzIsaPHjyBDihxJsqTJkyhTqlzJsqXLlzBjypxJs6bNmwuVEdQ5kKdAn/uACt1JtGfRn0eDJh1qtClSp0qhMn1KNWrVqVazYt26NGlOZcSUgR0rNmzYsmjPjlV71qzYtW/bkoWLlq5duWzn4o2rNy3fvHf7Bgbs1m/dwoEH87XrUO3bx5AjS55MubLly5gza97MubNnzGEbPjZYj/TB0gVRpzbNmqBq161hr44t8PVA2/tw56Zdm/fu2cBvn/b9VjRQnMiTa6wntiFzZbqVS5/uUGx0gtBCU9/O/evxhM27i/8f3zO8wufXyau3+by6Mmjr40u3zrC4/Ps4w8KvDx2/f5r0LdTefwS+ZN9C0ARY4IIqHZjQgAxGeJJ2/H0n4YUeKQieeRh22BGEORHj4YgdOYgQiCSmSFF2Fh6koYowQvSiixzGaCNDz+0Xoo439rhherXV6OOQBFGoUIL9EalkeS26JuSSPZoInohQLjmjQVJWeaORCmWpJYxeOtnklySiOCWZQ15ZUJhoesgijz+2eaOaYsppo5kHJUgMnHaOyGaQY/YpIZdxCpoinUwaeuiTLlKpqJ+M1vnoiIQi9Oek/iH6U6SY/pejaI52KqGmuXEq6n0sNoQkkKfGdymereINByuWe8bKIKmX2jpeqv/GsaqreK+a+qt4s65Z67CZJtmlsMhyp1+vzeJHarHRbperntXeF2yg2U5XKY3cdpscrsyKixO1PYVqbnfbcheurrzy56tM6OpK7rsxKZNJJvXw2eyn9R07HxqTZPJbt9OWGxMxYoghcLffFrQqdcqggQa/67ZLsRiTHGsdWplYpycxIdf4HDEkmwXNa2WR/BZza5aVyVnz2pRrUOqOazHGOIuVySRocFwyMUAHPbPEJFtssRgzv9dTJkET3PTR6RYtxsX42qzshlm/RAwajXzyEzFuFLwv0EInPQnQBfPEnNpsE1xwkD8TLHfZIdPN9tpmK0xTxDF33VLFFw9Ud8f/0OkbtX76Xq3dvkzv2a/aOukLdGjKoE31PlA3jSTbgucrbL0yEe1wbVAz7VMmDW/+dcGlZbdvqI2jUVrmbRtutIiyc+wTWEFvPR3pYFlr8eNr5y0Qybn/lDxPKwtFsu+cXxwq82jwRPS+OsVONNahu3SvtY4LlB3WBP0csmqW81xqXMR8MsnVOrGu/E/qi6j47PqGVffm1HkTtKZDuFrVI38++drMdLS9+1nuamZjne04pzrsEG0SOoFG3ApmNrYtkF3CO43fvDY/Kp3vfpxTH/vKZkDFQXBfP+MYfObnPpyVrXJrk9rZYHiW7tRLT/66SQH3g8CBbE9gRHMD5pLn/5gD0o+CKORcwfSHQOhED2bj0Zi3gleaAzZPIOpzH+4MFpSr1VBxGISisrDXvZ+lcU0Hc9a7SCWTIYJxigm0HgP5FxSj8ch0aRwj9L5GMO1Z7I3Oy174xBdCLI3QJV87XVDU55PsmE018kNDrTJnvX4dkHU3mKDlNLmy6RXSfBLEXO1yNp9yFW9jFawe4nSnyd9JrY059GDBGuaow13sbo5qn9349iwQcot0+ZqEElHHvSJxb48zQw3woqbDU+IsdXJzo1BiGLV9qQdwO3nk4ELFHCyWxzYiC6dbotecyJwFhmTsDWPIMz40pWybXywQwELUJrWFhTlQw2DNstjI1P+Ik0SjNNvXGhFPBsXrSHScE8lmxkOnjWp0B02RnmYGTlm58mFoWlmCIMWqm62rJg9d1kBPWkeMLpKlLCEeSGUVq3oWaGLgeimGivmVlVJne0962wifo1MCFlRSBWId9bBESYgkaHYXutYrkyqGG8RyJ7ccKPOK2spjZlQ5oIwcnNqXNbD8jJUE6uimuGoTpbJNXe2jHVjuCRTshSyI0jpqohaky6sG5Xnpwqb1ntYwgqmVPDJlkP0UV8unNXMfshvm8ypXt8ixFSdaJBANzZq8niTvdq/Lm88it7yARpFAKS0UgRY7WuWR9a9+daNoZYshm/5HgxU8oGFxmTdCwjUHoLxL2mXPJf8WvO5kpvdh3Rsbt0zFqeWJBYlkG89aW70CikGgM+JmM8c9sCy1PMGD7BF3Gi6crvaq59Mk89pise98T0T1INskxBZVly7IiYicZMF0CB2oNeI4YnkiNLRZ3zkiVz7KBTA2c0e4hupXk+KdYnVL+lXk4DaK8Q2a0HBIWtQBDWPAyy+DDhvR7khQeLo1o/YU+h7muZaTBhuu1rwq45lM4gYihmzmWscTseTSbgCsWMNy7J/ELqipB3lvJZM25A+mz4MXpXCNW9ok8zJJSv0ai3HjI8AKwdRd1n3fl7dj5DEblVsmNbPX5hhmNcPEtm4W4ke3HGcD2bfOyCFxm/G8Ejj/Gwglx+nXRMI15ZHss0toXUn0sgISCFmZIeyUV6FBkrBJS2Sipy0RHwF64BNBFdGZtrBakWRpiCgVwiFZmXLNxzAxlNV+OTHankVHY9HFkGk+hQhAyejECTqEOTeeRE4aUTgyfzQm2Uka+E6S3rLSMNa4pvNM/LySibr4YaMJ3O9Sxj+grIywiHwORZv2u8Vam0M7xja3mzaT1Fpq1iGhpFk3p5N7GgtlY4Oaho/X44mihmHZC+zVBs7uSTpOgpa9zc5UA9B9F5zWOKpwRhpHxvYd15pjcwO55cvBw1GJ4vizJhrVl8sez+9ibrSbx4LmMct1XGqMXolMpR0SYKMa/79Cga7hVOdj1XlvsbkJqPaop9vcTQ7oLvwgJ5f74X8/z5NFfHOY0/yRuBoRfT2RGvtYjqRP4++JjRP2JC3mvXwKeX2rJCyqd1xx0+4kuzDhqUohOUUdWY5CcYWPJVEdFJ88h4aSU+5+GIZI87xlfoFM8E6aWg9+G7xklXugg1lSaZcMeGdq+Z+j4qu+kIf7LTP7RCTRbr/Y6dvvIGMy2p/99txBg9gV351ZUabvyTdozi5RasMKu/ti6zigpf0ik6vpu/rJcHlL9XHUzCZrg4v9ac0z2t9bx0G8XQ7i3mmJzZk2zF/iWu31k3Dwszmz7FL8dorfh9qkhrLNApRpa/9qKicld3Z4wvOwI9FzrjMyYDx6MkEHRGzKogzEFhYf1mMINFJQFHjHp34EAx/XJlJjl3gcE3+5xXKVYzS5sTJdFHOUF2bI9CEuZiEV80UNplw88z8sc2KPh35XUxpu93Y+x0kBd3WzBGOlwnpEUWq/xizYwhKss0wuwkO34UYnl0cFoyOW5Duq1oCEB4Ewly6y9lSO4zapNBAYCEaOhz/iZ2e11melF0TfE09mtXzQ43JskTpHQ3EZJEHoh0cyw2PvZ1n6gmRnp11wWIYAxBLuBi4pMTkaCB4s+HU8dhvKtjfY9E5XgzpP9EkQRHyI0zhM40v01nwhd0iHJHeDM3WQEjdoW7UQCrRtt4Q0aMN+8uZFKdg8YFGKUyR/YeRWKFQPa/Nb8/NCPNiDFsVPH1hSOfMyOVUcCoJu3rYYfRcV7UFU31FckCUm2dZSrBKCfMZso1Zi0XgSmVWNMTFz2AggnHiL2/gQ+veNVBZx3iiO2Qcq5ig6UpaOccdm5ciOfiggnQiPFCFViUaPJFF5+Fht/+64j7eHZvPojw9RZgJpEtdYkCLRh460fwgpEdTWkB6hjRA5Egc5kR4RjhYZEg+ZkROnjAFDcxzpkCAYkCEZXWzGkCXJNV6WkhxBkCzZkev4khqhkIEjkxpRkTYpES6Zk/XYjTx5ETQZTij5kzj5k7ioKmABkka5kOS4lBWhie82lDy5kU65LAZWlYN2Z1gJEXr2jgJJlVvpSFcZlg9RlGRpEF15lgNklWpJjtI2VW2pWg9CkiwZlOZDjVtplnEpkXEZlSvZlwiBkYAplk05mIQJKkqZl8JCdVspmIZ5ToX5mLfhg3ApmX33hZYpXmyWmZD5FZIjUv8XmqA5mqJZmn+keZqmmZqouZqq2Zqs+ZquGZuwOZuy2ZqXWR2O8Rm6uZu82Zu++ZvAWRk9VCFyQRbFeZyHkZzGqZzIuZzO2ZzQyZzS+ZzTGZ3UeZ3WmZ3VWReQMZC98Z2oEZ7gOZ6/IZ7lSZ7mmZ7ouZ7n2Z7q6Z7s+Z7yGZ/0CZ/2OZ+70YGcC7mf/Nmf/vmfhhIQADs=";

var iconArrowLeft1 = "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";

var iconArrowLeft2 = "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";

var iconArrowRight1 = "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";

var iconArrowRight2 = "iVBORw0KGgoAAAANSUhEUgAAAFQAAABcCAIAAAB/WgX7AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAACu0SURBVHhe5XwJtBxVtXbNXT1Pd56T3ExkIGSGRCAgyCAyyaAGlElQFJbCA/T9vud7ooA+8UdRFBT4ffrQB4IoMgeEQMg83eTmJrnzPHX37am6umt6X/UOZecmN4kIa/1rvVpZnequU6fO3vvb395nn1OXnZiY8Pl8PM8z//sO1jAMjuP+9wluS8xalnUMyXGVZdmpGuCqaZp/F2ryBR294RaeZ037blPgBaf/KZ/00RjnOMJ/KA81LSaXU4EvURQhM2m7v39AlmWPxyNJEvSLq4Q/wzSgEV3X0Rh6yak5YNPn9X0Uevlohc/n8wfbO4eHhwcHB9PpNMTAAdmKkGEgLs4LhQJEFQQB1ANd1NVXLV++PBqJOnrXDd1GR1FnaIx7obUPxSonJDyGeAxeOPKqoig7duxob2/Hicfrx1FdXV1TUxMIBNAPEA9r53J5G/RFRUBHiUQCOorH4319PdAFvkYikTVr1pxyyimHwGLZLR0XO/aQTlA1JyT8MXx+EiOkUul1697o7e11uVyNjY11dXWRaBQC4ytsm81mSUJICyPjU1VV9ACbh8NhqAYmBdpTqdTQ0FBfX19HR8f4+Pi8efPOO++8hvpacoeig3BERv8gVX9A4SlGlEqeyWT+9KcXDh48WFFRgeHCzrASUNo/MAAxOjs7Ic/o6OjY2BhUYNtQsL2YKBNdQX6YGvLPmX0StNbc3FxeXo7+oaw9e/ag21DQf+6558IjcBdUBlXiOEELT9XsRIV3VE4jnmTwAwcOPPXU7zHcOXPmQHiIByeH3YD8iWTSpnRBgFVxAkfAJ8ybU9M0JugROsrlcrhknygGtAZFzJ49G6IC9tBLMpncvWvbwMBAKBQ655xzTj75ZNyIW9DnMYLRcVVzosJTRDzySd3dPU88+f+8Xu+smTPh2xCsq6tr3759gCsEBrZl2SZzx8iapgEj0A5+RJ+kR9yF36EFNBM4EXkX2sApIB7c4eyzzwbsK2tqgSBoEyCCij/72c8iUGSzea/HVRzYcSU9SoMTFf7IW9V8/peP/aq7pwdDgc2BB4I3PBYyA8BkHMhIkpP6ICEZmX6BzETg5L24ylq2P1MggBbgJmgDylh1+sc+85nPwPKQv7W1FcRx3XXXLVq00NABK84wLHSLcPF36eCDCK+q+T17W5988kkCJ0yHMNbb0+MELdicRo/DMDQMiFidIIBmOMDnxFu4RJgiU4u8VPoj1AGYQFljsXFIfuGFF1522WXweci/d+/eFStWXHvtWl23eyiqwI6j8KkTVMHfJ7w9PrWwcePGv/zlL9OnT4eFMWg4JOxg6DrO8WAcGATGh09oAQxNwuAgfsbvYBCIBBVQM/xOXmCnAZotCRoQyyAo4iuMn80pID/AClx49913A2tgwV27ds2YMePGG2+Ec0GHul4gvaP9iajg7xAeYwVdv/raupdffnnu3LkI3RgWiI1MKgoCGhB1kw/jKqgL0pBUZGG6SvLDsWFqB/+HIoh1aKJBbdAPDtueLpvboX0oGsfXvva1M888ExHknXc2QEHf//79SBzcbhca4y64yYlEwRMVHj3GYrE//vGPL7386llnnUVmxC94MM4xJjvusSykJU8uFZ6cmfiM/B/nbrebmI+GS4qz/cJk6RcnnpNy4/HxyspKkhyddHd3X3nllbB5Nqe+/fbbGMB9990nSQIcBCHgRCS3fY14iMZEvuc4DNkE3YHM4dVPP/30q6++On/ByYAWSBj0htED82iPaFReVkbsRYENqCP7Q1LiczrI/0kRuAoYg9VwF9oTKMjnnYP0gpahUAARBIJBa7gXRIj4j8j/hetvALm+8cYb0Ps3vnE3Is4JOvxhwjvEMymekeJ/+9vf/vjHPz7jjDOCoQiIp6enZ2RkpKGhAaEYDeB+4J9gMAgtkOVJlUVvt23ouD2hACKhT1gSYyWY4BfIg0g+EU+S6Sj4ER0UcaPhR1iYGKHIcAJ8/uRTFt95550Y/JYtWzBvuvfee3EjFHEixj8K7B1axgMpl4Zfff3rX585c2ZVVVXzzJm9fd2w+Sc/+cnFixeDaQAKDHfLpu3PPPMMeIiUiAPGBGoY08W7B6xCtWkILJ8BMjK5fsSIguLbtHn9+IiejIljY3FVG2ycHr3owk8r+dGtm1tCERdrCRBV0/KyKBtcf0ENl3IHoQla2Lf/ABLK733ve719fcDCtGnTbv7yl2xmNe0ctFQF6I1mkA40+G9/+9tHxcn7zGwBdDfccAOsDagvXLhw/4EDmI3e+pUvI7xD9729PSAtAK+muvbNN9+EwMTPGChGViQ8Xc2xXr8eH1fdcsDkB+pr5rbvYV9Z95QRv3DF6vpTVjGLV5Q11i1p3VT+0lvfr6mJLF28umXHkOyNc0KWZyrUvMroYYazLe8MnfwC8lfX1G7bZid/CIEIn8ivIqFw07RGeAsGQ9xBAlI6fELCA3T5fMHlEq+66mpwDHL1RYsWwZJIYzDZuvCCC5KpJIBa9EE7b5VdHkQBfAHTAniEVTurlcKQwdAkTgAd8JFwuL1z577tvtPXLL3jZ68vOKNlzvKu+av6T72g/+qvjvrNq596vIWVBj956fJtWzqRw4muQi4juVxB3Uw7EZEkJxUXNB3uBvnVXO6yyy8HB7/22murV60OhYJogAFDBaUqKxV+ygIWmBM2fPTRXyKXKCsrg53hzwh10O6SJUtsFTI84nwRiphpipAc0hLPEW9Dcii+mMwjsVHtmayLZYxQy67u0z4uXHn372R/Mpf2jY8qfT3jQ/1Z0dd/w31P3/Pd0998s33dSwcvvvScrp5OJAIud143JygRQId4Ck4IBfZ8UZS0fAHZ/lNPPbVp40acgIkeeughmySKqeFh0h5esJtS+GQyDdb40Y9+BEijx/r6egRVgL+6uhagSKftFKWpsQl6gcNDI+vXrwd74UlUmSC+gBYsNqkp0VB5LhlnA/7wth0byv2rr769zx2YGOgIJrOdIlvpkepUfaCzVU7lej/3zSf+9Z+/+8Zb8Xfe/evVV3x5cDDFiSl4sF33KspfSsz4CqdDxpFNZ0A3DzzwANINgBSR6PXXX6eMyyHII717SuGDQf9Xv3obngTxkEUhrgJRcC388sMf/hDVl4aGuomJVCgYgqvjqRgHHk9moSSPkha32yvKOU31oioliEZvR/6UZdM8le90t3kZNldQ/Jm0lldZ3qyDywy1R7t6Umvv/cL9Pzj3rZebd+5679OXfqG/mzdYO6CSqR0mJ/CT6nFvVUUl4i6i/YL585tnzHj22WfBysSRhMEjhZ+S8Do6upBFIXs///zzAR7M1YCipUuXxmJxfH388cdbWvauX//2T37ycOvefcFgKBwKwU3I28lE9LCCylliz8RIVSCSd3uYoa7QqvPUcP1uSQxMJJJlFT6TTZhM2iV5xkeT0bKI21sWy47PX/NaBX/100+k/JW7Vq+4ctPmN6nOWWp/Ep5FbOHs5KrIO3LLnpaTTjoJ0WTPnhYMA7kwJCcCOrLQOqXwMDui96pVqzCjxglSsV/84pGTT14kuz3bt28HFqBvVc3B7RFdiEjhCDjBgMjZ8AtBVJAMiasE/mXZ19sVP2lprnZafmzI8IZy2ZTAGEGeKTN01h9iUrFgMpOUJY/FpFect18yF6x7uqJiWs+smQva2lphdmIvSpYpJOua7pHd+WJFAPEIBU+M9tJLL0XCtW7duk996lMYCQZPQY7A6EDgMNgTSeAapo1/+vOfG5uaVqxciX4xb/3qbbfBlDlVReBFfMW/qqoKUHdZNAqaBe2CmQAtjIlKdHRejMYYaQFmy2fChmmPT000G8I+xpI4M1LQk4wwLrqTFgtN6p5gUmJFU0slh/1j8b61/+fZz32xaevrDWDPlaetSKv9Lq+lZDgLOaSkCfAGRnF5XAWjAELAjCaTSVVXVnQcPPDaKy83NDSFQpHnnnse4sBCkBleMMn4hwmPa6TaRx55BAKgAofEFkklGAXenskoxVrVn9AGzAc7UyDBQUaAtDRdddJ42+y8W+R9Si4muFABUKuqy/a3jmnxNeV1E2ohFY7a8SKTlHjWh2ch2eUYt56rYvh0coxNTqhn337nRZ9P7non2tg4benCK3ds6fGHdF7gCqrocnvMQjkMTlNpO+TKMqn+xRdfBAEhBAKkoGeMDUY9suZ7FNgDJNdff73H40X9BGIjjYUwmD9jJvvnP/8ZXYMCD3lRMd6gPWmUUi6HjSkOW6ZkWoV8Iev2chMTifJog5I1kzF+1vI9plqXTicD/jJAWFFjshhlWE2QTD0vs2ICebBW4KqqgjUL30wPLN3+RsN5V0iFvNbaMupypxlLTCc1X8CH2TM9GmMg2GKE7R3ti5csRczbunVrU1NTfX0dheHSnActJ7M9jPnWW28hY4XYcGaaS0CFgCuV1lCiQy/4vcjk9hwD8sOviITJ/uST+GpTAKMKvEdyCWggcN5MbrCmNhrrb3z5iVODlcOhYGUqIfLyUNBfl0raJV2zEHH5UiAC2eVHUtzXYfnk4Np/e7x5+a7Xn3NdcMEFpywv72rPub2m18/ktTHiM4ovNAUGKsGOv//971FxwDkSEErvnNTo6D6PXwFsmBc6W7lyJURFeEOndoFFFCEqkEm1VwIYznEV5zQzpfCGE7THQSxgWHZmhsReyVged3R0vDuZ7airq0l1XfbC4zO9oUSkakIylkLpkTIZbSzd62Jm86yX0WpFl6azcSVRy0kTn//3Z9zRAzvfqUP1bsWq6Qda824vQp+tZTyxWDUxMUI8C14AzAPwwCzmIyiu0sAwnkkVjsmWx81IFe0JTHMz7E8sAJkpY0O/lLrjMTRXwycpgqaxuIoT8gLStNvDK0oGkYznZIwSLpNMjY7EWmfM0/nh/3jusYrySj8v5XzegGmIEl/hCeQKmWomt5BjvCyv+MUFrKtrpH2u26/c/vNHde9/b3qt8Zq1XzxpftO+3bmMkibLk8dRPRtCwuB4Fub5iEr4CkXQOEvJaDLscQMmBphjY4jIk4ACQgt1jTshGw5057AdXSJdkMAEKjII7A+RgAY7PnO6Zkz4vFGRK+vo3NPZs6Nh3gE5/uBj97HBimGRD7rEkCgEJNFtCt0iM50zyzhtpm2rzJm+cDqfmuuSmc/889O98d+M9Vd9+faL5s5eOjaSAWSoEEAhFo/GLUR7ICloAXnnX//6V0oQaEbsHIcRHkD+wgsv7N69G1WqWbNmI5KjR9wMUR1ioxgOLaIxfsecB9MbFCSoLIFbkGbhHAfO0SaTBlg4LFbEEgMut9HVHi+oblEudLT39Q3uXLWmKj142ob1+z/2qTGtgPpGbb6ggGtdnqySCsoeTXLxSi7uczdkFUtLgcPKTz57w2+ffLdSuuWKa+Zs3tTS09MB1RPinFgL8yBCw3iY6iErj8djIAuMdhLhHzafB85vvvlmzIrhV/MWzD+wvx1JCrK37t5ecB60C98W3al4v6v9wM4Z0yL1lch5Aowrzok6UFokv78Vqq1iZUuSRFP3cYxPkjmGyxV0rE/BlyTNSOq5Gkbsba4/tWWTnhDv+vQtCVG5OJbst2uejB2fACZBUpHbc2LW1PyGzshiTVl9x4Hu9b+4Z81lZz9ZN3vo9q/8U1dnX1l1LhpuSqXHCqrkCh3UkvNMM9HTN/DQTx62GA51nscf/2UwgEILKkg2Qmm2c5jwCOZXXXUVzHXbbbcJoguULoouoB3GzxaXigGwbe/tcnnU66+9y+ea3dUxlMu4w6GKroENLj5CPdJh45+zg7+SdPnDBV5KKrmMpiuixLCmX1MDjJD1es14LGuYSlm0dvfGwrj2nzd+90WPeSXwS+7DcljVKgiuLC8prBHVmWGLS7jF+kDQ0z388ne/2PyVtW/WNQ9f8dnVyBRE9wTw7ndPt9RpGWODx+Xds6/t63f80+w5JyHsP/DAfdOaGpAIlQp/2HIX1YlgZBSYYvFUNFoOLENbqKMxZsElCkiYT15Yc8tN9/7iVy9u6/1y1bz3erqZgORHcCnk7CXHoucfquQABfjFF8oxBS+TFyWRF11RzoiCxrhQr8iV9yf3V1ScXMj6hti+8qXVfMwY7g3NqEMeigBp503oyTIkxuQ5SzZMmH2aZoIX2dF+eUnDLV996N5H7jzrjpv++MqrL6xeelMmFZ+3oDERS6Yybe7goWIxvJKmW/39/U2N9UVStAmbjsMsj5IYLA+qv/322/v6R0DbSBgFkbPjUCiMtVdwya033vnTx37Vrj5yznUDUiQnAEUF0ytjem+vGUF2Mj8++eLXXIrxepjywNwIf4mRnp3JjDLsiAczunylziiIBTks1eppr18wdF8+XZbM9ONem2WxeGOxHG9Isia6dME9lk82s+KwZcpBT3Na2xItC3eP//q+L874/r+9mlUmzvnEaoCoojIcCMpgZJH1tLYdOP3MNfd8459Rfbz88kuvveZzxdXuIuCLozws1IGiENUgPPhDUVXIDG6Dq3vdMni7s73r2rXXvfDSXwf0Ry65OZVQcrs3Bfu6Kzs7mc62ugP75INt+Odpb3O3t8md+9wd+/HPO5Hgujv4DZv2rdv8s86hV3iricufPdLdGBuWsymxr6uQjoesfP1wd3Cknxmb2CPwssADZDKKQDjnOcRIH5JfUwtYUmvEvzAUjIynt7JmROZmLaq8/4v/OnTrbZ9fvHjWNV+4KKfokhjMxqZTogUJYTD4LIwPAi7leTo/THjMh+DnoEqgF/J7/D7dKIDCfL5Ad2ff8mWrykKV6/bet/ITlbGRamVkGabQmjEkibKSVxDoOd6OMZhw28smop3e4f9sYoYB+7mZrJY8OPB269BjCre5pnGaJyhn1QlBdFtmJJNiRcn0+6JRzxmQlmPdHAvJ3ThHUshaMmO5BbYsLJ8dS7ayVrCqYgbHSrGJrq4D01YtvmjVJVveeHn8jjtvw2aPdGZM8kxALlgLARuED4nA0whJFA5LVXCY8HAMZK9QFcIDVeBp8wAWD9Mp5fxzPtnW2sVV9uqCHB9ze1i/MqZz2SZGi7JSPK+ahbyFz7xqf2r4mtPzOZ1192qahNEHwpIUig2nd2/veOa99gcKDNtQc3G0bI7BD7m9HpGrzKQTppVkzQBr+RjTw1oeGJxDqmd6Tc3tYpsNK1UVXp1KZnOpkNcb8HIrqma2+JgbTzkr9uyfft5Ye/LM6bPT2VE51G4ZHngoYAvJgV8IRblQKSVPtvzHPvYxpMRYCUMwh/GhvGg0WoSQJbDC4MDoYP+wO+LPG5bLF89mu8u8CxhVMoxxs+BDACu6PYsAx1ngkiKuLKxMGByP9IOfSIi5Ai/7dE5WYon0hn3fbhv4Q2xCLQuuioZmiIInHGg0dYDci6gJmfEp8Dbg7SBqyZJ3jLGwPylVXVUvuDJcYS5W+JMJ5NTc0kWLdN/vs2mmvqEWvqwk6gUuAAxCcoAfJfZvfetbWNuC/JQFOcdhli8rrxwYHHZ7fAhTuXwcs9sCaoemvQCKqtYzzzz71H89J1dmNJErWH7F4DJZeMcsRQnmzYJucnlM3DXUGKEOv65hNULMa5j681rBsJgCLxZ41rCwhsFnfYGYLIfa+p7e1vG9nZ2/6o+1Se66gHdp2L/SzqNFDl4gyirHJ1k2x5ouVitTlZmma8ztjhQysyR2ts4kAtGQZczCqgBmdFvf6/vC2m/C50XJTsNBk1rBLqtCTpSAk0l7RVhRkNvbJZajC+/3+4BzmqLgTvwPyZEVYW3WG0R1RSuvjHgSDcyYLmR9dtbiatXUYUFtiLiqcoaet4wCV8jzispl8Knxqi7qeUNQGV41WNXgFJ3J6KaiaxldY/lQtLJC8ueHU++19D20Yf9XtnZ8Zyz9ZkXw4xH3uX7+PNk8VzROE6xZqB5Ibl5LI5G4yJ4zcJ0ME4+GA9pEIOr36rm5vYM7meypcxbKSqEnFKzAxFFRh6mOjOZgflsdxX1BgPCUwk9raqQJDNWk0Y6qFLk83CaCEgsv6CN7vDwTC1ePaow0FAvlBS8QOpZQuVw5n4+ywL8qmgqrK4yuuLSsS9LdYsEj6F5B94i6SzREQZcEWyPpiZSpYj3exXICo6j6cHz33qFHXtxx0Xudt/Ypj5vuFn9UDEdmBeSVbubMkHda1LvEzDaG5JMq3J8oTAQ97nRAmGe6v/2bByM10TOGx1tGBy1J8IMy/L4IBg/hiwLb64IQBHFuUhlz8nLV2+vfxXx28+bNLa0tFdGqIgqQb6ngjL27DwwOxLLq3NpFe6uX72QCZjpdgb0DkmgIhekFaxdYghVSFpsTilVWuD2iNcuqAmdxPKb3oAN7FmhfZQUXF8xn/T6xUhI4LPrLriCWKmOJXpfbtAwTUQYejqlOyFsX8jd43WWyWe13zauuns5aXoGTzQIiC6OzWx/+47L//OYNy1bM2nXwyfH+qCeUyKQ0t9uv5VPdfb3R8jLU4LDQAv9fvepUQIES8KOkt/h1/TsbkN5hbrdx04bamsbiAqkqiKbHLScnlI72Xp5jM7mQVN9VtXhbqFbD+KwCl08bZnXcYjMGk0CGgpkYzXxRXPAhbHGWYNMgAm+REXl7ld6bjIisjzfcesHgWGQyol7gJyZ0rO0wLPYzIJtGccq0dNEyZJaRZFm1hEzByLByRubkoN9qmp3f9ZZw/82LF849X9Fb97atlyQ7L8jlMlA9Z0oHOtqXLFu6afNGFJrx3HknnYSk61DifGRuj+Fu3LQF00BExVdefSkcKudY0WJQMzOQ6gWD0VRS2b/hDY5rYvimgjiii3s8Hl8o6BM87Yl0o8lk84VkQcvYWxWw0ow6lJYTTAQCZGrQtz29Bxhxbsccl8sn1nAsajIKb2KZwRLCexZ/vC/oqQU4MPnHHJhhkSKA9hSWKyhZ0eVPSv6srqvY1LF4MdPyTuSbF5+xYN5CKby5bbeqcfuwtuESg6xRbgn9vBnY09Z63fXXP/bLx7Zv34F6JGqtxVrT1JZ/b+NmLEuh0bPP/TfKTx63H8rH3FwpZHzeEMsIrkJgf+fzA/3jsjUH+47sik3OYIWc32xArQ7hJ53KItTb4nGGbiD/DTvR1WRofwJ8gUm4M0G5qrwsygvW0EBBtZRlF/V8fG3nUHcKCQzPuGHtYjUkb1pZ1PYqy6NDw6YQaPPI5bMWjOxYz95z3gXLl83w1+7duGEXb0zzR5SCpsChtFxIY7tExre/4+ATTz551dVXozwzf/58v89XBPwUwmPnz8ZNmzE9xtzmLy8+r2uc3xdCkqBZBZ9PxjY5XbOYkMibYjbZNzEypkx4NCOlM0nLCoOBASqsKSeSipK1l9/hLLCYiRTRntseWmyyJbdPWdn0M3xvQ+VKLbkwrr17znUHF68J7NyOlR0QYAH/GC4PkAJEQAHUYaop0R/PW4kFy5VNLzU98Pk1c2YFPeHNW7caVY0KchuJac5qeyS2WWd7kB1kJ8z+ocHtO3dMnzFj06ZNWH0Ih4I0azi6z6MagYoPpEXpC8wHkqCJGhwYGSLtIqTK5KHj/XIlsSh+BLXSplJQxaHqCpfXUi7RnqcklTzn9kVzuRGvR0t1ZpJZQRcCmKyee33/vNPbRvvLCgpcYkhiqjnoyAAABUnElEnIWQdEqdnkti1YWLnr3dRdn5q74pQzhOCW3u6YyeWocIbH2dsBGAYMj8LE4PBIMc4pO3fuRjHvE584J5vNeb12xfXocR63oeiFLjANQG5H5V5IjlSXZjhUCaRdVGhGB5APgWkjGVW4ILnzNZtM8gKS3QyLkqrLTE4M+GTfcE96OMbmTOZgV+KSW/cvXHOwfcfsiXEeKZ1HnAFT57JlgifuDo1jQTSjDbilJsYamzNr7rb1iTvPP2fxygou8ta2HS28xMNJqWpKFXSqZCJDx49IWCEntkyR30FyjHRK4XEnKtYkPEq3dlJf3OhMpSt0RxVLCqG0W4Zqe2RkOqcU2tGUyEr5QkzHmp1ppjPjwRAfH4mnRtmhbHb3fu1z332zftmWfVvmCpIrEBIzSVZJ+ZNJyxsdTiStwX63O5xkpBTWJRoa3J27+Z/eet2iZbKmx3s7szNnzTWFUTwLD6XUHXbCMGAAKhxfccUVqKqhNoPSPUI2hn2s6i2BGboEbNAdaJ96cdYkqDhPn0cepFQq+FJShcPD+sDPWLhBmduNpaVsrrdzaHRsYkzTrv/xa3NOz2x+e4bJ8Aw/kU6Isi+t6SmfX8gC/1Y4UMZlFa+hzG86aaRtC/uj22uWLg9l8ruQxrp8KsdUWgwPiFFiRgtHpAg4LKyF7UpYd4MIWIDAqMBHxUrOFLCnEieK1tjuB/sDBbQChY7wSV5Nbk+c4dA4VXipVk1JYTGo2PbPKabXF9JNkeU85ZGqndvaYhMZRey/7O5905ZarburQtGKPDuSShdYeTifCzIClpfgVF5vmEkmNcwUp83S9qyvf+o/KrEVIJ3fGvT7VXOPX5qZzL3LGzMwEkgLFeC5GCQxVGIigf1yWGjZv38/9hcUrWU3A1KnFJ7sBreH5YEWeA5qG6RL6pdUSxI68tNXyEm6INU41XsN+zZEqaCxkUCwt71TTQkpI7ni8sC8s8YPHEBp0EgV+llpwu3nksONrJRhmMDgyLg7oGaToqG5mmfnO1vj//VAtSyVyx5TL7ijFUxQnqVqbSJTJbnQ3jYJrVsQQjFyfH7pS19CqoaqJHbT4CvyJbt6foydGSQSZEaGC+ODQqA8iEQzQXRNNcxSm5dCAA1wUCdQP20JkXxCRs0xpoVUr2PfPswPxYi15HK9oy0AfVqilkj1YbavJP3+sCuT1TjBklxBNeczLGnOQqu3NfzEvzR7BEMOxv1+u5idTnhYPcDY6XIWe53ocYRZGiEytJUrVmKLFt72gPEQuSDy+7vXpoY9eqGyPvaYQX844P/olGo7RKQkvGNtpzxCaKdLNJpDA5IMVcOGHOzGyQR9rt7eoZrpkYx7b3oCuwVDalYOeGvTSZ0RUfsYtQxvSu2XhUbD5Otmju3a4PrlvSzPqBFvDS/nDTaN7A2Ta9Y1pGXqOa2el0Yc6inuW7PjK557zTXXYCsJqnLw9iIYMTcFF9rFhSlhj6HDXBg93L4sGh7o782rCsrdwBNiNy1EHunw1B0BhJZBcU7rB3YtxWLDuljNq1leG8lIIdt3BoaDvD0SncnhH2uqUn48nRGkOov15oWmLNdeWTs8vL3mpYfKxHR5ZaXhDee9XJTRTVZIYjWeYcOMe7zAjVpWNXQOR/R6/cVNGmx7Z9fq0884ZcnSjo6DY2MjF154PsyO0Fx0TETuw96dnHJPzuWXXw7lQZ0U1RD5nKXoUuU555N8gdQBRbh4rE9gKV7wuKvTuWGTzQuFSjERVXnfaK5T9GbNvJspyN5AfjxzULWkQmagqUGOt5/2yHcyopyoasyE/E2om6HDSVxDj6btmoA6QEqwxT58bEhCSotVGgyeVuade6e0fOkFbL/Cbnas3kBmJDyI/OA8YpRjHwR7HOQpWloJhjwFXUwktPrmsryR7tyZlvqnwfYRsUFLBXNZNa/kjYw3LFS59UxjNRtrXfazfzkQ9PhEUQv6a0zWAuadbknLjq6RWYFfMDCEJ1jrlltuQcxDJRZPx35BDIPm85Oo7tAIjyHJxRdfDLdB7yB/qBAJP86P0b408pHZMaagm43H8iL2ZElsdU19Hm9fxPK7n8vwc7KD2pjJBS3NZ6kezfIMaIPivGSms/E3PxjySR7B3dLY0Mww2KJkpidsHi2Vn5yr6M+2bSE/9ghiKxJ2ByPIw+xYpaNcg7ZJHVX+KTck4UmgfUxy/vCHP1RWVgE55M9k1kPjONqrqHSJ+K+o+LSR9yEx1LlU0FeWiSvx+HDPwaQU8M5b3JyriI0GU+lILlTDza2d37HOePXnmNDGJTE7b9Zqe14jpA0dm3DAjvbbKJQ7ELeROqBknMM8GN4937gHJ++99x42Dl577TWkGspQ0RK6mGS5KX0erdEddqagI6zbYs5Dy/XHQ/3fNreSFnTTKKtqyCiYAg67+fDSU5f5I0Ihxe68V3/jW4PJt6VI2gv2T212vf39sf2PiqZaYM30onmrRaYJZQ8s7MbG417P3zYMO4An4YF2SAWz33TTTRgw/BRDveOOO6gZ2bxYhrTpgNjaOY6+65oukzuh60svvRwBs5gha9h/TL3YTy7J6qjfI0MgJsHJeCKfiwfsN8SsSEV4eLC7ZfOeg+MdAbOGzas+JokCD++qiTbXqa7xpupweWihx1uuqGNY2EToREFxeHjc67UnF5TPYBUcqxEQFQdmUjg//fTTly1b1jfQjz01v/vd72bMmIbwDJmd3RQQnrzA8U3bEaayJJ5Br9DgAY899hjyRKQ96HGq9kfSKf2iay5TTLlkXs9ysstIZVNlFfXnXLhyyaxTBHcaZZ4hpmqYrzIqOF2KzWyYUVU2PxixMvl9qHazLDbY5VLpeCRkv9JCRymzoH+wErKSU089FSsur7zyCkr02FZB1iYuwDmtu9Es4DDLO2mpYzcCDBEJ7SXEgW1NWMPEnsSa6gb8CCBQkk9v9tk7gVC5Lnlpw0kH8CO9TkITPoIMTgIBH+61dy9kMngQMnCklaCYbFpBS2dXVwmU7LScNhggsMEHITa+Ll66BMJDclQs8OLJXXfdhVsoEy/V1FFtdhjs36cQW3hqXbq1jOQ/44w1iKi0jE1Td1rSoo2H1N4ZMU5AE5CchP+bv9iEYm/vwSgRmYiQ6O1avGZCc2THj97v0K4jUH0R7fEJJJ522mmN05owANgcb1o++OCDZC0yyXGFPwrsJ2GDPB8jwP6sX//611AwbehELIXvIfmHIiAhTeZJ687OJAeojrOhc8dBcAv6AT/hADKLKyV2cu4YrRThlC9Sxo0bgRfsMa2trcUvjz76KGavP/3pT6nogEu0R+64x2HCEyCde4hIqSOMHl+x4oUtxxs2bAC7kn3ArngYbTZ3prGOFii6UMB3ZkT0CEcdjrM4NE4npe3tTNHlgswYDACPq3i3BypG0e3555/HOyYPP/wwcEFqhXYmrclNpYXJsKeRoQsgkN6ZoAIenBy/Q2asXsDB1q5dC8GgeGAVbZAOYscDsSMV8Eg8Gg2VvShTJuQXFWdnDcQ4aA/twO1tXnj/vTpq6eCfXk5E/5ANuoYKsNkKZv/3e7+DrI5Qg6s0fmdyOQnFk7RwdLZ3gEejh+QwL+6E5PjEk7DLBROmd999l2p4KJjQYjA0QoOj/YA0kXQUSpI4zIITogyq/JVSLxnAkRxfiauhbrg99r8j9QLh4Y0qSE66AwXQlH7SfrNjgP/olidFIp+n94FpSosTODmAgKuQEyd4m+EHP/gBAIKNnqgNYlg4IDbthEMzGjFUgPa0S5N8Hpdocx5xBOWOVHXE9mlHcvIsUh9e3sEn+oGQmKjjpeKfPPwwLmWVrP1KI8fh0YADRkUuQ/nYsS0/pfAYFhSJ7gBs2l1No4QAqIdioGgARoU67r//frxj0tQ0HQ+m6h2uYhZIix80z4Xk6IrcgYQHjHFOjooG0CCmT/Zwi7An13CERz9QPtwNfodcCwkcKrO4ar+NjE0sxaoJ+qEduLRx/IMITzbHzYRP5xMnFMaS6RSuAurAhddj/zEMSIU92Q/93wfhgbgE/of86Adas/9cht+PE0IjFQIJ6tQzfqee7V0wHvsFcKxS4ir6Rw/EGrQQ0N3XD8xfcsklV199dTlWb4ZGoFBbv7T4WQR8UUd/ew/FIc5S5JdiYbLlMRRCODG246VEWsQFdsqiZO2yoWq/P3pISJ8HRIDd+FgSxTgAQir442GkC0oHoAv6cweUe0JsqvbDXPRKQEHNozFVY/Ec2vkMV7rk8k9jlgnSgcMDXeFw6P21xkPbu6l25KiAgoUTMhz5jyU8RTtHZkcF9LKO0wV+hwqw6RTjxvPsgrmp07b0lpYWpByYC0EqPDvgsx0EYpRWBBz8EzvgoF3tFBrRkv6uDNSBairqsEhmgCKsNR05MyM7keVL5Sf8Oio4vvDkkPgklnYsT9Q1KXjiaiyO12zyYATkW9hjiAYQhqgeP6J4ChX0dNnvnsJXcVBySi6KCIL2Nu8VPwk+thcwFrQAx8bkHFuAkUdSAMNfESE3noRhogwIXyo/4Z+En2T8KS1P/VJ3Jcxk4wDjo+y11P5FB8ar5XH8VRCcU8TCQSRPmaaet/9IAl48hjuAqGFS6ILCPlmM1kUhG3J7+DDSVZAlFEEsOHNmM14fmSQzfSWSI5B+aMKT5UupzhF+qsypGAKG8VdhyGucuG2H7uJAycLoFqqh1ICojoCKoSOmQmDb54u6Qz9Qx9Kli4+K81JdUHHtQ4M9Rk8xZpL8GPqJ5w8EhM7O7o7OTroRo0S3jjcR/8G2GDdOZs+etWD+PMojSw/S5lEtT7gjjj8S8x+E8AhOk+Lc+2mJ7fkkgJPzO8nsVOP7SH/nBZtoP5xQh4GS2BQhycMp2NKkjfQCFUz60wz0I4XxD/2AogkgR/ZM/kiDLA1yZJ5J7Y9E0OQyFjpyKK30nFIR6o50MWm5l3BOMRlD+RDVcdw/1EjpEMlPZiOeLxX+qL5zmPA2PxUPnOBOsjmd4+REDDvJRXHvB/YL8qxJMhwVVqWBjcZ/XJtTg8OEp4CJX8mxKa4S2omBp4I0RZ0PBnhSEG4/QVGdp5TGcMfgjuTOeI7Bl0cX3gmezpMQqJw4d2wG/gAqIEI9blQr7ZkCuzOSIw1+IoOcDHuCGaGdosUkYUgLNAk56qUPIDxFu6MmEbhEFdhjHGTkY1h4SsCWwrVUWyT/kRnlcWWj6YrTzBk9mZeYmXjkSMo8bucfboPj/KmYI2nzH3w86fqDqfUffPSRt39wojqRoZyI451IPx9Rm49W+I9o0B9Wt1MuV31YD/j/uZ//AYZX6Y0v1pqrAAAAAElFTkSuQmCC";

////////////////////////////////////////////////////////////////////////////////
// Initializers
////////////////////////////////////////////////////////////////////////////////

// Initialize page variables from HTML initial page
function init()
{
  var obj = document.getElementById(PAGE_FIELD_CELLS_PER_LINE);
  if(obj)
    CELLS_PER_LINE = parseInt(obj.value);

  var obj = document.getElementById(PAGE_FIELD_SERVER);
  if(obj)
    SERVER = obj.value;

  var obj = document.getElementById(PAGE_FIELD_PROJECT_DIR);
  if(obj)
    PROJECT_DIR = obj.value;

  var obj = document.getElementById(PAGE_FIELD_TABLES_DIR);
  if(obj)
    TABLES_DIR = obj.value;

  var obj = document.getElementById(PAGE_FIELD_FASTA_FILENAME);
  if(obj)
    GLOBAL_FASTA_FILENAME = obj.value;

  var obj = document.getElementById(PAGE_FIELD_SPECS_MS_FILENAME);
  if(obj)
    GLOBAL_SPECS_MS_FILENAME = obj.value;

  var obj = document.getElementById(PAGE_FIELD_NO_CLUSTERS);
  if(obj)
    GLOBAL_NO_CLUSTERS = obj.value;

  var obj = document.getElementById(PAGE_FIELD_TABLES_LOAD);
  if(obj)
    TABLES_LOAD = (obj.value === 'true');

  var obj = document.getElementById(PAGE_FIELD_TABLES_RELOAD);
  if(obj)
    TABLES_RELOAD = (obj.value === 'true');

  var obj = document.getElementById(PAGE_FIELD_SERVER_UPDATE);
  if(obj)
    SERVER_UPDATE = (obj.value === 'true');

  var obj = document.getElementById(PAGE_FIELD_SERVER_IMAGES);
  if(obj)
    SERVER_IMAGES = (obj.value === 'true');

  var obj = document.getElementById(PAGE_FIELD_DYNAMIC);
  if(obj)
    DYNAMIC = (obj.value === 'true');



  SPECPLOT_VAL_SPECTRA_PKLBIN = PROJECT_DIR + '/' + SPECPLOT_VAL_SPECTRA_PKLBIN;
  CONTPLOT_VAL_STAR           = PROJECT_DIR + '/' + CONTPLOT_VAL_STAR;
  CONTPLOT_VAL_ABRUIJN        = PROJECT_DIR + '/' + CONTPLOT_VAL_ABRUIJN;
  CONTPLOT_VAL_SEQS           = PROJECT_DIR + '/' + CONTPLOT_VAL_SEQS;

  TablesAll = new ReportTables();
  //TablesAll.getData();

  var field = document.getElementById("status");
  if(field)
    field.innerHTML = "Initializing...";

  // preload tables, if they exist
  preloadTables();

  // preload images from the page, if they exist
  preloadImages();

  // get report status
  getStatus();

  // check if there are jump cookies defineds
  if(checkCookies())
    return;

  // show main page
  TablesAll.loadPage(PAGE_INITIAL, true);

  // set the link context menus for the initial page
  TablesAll.setContextMenus();
}
////////////////////////////////////////////////////////////////////////////////
function checkCookies()
{
  for(var i = 0 ; i < 20 ; i++) {
    var cooky = COOKIE_NEW_PREFIX + i;
    var aux = jQuery.cookie(cooky);
    if(aux != null) {
      eval(aux);
      jQuery.cookie(cooky, null);
      return true;
    }
  }
  return false;
}
////////////////////////////////////////////////////////////////////////////////
function setCookie(str)
{
  for(var i = 0 ; i < 20 ; i++) {
    var cooky = COOKIE_NEW_PREFIX + i;
    var aux = jQuery.cookie(cooky);
    if(aux == null) {
      jQuery.cookie(cooky, str);
      return true;
    }
  }
  return false;
}
////////////////////////////////////////////////////////////////////////////////
function preloadTables()
{
  if (typeof T === 'undefined')
    return;

  if(T.length < 5)
    return;

  TablesAll.ProteinsTable.loadData(T[0], "%");
  TablesAll.ProteinCoverageTable.loadData(T[1], "%");
  TablesAll.ContigsTable.loadData(T[2], "%");
  TablesAll.ClustersTable.loadData(T[3], "%");
  TablesAll.SpectraTable.loadData(T[4], "%");
}
////////////////////////////////////////////////////////////////////////////////
function preloadImages()
{
  if (typeof I === 'undefined')
    return;

  for(var i = 0 ; i < I.length ; i++) {

    if(I[i].length < 5)
      continue;

    // build element
    var elem = new cacheElement();
    elem.renderer   = I[i][0];
    elem.params     = I[i][1];
    elem.tag2params = "";
    elem.id         = I[i][2];
    elem.sequence   = I[i][3];
    elem.image      = I[i][4];

    // store it
    TablesAll.iCache.add(elem);
  }
}
////////////////////////////////////////////////////////////////////////////////
function makeTag(content)
{
  return TAG_OPEN + content + TAG_CLOSE;
}
////////////////////////////////////////////////////////////////////////////////
function showMain(ok)
{
	var main  = document.getElementById(DIV_PAGE_MAIN);
	var pages = document.getElementById(DIV_PAGE_DATA);

	if(ok) {
    main.style.display  = "block";
    pages.style.display = "none";
  }	else {
    main.style.display  = "none";
    pages.style.display = "block";
	}
}
////////////////////////////////////////////////////////////////////////////////
// AJAX main call
////////////////////////////////////////////////////////////////////////////////
function AjaxGlobal(sURL, sMethod, sVars, fnDone, sync)
{
  var myConn = new XHConn();
  if (!myConn) alert(CONN_ERR);
  myConn.connect(sURL, sMethod, sVars + '&' + REPORT_SERVER_PAR_REQUEST_ID + '=' + requestID++, fnDone, sync);
}
////////////////////////////////////////////////////////////////////////////////
function getStatus()
{
  var field = document.getElementById("status");

  if(!TABLES_RELOAD) {

    if(TABLES_LOAD) {
      if(field)
        field.innerHTML = "Loading data...";
      TablesAll.getData();
    }

    globalStatus = STATUS_OK;
    field.style.backgroundColor = "#ffffff";
    field.innerHTML = "Completed";
    return;
  }

  fnDone7 = function (oXML) {
    if(field) {
      globalStatus = oXML.responseText;

      if(globalStatus == STATUS_RETRIEVE) {
        field.style.backgroundColor = "yellow";
      } else if(globalStatus == STATUS_ERROR) {
        field.style.backgroundColor = "red";
      } else if(globalStatus == STATUS_OK) {
        if(globalStatusPrev != STATUS_OK && !TABLES_RELOAD) {
          field.style.backgroundColor = "#ffffff";
          field.innerHTML = "Loading data...";
          TablesAll.getData();
        }
        field.style.backgroundColor = "lightgreen";
      } else {
        field.style.backgroundColor = "#ffffff";
      }
      field.innerHTML = globalStatus;
    }
    globalStatusPrev = globalStatus;
    setTimeout(function() {getStatus();}, 10000);
  };

  if(field) {
    var thePage = SERVER + SPS_REPORTS;
    var params = REPORT_SERVER_PAR_STATUS;
    params += '&' + REPORT_SERVER_PAR_PROJECT_DIR + '&' + PROJECT_DIR;
    params += '&' + REPORT_SERVER_PAR_FILENAME    + '&' + STATUS_FILENAME;
    AjaxGlobal(thePage, "GET", params, fnDone7, true);
  }
}
////////////////////////////////////////////////////////////////////////////////
// Image Cache
////////////////////////////////////////////////////////////////////////////////
function cacheElement()
{
  // renderer to be used
  this.renderer   = "";
  // parameters for renderer
  this.params     = "";
  // where to store the non changed parameters for the image (only the user sequence should change) <input> ID
  this.tag2params = "";
  // the unique ID used to identify the image
  this.id         = 0;
  // the user sequence, to check for change
  this.sequence   = "";
  // the image contents
  this.image      = "";

  // additional elements for queue

  // where to put the image <image> ID
  this.tag        = "";
  // where to store the params for later usage (image update) <input> ID
  this.tag2       = "";
  // href or src. Used to now which object tag should contain the image
  this.target     = "";
}
////////////////////////////////////////////////////////////////////////////////
// Image cache object. Stores images do avoid duplicate requests to server
////////////////////////////////////////////////////////////////////////////////
function ImageCache()
{
  // Image processing queue
  this.queue = new Array();

  // the actual cache
  if(IMAGE_CACHE_BST) {
    this.cache = new BST();
    return;
  }
  // Array cache type
  this.cache = new Array();
}

// Translate string to number
ImageCache.prototype.string2Number = function(str)
{
  var v = 0;
  for(var i = 0 ; i < str.length ; i++)
    v += (str[str.length - i - 1].charCodeAt() - 48) * Math.pow(36, i);
  return v;
}

ImageCache.prototype.add = function(e)
{
  if(IMAGE_CACHE_BST) {
    var id = this.string2Number(e.id);
    this.cache.insert(id, e);
  } else
    // Array cache type
    this.cache.push(e);
}

ImageCache.prototype.update = function(i, element)
{
  if(IMAGE_CACHE_BST) {
    var obj = this.cache.search(i);
    obj.value = element;
  } else
    // Array cache type
    this.cache[i] = element;
}

ImageCache.prototype.get = function(i)
{
  if(IMAGE_CACHE_BST) {
    var aux = this.cache.search(i);
    return aux.value;
  }
  // Array cache type
  return this.cache[i];
}

ImageCache.prototype.find = function(key)
{
  if(IMAGE_CACHE_BST) {
    var id = this.string2Number(key);
    node = this.cache.search(id);
    if(node != null)
      return node.key;
  } else {

    // Array cache type
    for(var i = 0 ; i < this.cache.length ; i++)
      if(this.cache[i].id == key)
        return i;
  }

  return -1;
}
////////////////////////////////////////////////////////////////////////////////
// Load entry point function and image load functions
ImageCache.prototype.loadImage = function(renderer, params, theTag, target, force, sync, sequence)
{
  // image chache index
  var index = -1;

  // cache search section

  if(!force && USE_IMAGE_CACHE) {
    // check for image in cache
    index = this.find(theTag);
    // ignore cache if not found
    if(index != -1) {
      // get element
      var elem = this.get(index);
      //check for sequence changes
      if(elem.sequence == sequence) {
        // set the image
        var obj = document.getElementById(theTag);
        if(obj) {
          if(target == "href")
            obj.href = "data:image/png;base64," + elem.image;
          else
            obj.src = "data:image/png;base64," + elem.image;
        }
        // and exit
        return;
      }
    }
  }

  // if images can't be acquired from the server, exit
  if(!SERVER_IMAGES) {
    var obj2 = document.getElementById(theTag);
    if(obj2) {
      if(target == "href")
        obj2.href = "data:image/png;base64," + imageNa;
      else
        obj2.src = "data:image/png;base64," + imageNa;
    }
    return;
  }

  // we need to get the image

  // create a local variable so that it can be used by callback function
  var tag = theTag;
  var This = this;
  // callback function for assyncronous call to server
  fnDone = function (oXML) {

    var obj2 = document.getElementById(tag);
    if(obj2) {
      if(target == "href")
        obj2.href = "data:image/png;base64," + oXML.responseText;
      else
        obj2.src = "data:image/png;base64," + oXML.responseText;
    }

    // add element to cache
    var aux = new cacheElement();
    aux.renderer   = renderer;
    aux.params     = params;
    aux.tag2params = "";
    aux.id         = tag;
    aux.sequence   = sequence;
    aux.image      = oXML.responseText;

    if(USE_IMAGE_CACHE)
      if(index == -1)
        This.add(aux);
      else
        This.update(index, aux);
  };


  // what to get
  var thePage = SERVER + renderer;
  // connect to server
  AjaxGlobal(thePage, "GET", params, fnDone, sync);
}
////////////////////////////////////////////////////////////////////////////////
// Process Image queue
//
// Send assyncronous image requests to server and put them in place
//
ImageCache.prototype.processQueue = function()
{
  for(var i = 0 ; i < this.queue.length ; i++) {

    // get image
    this.loadImage(this.queue[i].renderer, this.queue[i].params, this.queue[i].tag, this.queue[i].target, false, true, this.queue[i].sequence);

    // store parameters for image update
    var obj = document.getElementById(this.queue[i].tag2);
    if(obj) {
      obj.value = this.queue[i].tag2params;
    }
  }

  // clear queue
  this.queue = [];
}
////////////////////////////////////////////////////////////////////////////////
// Reference Utilities
////////////////////////////////////////////////////////////////////////////////
// Create a variable reference to allow primitive data types to be passed-by-reference
function createReference(value)
{
   var newVar = new Array();
   newVar[0] = value;
   return newVar;
}
////////////////////////////////////////////////////////////////////////////////
// set reference variable's value
function setReference(val, value)
{
   val[0] = value;
}
////////////////////////////////////////////////////////////////////////////////
// add to variable
function addToReference(val, value)
{
   val[0] += value;
}
////////////////////////////////////////////////////////////////////////////////
// Auxiliary functions
////////////////////////////////////////////////////////////////////////////////
// Sort comparison function.
function orderSortingFunction(v1, v2)
{
  return (v1[1] == v2[1] ? v1[2] - v2[2] : v1[1] - v2[1]);
}
////////////////////////////////////////////////////////////////////////////////
function propComparator(col, dir) {
  return function(a, b) {
    aa = a[col].replace(/(<([^>]+)>)/ig,"");
    bb = b[col].replace(/(<([^>]+)>)/ig,"");
    if (aa.match(/^-?[£$¤]?[\d,.]+%?$/) && bb.match(/^-?[£$¤]?[\d,.]+%?$/)) {
      aa = parseFloat(aa.replace(/[^0-9.-]/g,''));
      if (isNaN(aa)) aa = 0;
      bb = parseFloat(bb.replace(/[^0-9.-]/g,''));
      if (isNaN(bb)) bb = 0;
      if(dir)
        return bb-aa;
      return aa-bb;
    }

    if (aa == bb) return 0;
    if (aa < bb && dir == 2) return 1;
    if (aa < bb) return -1;
    if(dir) return -1;
    return 1;
    //return a[col] - b[col];
  }
}
////////////////////////////////////////////////////////////////////////////////
function shaker_sort(list, comp_func)
{
  // A stable sort function to allow multi-level sorting of data
  // see: http://en.wikipedia.org/wiki/Cocktail_sort
  var b = 0;
  var t = list.length - 1;
  var swap = true;

  while(swap) {
    swap = false;
    for(var i = b; i < t; ++i) {
      if ( comp_func(list[i], list[i+1]) > 0 ) {
        var q = list[i]; list[i] = list[i+1]; list[i+1] = q;
        swap = true;
      }
    } // for
    t--;

    if (!swap) break;

    for(var i = t; i > b; --i) {
      if ( comp_func(list[i], list[i-1]) < 0 ) {
        var q = list[i]; list[i] = list[i-1]; list[i-1] = q;
        swap = true;
      }
    } // for
    b++;

  } // while(swap)
}
////////////////////////////////////////////////////////////////////////////////
;(function() {

  var defaultComparator = function (a, b) {
    if (a < b) {
      return -1;
    }
    if (a > b) {
      return 1;
    }
    return 0;
  }

  Array.prototype.mergeSort = function( comparator ) {
    var i, j, k,
        firstHalf,
        secondHalf,
        arr1,
        arr2;

    if (typeof comparator != "function") { comparator = defaultComparator; }

    if (this.length > 1) {
      firstHalf = Math.floor(this.length / 2);
      secondHalf = this.length - firstHalf;
      arr1 = [];
      arr2 = [];

      for (i = 0; i < firstHalf; i++) {
        arr1[i] = this[i];
      }

      for(i = firstHalf; i < firstHalf + secondHalf; i++) {
        arr2[i - firstHalf] = this[i];
      }

      arr1.mergeSort( comparator );
      arr2.mergeSort( comparator );

      i=j=k=0;

      while(arr1.length != j && arr2.length != k) {
        if ( comparator( arr1[j], arr2[k] ) <= 0 ) {
          this[i] = arr1[j];
          i++;
          j++;
        }
        else {
          this[i] = arr2[k];
          i++;
          k++;
        }
      }

      while (arr1.length != j) {
        this[i] = arr1[j];
        i++;
        j++;
      }

      while (arr2.length != k) {
        this[i] = arr2[k];
        i++;
        k++;
      }
    }
  }
})();
////////////////////////////////////////////////////////////////////////////////
// generate a click event for the object
function triggerClick(id)
{
  var clicky = document.createEvent('HTMLEvents');clicky.initEvent('click', true, true);
  var aux = document.getElementById(id);
  if(aux)
    aux.dispatchEvent(clicky);
}
////////////////////////////////////////////////////////////////////////////////
function validateStatus()
{
  if(globalStatus != STATUS_OK)
    return false;
  showMain(false);
  return true;
}
////////////////////////////////////////////////////////////////////////////////
// ReportTables class.
// Holds all report tables
////////////////////////////////////////////////////////////////////////////////
function pageQueueElement(t,i,s)
{
  this.currentPageType  = t;
  this.currentPageID    = i;
  this.currentPageStart = s;
}
///////////////////////////////////////
function ReportTables()
{
  // keep track of what king of page is being displayed (page type)
  this.currentPageType;
  // keep track of what page is being displayed (data)
  this.currentPageData;

  // Image cache
  this.iCache = new ImageCache();

  // page Queue
  this.pageQueue = new Array();

  // page queue position
  this.pageQueueLocation = -1;

  // create table objects
  this.ProteinsTable        = new tableProtein();
  this.ProteinCoverageTable = new tableProteinCoverage();
  this.ContigsTable         = new tableContig();
  this.ClustersTable        = new tableCluster();
  this.SpectraTable         = new tableInputSpectra();

  // Protein coverage buffer -- used to keep protien edition state while navigatin away
  this.proteinCoverageState = new Array();
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.getData = function()
{
  // load tables into memory
  this.ProteinsTable.getData();
  this.ProteinCoverageTable.getData();
  this.ContigsTable.getData();
  this.ClustersTable.getData();
  this.SpectraTable.getData();
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.getElementOC = function(par)
{
  var aux = par.attr('onclick');
  if(typeof(aux) != 'undefined')
    if(aux.length > 0)
      return aux;

  aux = par.find("p");
  if(typeof(aux) != 'undefined') {
    var aux2 = aux.attr('onclick');
    if(typeof(aux2) != 'undefined')
      if(aux2.length > 0)
        return aux2;
  }

  aux = par.find("img");
  if(typeof(aux) != 'undefined') {
    var aux2 = aux.attr('onclick');
    if(typeof(aux2) != 'undefined')
      if(aux2.length > 0)
        return aux2;
  }

  return undefined;
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.setContextMenus = function()
{
  This = this;

	jQuery(document).ready( function() {

		jQuery("A").contextMenu({
			menu: 'myMenu'
		},
			function(action, el, pos) {

			  if(action == 'newtab') {
          jQuery(document).ready(function() {

            var aux = This.getElementOC(jQuery(el));
            if(typeof(aux) != 'undefined')
              setCookie(aux);
            jQuery(this).target = "_blank";
            window.open(jQuery(el).attr("href"));
            return false;
          });
			  }

			  if(action == 'newwin') {
          jQuery(document).ready(function() {

            var aux = This.getElementOC(jQuery(el));
            if(typeof(aux) != 'undefined')
              setCookie(aux);
            var NWin = window.open(jQuery(el).attr("href"), '', 'height=800,width=800');
            if (window.focus) {
              NWin.focus();
            }
		      });
        }
      });

	});
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.afterPageload = function(page, data)
{
  switch(page) {

  case PAGE_INITIAL:
    break;

  case PAGE_PROTEIN:
    break;

  case PAGE_PROTEIN_COVERAGE:
    this.restoreCoverage(data);
    break;

  case PAGE_CONTIGS:
    break;

  case PAGE_CONTIG:
    break;

  case PAGE_CLUSTER:
    break;

  case PAGE_SPECTRA:
    break;

  }

  this.setContextMenus();

  // make tables sortable
  //sorttable.makeSortable(document.getElementById('dataTable'));

  // set current page type
  this.currentPageType = page;

  // set current page data;
  this.currentPageData = data;
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.onPageExit = function(page, data)
{
  switch(page) {

  case PAGE_INITIAL:
    break;

  case PAGE_PROTEINS:
    break;

  case PAGE_PROTEIN:
    break;

  case PAGE_PROTEIN_COVERAGE:
    this.saveCoverage(data);
    break;

  case PAGE_CONTIGS:
    break;

  case PAGE_CONTIG:
    break;

  case PAGE_CLUSTER:
    break;

  case PAGE_SPECTRA:
    break;

  }
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.sortTable = function(tab, dataCol, reportType, reportData)
{
  switch(tab) {
  case TABLE_PROTEIN_ID:
    this.setWorkingImage(DIV_PAGE_DATA);
    this.ProteinsTable.sortTable(dataCol);
    break;
  case TABLE_CONTIG_ID:
    this.setWorkingImage(DIV_PAGE_DATA);
    this.ContigsTable.sortTable(dataCol);
    break;
  case TABLE_CLUSTER_ID:
    this.setWorkingImage(DIV_PAGE_DATA);
    this.ClustersTable.sortTable(dataCol);
    break;
  case TABLE_SPECTRA_ID:
    this.setWorkingImage(DIV_PAGE_DATA);
    this.SpectraTable.sortTable(dataCol);
    break;
  case TABLE_COVERAGE_ID:
    this.setWorkingImage(DIV_PAGE_DATA);
    this.ProteinCoverageTable.sortTable(dataCol);
    break;
  default:
    return;
  }

  this.gotoPage(reportType, reportData);
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.goBack = function()
{
  // test if we are at the end of the queue
  if(this.pageQueueLocation <= 0)
    return;

  // get the previous element in queue
  var aux = this.pageQueue[--this.pageQueueLocation];

  // get the page, based on the queue element
  this.gotoPage(aux.currentPageType, aux.currentPageID, aux.currentPageStart);
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.goForward = function()
{
  // test if we are at the end of the queue
  if(this.pageQueueLocation >= this.pageQueue.length - 1 )
    return;

  // get the previous element in queue
  var aux = this.pageQueue[++this.pageQueueLocation];
  // get the page, based on the queue element
  this.gotoPage(aux.currentPageType, aux.currentPageID, aux.currentPageStart);
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.loadPage = function(page, id, start)
{
  this.pageQueue.length = this.pageQueueLocation + 1;
  this.pageQueue.push(new pageQueueElement(page,id,start));
  this.pageQueueLocation = this.pageQueue.length - 1;
  this.gotoPage(page, id, start);
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.gotoPage = function(page, id, start)
{
  switch(page) {
  case PAGE_INITIAL:
    showMain(id);
    break;
  case PAGE_PROTEINS:
    this.loadProteinsPage(start);
    break;
  case PAGE_PROTEIN:
    this.loadProteinPage(id, start);
    break;
  case PAGE_CONTIGS:
    this.loadContigsPage(start);
    break;
  case PAGE_CONTIG:
    this.loadContigPage(id, start);
    break;
  case PAGE_CLUSTER:
    this.loadClusterPage(id, start);
    break;
  case PAGE_SPECTRA:
    this.loadInputSpectraPage(id, start);
    break;
  case PAGE_PROTEIN_COVERAGE:
    this.loadProteinDetails(id);
    break;
  default:
    return;
  }
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.loadProteinsPage = function(start)
{
  if(!validateStatus())
    return;

  // exit page procedure
  this.onPageExit(this.currentPageType, this.currentPageData);

  // build report object
  rep = new ReportProtein();
  // set the table
  rep.proteinsPage(this.ProteinsTable);
  // check if the table is to be loaded or just set from memory
  if(TABLES_RELOAD) {
    // set loading image
    this.setLoadingImage(DIV_PAGE_DATA);
    // retrieve tables data
    rep.getData();
  }

  var This = this;

  this.setWorkingImage(DIV_PAGE_DATA);
  setTimeout(function() {

  // define renderer
  var r = new renderer(DYNAMIC);
  r.reportType = PAGE_PROTEINS;
  r.reportData = -1;
  r.queueSize = This.pageQueue.length;
  r.queueLocation = This.pageQueueLocation;

  // build entry point for pagination
  var fn = "TablesAll.loadPage(" + PAGE_PROTEINS + ",0,";
  // build the report
  r.buildReport(DIV_PAGE_DATA, rep, start, PAGE_LENGTH * 2, fn, 1);
  // call image queue processor
  This.iCache.processQueue();
  // entry page procedure
  This.afterPageload(PAGE_PROTEINS);

  }, 10);
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.loadProteinPage = function(protein, start)
{
  if(!validateStatus())
    return;

  // exit page procedure
  this.onPageExit(this.currentPageType, this.currentPageData);

  // build report object
  rep = new ReportProtein();
  // set the table
  rep.proteinPage(protein, this.ProteinsTable, this.ContigsTable);
  // check if the table is to be loaded or just set from memory
  if(TABLES_RELOAD) {
    // set loading image
    this.setLoadingImage(DIV_PAGE_DATA);
    // retrieve tables data
    rep.getData();
  }

  var This = this;

  this.setWorkingImage(DIV_PAGE_DATA);
  setTimeout(function() {

  // define renderer
  var r = new renderer(DYNAMIC);
  r.reportType = PAGE_PROTEIN;
  r.reportData = protein;
  r.queueSize = This.pageQueue.length;
  r.queueLocation = This.pageQueueLocation;

  // build entry point for pagination
  var fn = "TablesAll.loadPage(" + PAGE_PROTEIN + "," + protein + ",";
  // build the report
  r.buildReport(DIV_PAGE_DATA, rep, start, PAGE_LENGTH, fn, 1);
  // call image queue processor
  This.iCache.processQueue();
  // entry page procedure
  This.afterPageload(PAGE_PROTEIN, protein);

  }, 10);
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.loadContigsPage = function(start)
{
  if(!validateStatus())
    return;

  // exit page procedure
  this.onPageExit(this.currentPageType, this.currentPageData);

  // build report object
  rep = new ReportContig();
  // set the table
  rep.contigsPage(this.ContigsTable);
  // check if the table is to be loaded or just set from memory
  if(TABLES_RELOAD) {
    // set loading image
    this.setLoadingImage(DIV_PAGE_DATA);
    // retrieve tables data
    rep.getData();
  }

  var This = this;

  this.setWorkingImage(DIV_PAGE_DATA);
  setTimeout(function() {

  // define renderer
  var r = new renderer(DYNAMIC);
  r.reportType = PAGE_CONTIGS;
  r.reportData = -1;
  r.queueSize = This.pageQueue.length;
  r.queueLocation = This.pageQueueLocation;

  // build entry point for pagination
  var fn = "TablesAll.loadPage(" + PAGE_CONTIGS + ",0,";
  // build the report
  r.buildReport(DIV_PAGE_DATA, rep, start, PAGE_LENGTH, fn);
  // call image queue processor
  This.iCache.processQueue();
  // entry page procedure
  This.afterPageload(PAGE_CONTIGS);

  }, 10);
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.loadContigPage = function(contig, start)
{
  if(!validateStatus())
    return;

  // exit page procedure
  this.onPageExit(this.currentPageType, this.currentPageData);

  // build report object
  rep = new ReportContig();
  // set the table
  rep.contigPage(contig, GLOBAL_NO_CLUSTERS, this.ContigsTable, this.ClustersTable, this.SpectraTable);
  // check if the table is to be loaded or just set from memory
  if(TABLES_RELOAD) {
    // set loading image
    this.setLoadingImage(DIV_PAGE_DATA);
    // retrieve tables data
    rep.getData();
  }

  // get protein ID
  protein = rep.getField(0, 0, 1);
  var navType = 2;
  if(protein[0] == -1) navType = 3;

  var This = this;

  this.setWorkingImage(DIV_PAGE_DATA);
  setTimeout(function() {

  // define renderer
  var r = new renderer(DYNAMIC);
  r.reportType = PAGE_CONTIG;
  r.reportData = contig;
  r.queueSize = This.pageQueue.length;
  r.queueLocation = This.pageQueueLocation;

  // build entry point for pagination
  var fn = "TablesAll.loadPage(" + PAGE_CONTIG + "," + contig + ",";
  // build the report
  r.buildReport(DIV_PAGE_DATA, rep, start, PAGE_LENGTH, fn, navType);
  // call image queue processor
  This.iCache.processQueue();
  // entry page procedure
  This.afterPageload(PAGE_CONTIG, contig);

  }, 10);
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.loadClusterPage = function(cluster, start)
{
  if(!validateStatus())
    return;

  // exit page procedure
  this.onPageExit(this.currentPageType, this.currentPageData);

  // build report object
  rep = new ReportCluster();
  // set the table
  rep.clusterPage(cluster, this.ClustersTable, this.SpectraTable);
  // check if the table is to be loaded or just set from memory
  if(TABLES_RELOAD) {
    // set loading image
    this.setLoadingImage(DIV_PAGE_DATA);
    // retrieve tables data
    rep.getData();
  }

  // get protein ID
  protein = rep.getField(0, 0, 2);
  var navType = 2;
  if(protein[0] == 0) navType = 4;

  var This = this;

  this.setWorkingImage(DIV_PAGE_DATA);
  setTimeout(function() {

  // define renderer
  var r = new renderer(DYNAMIC);
  r.reportType = PAGE_CLUSTER;
  r.reportData = cluster;
  r.queueSize = This.pageQueue.length;
  r.queueLocation = This.pageQueueLocation;

  // build entry point for pagination
  var fn = "TablesAll.loadPage(" + PAGE_CLUSTER + "," + cluster + ",";
  // build the report
  r.buildReport(DIV_PAGE_DATA, rep, start, PAGE_LENGTH, fn, navType);
  // call image queue processor
  This.iCache.processQueue();
  // entry page procedure
  This.afterPageload(PAGE_CLUSTER, cluster);

  }, 10);
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.loadInputSpectraPage = function(fileIndex, start)
{
  if(!validateStatus())
    return;

  // exit page procedure
  this.onPageExit(this.currentPageType, this.currentPageData);

  // build report object
  rep = new ReportInputSpectra();
  // set the table
  rep.inputSpectraPage(fileIndex, GLOBAL_NO_CLUSTERS, this.SpectraTable);
  // check if the table is to be loaded or just set from memory
  if(TABLES_RELOAD) {
    // set loading image
    this.setLoadingImage(DIV_PAGE_DATA);
    // retrieve tables data
    rep.getData();
  }

 var This = this;

  this.setWorkingImage(DIV_PAGE_DATA);
  setTimeout(function() {

  // define renderer
  var r = new renderer(DYNAMIC);
  r.reportType = PAGE_SPECTRA;
  r.reportData = fileIndex;
  r.queueSize = This.pageQueue.length;
  r.queueLocation = This.pageQueueLocation;

  // build entry point for pagination
  var fn = "TablesAll.loadPage(" + PAGE_SPECTRA + "," + fileIndex + ",";
  // build the report
  r.buildReport(DIV_PAGE_DATA, rep, start, PAGE_LENGTH, fn);
  // call image queue processor
  This.iCache.processQueue();
  // entry page procedure
  This.afterPageload(PAGE_SPECTRA, fileIndex);

  }, 10);
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.loadProteinDetails = function(protein)
{
  if(!validateStatus())
    return;

  // exit page procedure
  this.onPageExit(this.currentPageType, this.currentPageData);

  // build report object
  rep = new ReportProteinCoverage();
  // set the table
  rep.proteinCoveragePage(protein, this.ProteinCoverageTable);
  // check if the table is to be loaded or just set from memory
  if(TABLES_RELOAD) {
    // set loading image
    this.setLoadingImage(DIV_PAGE_DATA);
    // retrieve tables data
    rep.getData();
  }

  var This = this;

  this.setWorkingImage(DIV_PAGE_DATA);
  setTimeout(function() {

  // define renderer
  var r = new renderer(DYNAMIC);
  r.reportType = PAGE_PROTEIN_COVERAGE;
  r.reportData = protein;
  r.queueSize = This.pageQueue.length;
  r.queueLocation = This.pageQueueLocation;

  // build the report
  r.buildReport(DIV_PAGE_DATA, rep, null, null, "", 2);
  // call image queue processor
  This.iCache.processQueue();
  // entry page procedure
  This.afterPageload(PAGE_PROTEIN_COVERAGE, protein);

  }, 10);
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.loadProteinDetailsCSV = function(protein)
{
  if(!validateStatus())
    return;

  // build report object
  rep = new ReportProteinCoverage();
  // set the table
  rep.proteinCoverageCSVPage(protein, this.ProteinCoverageTable);
  // check if the table is to be loaded or just set from memory
  if(TABLES_RELOAD) {
    // retrieve tables data
    rep.getData();
  }

  // define renderer
  var r = new renderer(DYNAMIC);
  r.reportType = PAGE_PROTEIN_COVERAGE_CSV;
  r.reportData = protein;
  r.queueSize = This.pageQueue.length;
  r.queueLocation = This.pageQueueLocation;

  // build the report. NEW means it will open a new window/tab
  r.buildReport('NEW', rep, null, null, "", 2);
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.setLoadingImage = function(div)
{
  this.setImage(div, loadingImage2);
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.setWorkingImage = function(div)
{
  this.setImage(div, workingImage);
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.setImage = function(div, image)
{
  // set loading image
  var aux = "<table align='center'><tr><td align='center'><img src='data:image/gif;base64," + image + "' /></td></tr></table>";
  // set data on page
  var target = document.getElementById(div);
  if(target)
    target.innerHTML = aux;
}

////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.updateContig = function(fieldId, textId, img, ctrl, target, row, col)
{
  var inData  = document.getElementById(fieldId);
  var outData = document.getElementById(textId);

  // test for inexistent input element
  if(!inData)
    return;

  // get data
  var str = inData.value.toUpperCase();

  // test for target and set string
  if(outData)
    outData.innerHTML = str;

  // update the local tables
  if(!TABLES_RELOAD)
    TablesAll.ContigsTable.updateField(TABLE_CONTIGS_FIELD_ID, row, col, str);

  // update the tables thru the server
  if(SERVER_UPDATE)
    updateField(TABLE_CONTIG_ID, TABLE_CONTIGS_FIELD_ID, row, col, str);

  // get params for image generation
  var paramsObj = document.getElementById(ctrl);
  if(!paramsObj) return;
  var params = paramsObj.value;

  if(str)
    params += '&' + CONTPLOT_PAR_SEQ_USER + '="' + str + '"';
  // load the image
  this.iCache.loadImage(CONTIG_RENDERER, params, img, target, false, true, str)
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.updateCluster = function(fieldId, textId, img, ctrl, target, row, col, sync)
{
  var inData  = document.getElementById(fieldId);
  var outData = document.getElementById(textId);

  var str = inData.value.toUpperCase();

  if(outData)
    outData.innerHTML = str;

  // update the local tables
  if(!TABLES_RELOAD)
    TablesAll.ClustersTable.updateField(TABLE_CLUSTER_FIELD_ID, row, col, str);

  // update the tables thru the server
  if(SERVER_UPDATE)
    updateField(TABLE_CLUSTER_ID, TABLE_CLUSTER_FIELD_ID, row, col, str);

  // get params for image generation
  var paramsObj = document.getElementById(ctrl);
  if(!paramsObj) return;
  var params = paramsObj.value;

  if(str)
    params += '&' + SPECPLOT_PAR_PEPTIDE+ '="' + str + '"';
  // load the image
  this.iCache.loadImage(SPECTRUM_RENDERER, params, img, target, false, sync, str)
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.updateSpectra = function(fieldId, textId, img, ctrl, target, row, col, sync)
{
  var inData  = document.getElementById(fieldId);
  var outData = document.getElementById(textId);

  var str = inData.value.toUpperCase();

  if(outData)
    outData.innerHTML = str;

  // update the local tables
  if(!TABLES_RELOAD)
    TablesAll.SpectraTable.updateField(TABLE_SPECTRA_FIELD_ID, row, col, str);

  // update the tables thru the server
  if(SERVER_UPDATE)
    updateField(TABLE_SPECTRA_ID, TABLE_SPECTRA_FIELD_ID, row, col, str);

 // get params for image generation
  var paramsObj = document.getElementById(ctrl);
  if(!paramsObj) return;
  var params = paramsObj.value;

  if(str)
    params += '&' + SPECPLOT_PAR_PEPTIDE + '="' + str + '"';
  // load the image
  this.iCache.loadImage(SPECTRUM_RENDERER, params, img, target, false, sync, str)
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.saveCoverage = function(data)
{
  if(!DYNAMIC)
    return;

  // rows holder. Holds the rows data
  var rows = new Array();

  // row index counter
  var k = 0;

  // go thru all AA cells
  for(var i = 0 ; i < globalProteinLength ; i += CELLS_PER_LINE) {

    // where to save the sequence. 1st element is 'checked', subsequence are cell contents for that row
    var row = new Array();

    // get row state checkbox
    var ckId = 'ck' + i;
    var ckObj = document.getElementById(ckId);

    // save row state
    row[0] = ckObj.checked;

    // go thru all AA cells for the row
    for(var j = i ; j < i + CELLS_PER_LINE && j < globalProteinLength ; j++) {

      // get the cell ID
      var dataId = INP_ELEM_PREFIX + j;
      var dataVal = document.getElementById(dataId);
      // get the cell content
      row[j - i + 1] = dataVal.value;
    }
    // store the row
    rows[k++] = row;
  }
  this.proteinCoverageState[data] = rows;
}
////////////////////////////////////////////////////////////////////////////////
ReportTables.prototype.restoreCoverage = function(data)
{
  if(!DYNAMIC)
    return;

  // check if data is present
  if(typeof(data) == 'undefined' || typeof(this.proteinCoverageState[data]) == 'undefined')
    return;

  // row index counter
  var k = 0;

  // go thru all AA cells
  for(var i = 0 ; i < globalProteinLength && k < this.proteinCoverageState[data].length ; i += CELLS_PER_LINE, k++) {

    // get row state checkbox
    var ckId = 'ck' + i;
    var ckObj = document.getElementById(ckId);

    // get row state
    ckObj.checked = this.proteinCoverageState[data][k][0];

    // go thru all AA cells for the row
    for(var j = i ; j < i + CELLS_PER_LINE && j < globalProteinLength; j++) {

      // get the cell ID
      var dataId = INP_ELEM_PREFIX + j;
      var dataVal = document.getElementById(dataId);

      // put the cell content
      if(j - i + 1 < this.proteinCoverageState[data][k].length)
        dataVal.value = this.proteinCoverageState[data][k][j - i + 1];
    }
  }
}
////////////////////////////////////////////////////////////////////////////////
function fillCoverageRow(obj, i)
{
  if(!obj.checked) return;
  for(var j = i ; j < i + CELLS_PER_LINE && j < globalProteinLength ; j++) {
    var aux1 = PEP_ELEM_PREFIX + j;
    var aux2 = INP_ELEM_PREFIX + j;
    var obj1 = document.getElementById(aux1);
    var obj2 = document.getElementById(aux2);
    if(obj1 && obj2)
      obj2.value = obj1.innerHTML;
  }
}
////////////////////////////////////////////////////////////////////////////////
function submitCoverage()
{
  var sequence = "";

  for(var i = 0 ; i < globalProteinLength ; i += CELLS_PER_LINE) {

    var ckId = 'ck' + i;
    var ckObj = document.getElementById(ckId);

    for(var j = i ; j < i + CELLS_PER_LINE && j < globalProteinLength ; j++) {

      var dataId = INP_ELEM_PREFIX + j;
      var dataVal = document.getElementById(dataId);
      var pepId = PEP_ELEM_PREFIX + j;
      var pepVal = document.getElementById(pepId);

      //if(dataVal.value.length && ckObj.checked)
      //  sequence += dataVal.value.toUpperCase();
      //else
      //  sequence += pepVal.innerHTML;

      if(ckObj.checked) {
        if(dataVal.value.length)
          sequence += dataVal.value.toUpperCase();
      } else
        sequence += pepVal.innerHTML;
    }
  }

  var ProtID   = document.getElementById('ProtID').value;
  var ProtDesc = document.getElementById('ProtDESC').value;

  if(ProtID.length == 0 || ProtDesc.length == 0 || sequence.length ==0) {
    var msg = "Attention!\n\nThe following fields are empty:\n\n";
    msg += (ProtID.length == 0 ? "Protein ID\n" : "");
    msg += (ProtDesc.length == 0 ? "Description\n" : "");
    msg += (sequence.length == 0 ? "Protein sequence\n" : "");
    alert(msg);
    return;
  }

  var params = REPORT_SERVER_PAR_LAUNCH + '=' + RELAUNCH_SCRIPT;
  params += '&' + REPORT_SERVER_PAR_PROJECT_DIR + '=' + PROJECT_DIR;
  params += '&' + REPORT_SERVER_PAR_FILENAME    + '=' + GLOBAL_FASTA_FILENAME;
  params += '&' + REPORT_SERVER_PAR_ID          + '="' + ProtID + '"';
  params += '&' + REPORT_SERVER_PAR_DESCRIPTION + '="' + ProtDesc + '"';
  params += '&' + REPORT_SERVER_PAR_SEQUENCE    + '="' + sequence + '"';

  // callback
  fnDone8 = function (oXML) {
    // goto main page
    document.location = INITIAL_PAGE;
  };
  // AJAX call
  var thePage = SERVER + SPS_REPORTS;
  AjaxGlobal(thePage, "POST", params, fnDone8, false);
  // reset global status
  globalStatus = "";
}
////////////////////////////////////////////////////////////////////////////////
function updateField(table, filterField, filterData, updateField, updateData)
{
  var params = REPORT_SERVER_PAR_UPDATE;
  params += '&' + REPORT_SERVER_PAR_TABLE         + '=' + table;
  params += '&' + REPORT_SERVER_PAR_TABLES_DIR    + '=' + TABLES_DIR;
  params += '&' + REPORT_SERVER_PAR_PROJECT_DIR   + '=' + PROJECT_DIR;

  params += '&' + REPORT_SERVER_PAR_FILTER_FIELD  + '=' + filterField;
  params += '&' + REPORT_SERVER_PAR_FILTER_DATA   + '=' + filterData;
  params += '&' + REPORT_SERVER_PAR_UPDATE_FIELD  + '=' + updateField;
  if(updateData.length)
    params += '&' + REPORT_SERVER_PAR_UPDATE_DATA + '=' + updateData;
  else
    params += '&' + REPORT_SERVER_PAR_CLEAR_DATA;

  // callback
  fnDone = function (oXML) {
  };
  // SJAX call
  var thePage = SERVER + SPS_REPORTS;
  AjaxGlobal(thePage, "GET", params, fnDone, true);
}
////////////////////////////////////////////////////////////////////////////////
// Column types
////////////////////////////////////////////////////////////////////////////////
function ReportParamsOption(p, o, v, s)
{
  this.param      = p;
  this.option     = o;
  this.validator  = v;
  this.store      = typeof(s) != 'undefined' ? s : 1;
}
////////////////////////////////////////////////////////////////////////////////
function ReportColumnTypeBase()
{
  this.cssClass     = "";     // CSS class name for HTML formating
  this.dynamic      = false;  // specifies a cell with content dynamically used (content sent to server)
  this.columnLabel  = "";     // label on the table column
  this.link         = "";     // URL template for the link
  this.onClick      = "";     // template for onClick HTML method
  this.id           = "";     // template for field ID, needed to read or write data to
  this.validator    = "";     // validator must be not null in order for the cell to be displayed
  this.rtti         = "base"; // RTTI emulation in JS
  this.sortDataCol  = -1;     // Data table columns associated with sorting this HTML column
}
////////////////////////////////////////////////////////////////////////////////
function ReportColumnTypeImageOnDemand()
{
  this.rtti         = REPORT_CELL_TYPE_IOD;
  this.iconRenderer = "";             // renderer used to generate the icon. If empty, iconParams treated as image/URL
  this.iconParams   = new Array();    // Icon path/image/URL   vector<ReportParamsOption>
  this.iconSequence = "";

  this.label        = "";             // label to show for the link (defined by renderer and params)
  this.renderer     = "";             // Object name used for rendering the Image On Demand
  this.params       = new Array();    // parameters passed to the renderer object for  the Image On Demand  vector<ReportParamsOption>
  this.imgSequence  = "";
  this.splitLabel   = "false";        // specifies if the label is a sequence that needs to be split into chunks

  // When using a CGI call, the command is constructed in the following way:
  // /cgi-bin/<renderer> <params>
  //
  // when rendering local static pages, the renderer name is used to generate/request a render object by name (using a object factory model)
  // and <params> are passed to build the image
}

ReportColumnTypeImageOnDemand.prototype = new ReportColumnTypeBase();
////////////////////////////////////////////////////////////////////////////////
function ReportColumnTypeString()
{
  this.rtti       = REPORT_CELL_TYPE_STRING;
  this.text       = "";       // Text template for cell contents, button, input box.
  this.splitText  = "false";  // specifies if the text is a sequence that needs to be split into chunks
  this.isButton   = false;    // If true, a button is drawn with the text in the "text" field
  this.isInput    = false;    // if True, an input box is drawn
}

ReportColumnTypeString.prototype = new ReportColumnTypeBase();
////////////////////////////////////////////////////////////////////////////////
function ReportColumnTypeStringMultiple()
{
  this.rtti       = REPORT_CELL_TYPE_STRING_MULTIPLE;
  this.linkPrefix = ""; // link filename prefix
  this.linkSuffix = ""; // link filename suffix
  this.text       = ""; // Text template for cell contents.
}

ReportColumnTypeStringMultiple.prototype = new ReportColumnTypeBase();
////////////////////////////////////////////////////////////////////////////////
function ReportColumnTypeBox()
{
  this.rtti       = REPORT_CELL_TYPE_BOX;
  this.sequences = new Array(); // Vector of several column types. vector<ReportColumnTypeBase *>
}

ReportColumnTypeBox.prototype = new ReportColumnTypeBase();
////////////////////////////////////////////////////////////////////////////////
// Table base class
////////////////////////////////////////////////////////////////////////////////
function table()
{
  // the table rows
  this.theArray = [];

  // the indexing vector for sorting and filtering the table
  this.tableIndex = [];

  // the iterator current position.
  this.iteratorPosition = -1;

  // the column types
  this.colTypes = [];

  // table type
  this.tableType = -1;

  // should the table borders be drawn?
  this.drawBorders = 1;

  // field to filter data by
  this.filterField = -1;
  // data filter
  this.filterData = "";

  // sort column. Default is none.
  this.sortColumn       = -1;
  // sorting direction. False means increasing
  this.sortDirection    = false;

  // drawing exceptions:
  this.exception = "";
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.clearView = function()
{
  this.colTypes         = [];
  this.tableIndex       = [];
  this.iteratorPosition = -1;
  this.drawBorders      =  1;
  this.filterField      = -1;
  this.filterData       = "";
  this.exception        = "";
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.clearFilter = function()
{
  this.filterField  = -1;
  this.filterData   = "";
  this.tableIndex   = [];
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.setFilter = function(field, data)
{
  this.filterField = field;
  this.filterData = data;
  this.applyFilter();
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.applyFilter = function()
{
  // clear the filter
  this.tableIndex = [];
  // if there is no filtering rule, we're done
  if(this.filterField == -1 || this.filterData == "")
    return;

  // build the index array based on the filter
  for(var i = 0 ; i < this.theArray.length ; i++)
    if(this.theArray[i][this.filterField] == this.filterData)
      this.tableIndex.push(i);

  //var aux = this.tableType + " : ";
  //for(var i = 0 ; i < this.tableIndex.length ; i++)
  //  aux += "(" + this.tableIndex[i] + " -> " + this.theArray[this.tableIndex[i]] + ")  ";
  //alert(aux);
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.getSize = function()
{
  if(this.tableIndex.length)
    return this.tableIndex.length;
  return this.theArray.length;
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.getFirst = function()
{
  this.iteratorPosition = 0;

  return this.getCurrent();
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.getLast = function()
{
  if(this.tableIndex.length)
    return this.tableIndex[this.tableIndex.length - 1];
  else
    if(this.theArray.length)
      return this.theArray.length - 1;

  return -2;
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.getNext = function(add)
{
  if(typeof(add) == 'undefined')
    this.iteratorPosition++;
  else
    this.iteratorPosition += add;

  return this.getCurrent();
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.getAt = function(pos)
{
  if(typeof(pos) == 'undefined')
    return -1;

  if(this.tableIndex.length) {
    if(pos >= this.tableIndex.length)
      return -2;
  } else
    if(pos >= this.theArray.length)
      return -2;

  if(this.tableIndex.length)
    return this.tableIndex[pos];
  return pos;
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.peek = function(pos)
{
  if(typeof(pos) == 'undefined')
    return -1;

  var ret = this.getAt(pos);

  if(ret >= 0)
    return pos;

  return this.getLast();
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.moveTo = function(pos)
{
  this.iteratorPosition = pos;

  return this.getCurrent();
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.getCurrent = function()
{
  // check for invalid values
  if(this.iteratorPosition < 0)
    return this.iteratorPosition;

  if(this.tableIndex.length) {
    if(this.iteratorPosition >= this.tableIndex.length)
      return this.iteratorPosition = -2;
  } else
    if(this.iteratorPosition >= this.theArray.length)
      return this.iteratorPosition = -2;

  if(this.tableIndex.length)
    return this.tableIndex[this.iteratorPosition];
  return this.iteratorPosition;
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.getId = function()
{
  return [];
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.getSingleId = function(row)
{
  if(row < this.theArray.length)
    return this.theArray[row][0];
  return -1;
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.getField = function(row, col)
{
  var aux = [];
  if(row < this.theArray.length)
    if(col < this.theArray[row].length)
      aux.push(this.theArray[row][col]);

  return aux;
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.updateField = function(filterField, filterData, col, value)
{
  for(var i = 0 ; i < this.theArray.length ; i++)
    if(this.theArray[i][filterField] == filterData)
      this.theArray[i][col] = value;
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.loadData = function(data, sep)
{
  if(typeof(sep) === 'undefined')
    sep = "\n";

  var aux = data.split(sep);
  this.theArray = new Array(aux.length);
  for(var i = 0 ; i < aux.length ; i++) {

    var aux2 = aux[i].split(";");

    var arrayItem = new Array();

    for(var j = 0 ; j < aux2.length ; j++) {
      arrayItem[j] = aux2[j];
    }
    this.theArray[i] = arrayItem;
  }
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.getData = function()
{
  var params = REPORT_SERVER_PAR_GET;
  params += '&' + REPORT_SERVER_PAR_TABLE       + '&' + this.tableType;
  params += '&' + REPORT_SERVER_PAR_TABLES_DIR  + '&' + TABLES_DIR;
  params += '&' + REPORT_SERVER_PAR_PROJECT_DIR + '&' + PROJECT_DIR;

  if(this.filterField >= 0) {
    params += '&' + REPORT_SERVER_PAR_FILTER_FIELD + '&' + this.filterField;
    params += '&' + REPORT_SERVER_PAR_FILTER_DATA  + '&' + this.filterData;
  }

  if(TABLES_RELOAD && this.sortColumn >= 0) {
    params += '&' + REPORT_SERVER_PAR_SORT_FIELD + '&' + this.sortColumn;
    if(this.sortDirection)
      params += '&' + REPORT_SERVER_PAR_SORT_REVERSE;
  }

  // As the data is already filtered, internal filter must be cleared
  this.tableIndex = [];

  // this
  var This = this;
  // callback
  fnDone = function (oXML) {
    This.loadData(oXML.responseText);
  };
  // SJAX call
  var thePage = SERVER + SPS_REPORTS;
  AjaxGlobal(thePage, "GET", params, fnDone, false);
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.sortTableServer = function(dataCol)
{
  this.sortDirection = (this.sortColumn == dataCol ? !this.sortDirection : false);
  this.sortColumn = dataCol;
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.sortTable = function(dataCol)
{
  if(TABLES_RELOAD) {
    this.sortTableServer(dataCol)
    return;
  }

  if(this.sortColumn == dataCol) {
    this.sortDirection = !this.sortDirection;
    this.reverseTable();
    return;
  }

  this.sortColumn = dataCol;
  this.sortDirection = false;
  //shaker_sort(this.theArray, propComparator(dataCol, this.sortDirection) );
  this.theArray.sort(propComparator(dataCol, this.sortDirection) );
}
////////////////////////////////////////////////////////////////////////////////
table.prototype.reverseTable = function()
{
  var j = this.theArray.length / 2;
  for(var i = 0 ; i < j ; i++) {
    var aux = this.theArray[i];
    this.theArray[i] = this.theArray[this.theArray.length - i - 1];
    this.theArray[this.theArray.length - i - 1] = aux;
  }
}
////////////////////////////////////////////////////////////////////////////////
// Table Protien
////////////////////////////////////////////////////////////////////////////////
function tableProtein()
{
  //table.call( this );
  this.tableType = TABLE_PROTEIN_ID;
}

tableProtein.prototype = new table();
////////////////////////////////////////////////////////////////////////////////
tableProtein.prototype.getId = function()
{
  var aux = [];

  if(this.tableIndex.length)
    aux.push(this.theArray[this.tableIndex[0]][0]);
  else
    if(this.theArray.length)
      aux.push(this.theArray[0][0]);

  return aux;
}
////////////////////////////////////////////////////////////////////////////////
tableProtein.prototype.defineView = function()
{
  // clear view
  this.clearView();

  // colTypes[0] . (CTstring) Protein name in fasta file
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_PROTEINS_0;
  auxS.sortDataCol  = TABLE_PROTEINS_FIELD_NAME;
  auxS.text         = TAG_TABLE_PROTEINS_FIELD_NAME;
  auxS.link         = "#";
  auxS.onClick      = "javascript:TablesAll.loadPage(" + PAGE_PROTEIN + "," + TAG_TABLE_PROTEINS_FIELD_ID + ");";
  this.colTypes.push(auxS);

  // colTypes[1] . (CTstring) Protein description
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_PROTEINS_1;
  auxS.text         = TAG_TABLE_PROTEINS_FIELD_DESC;
  this.colTypes.push(auxS);

  // colTypes[2] . (CTstring) contigs
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_PROTEINS_2;
  auxS.sortDataCol  = TABLE_PROTEINS_FIELD_CONTIGS;
  auxS.text         = TAG_TABLE_PROTEINS_FIELD_CONTIGS;
  this.colTypes.push(auxS);

  // colTypes[3] . (CTstring) spectra
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_PROTEINS_3;
  auxS.sortDataCol  = TABLE_PROTEINS_FIELD_SPECTRA;
  auxS.text         = TAG_TABLE_PROTEINS_FIELD_SPECTRA;
  this.colTypes.push(auxS);

  // colTypes[4] . (CTstring) Amino acids
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_PROTEINS_4;
  auxS.sortDataCol  = TABLE_PROTEINS_FIELD_AAS;
  auxS.text         = TAG_TABLE_PROTEINS_FIELD_AAS;
  this.colTypes.push(auxS);

  // colTypes[5] . (CTstring) coverage %
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_PROTEINS_5;
  auxS.sortDataCol  = TABLE_PROTEINS_FIELD_COVERAGE;
  auxS.text         = TAG_TABLE_PROTEINS_FIELD_COVERAGE;
  this.colTypes.push(auxS);
}
////////////////////////////////////////////////////////////////////////////////
tableProtein.prototype.defineView2 = function()
{
  // clear view
  this.clearView();

  this.exception = "ProteinException";
}
////////////////////////////////////////////////////////////////////////////////
// Table Protien Coverage
////////////////////////////////////////////////////////////////////////////////
function tableProteinCoverage()
{
  this.tableType = TABLE_COVERAGE_ID;
}
////////////////////////////////////////////////////////////////////////////////
tableProteinCoverage.prototype = new table();

////////////////////////////////////////////////////////////////////////////////
tableProteinCoverage.prototype.getId = function()
{
  var aux = [];

  if(this.tableIndex.length)
    aux.push(this.theArray[this.tableIndex[0]][0]);
  else
    if(this.theArray.length)
      aux.push(this.theArray[0][0]);

  return aux;
}
////////////////////////////////////////////////////////////////////////////////
tableProteinCoverage.prototype.defineView = function()
{
  // clear view
  this.clearView();

  this.exception = "ProteinCoverageException";
}
////////////////////////////////////////////////////////////////////////////////
tableProteinCoverage.prototype.defineView2 = function()
{
  // clear view
  this.clearView();

  this.exception = "ProteinCoverageExceptionCSV";
}
////////////////////////////////////////////////////////////////////////////////
// Table contig
////////////////////////////////////////////////////////////////////////////////
function tableContig()
{
  this.tableType = TABLE_CONTIG_ID;
}
////////////////////////////////////////////////////////////////////////////////
tableContig.prototype = new table();

////////////////////////////////////////////////////////////////////////////////
tableContig.prototype.getId = function()
{
  var aux = [];

  if(this.tableIndex.length)
    aux.push(this.theArray[this.tableIndex[0]][1]);
  else
    if(this.theArray.length)
      aux.push(this.theArray[0][1]);

  //if(this.theArray.length) {
  //  aux.push(this.theArray[0][1]);
  //  //aux.push(this.theArray[0][0]);
  //}
  return aux;
}
////////////////////////////////////////////////////////////////////////////////
tableContig.prototype.buildUpdateCall = function(inputID, suffix)
{
  var aux = "javascript:TablesAll.updateContig(\"" + inputID + "\", \"" + suffix + "\", \"" + IMAGE_ICON_ID_PREFIX + suffix + "\", \"" + IMAGE_ICON_CTRL_ID_PREFIX + suffix + "\", \"src\", " + TAG_TABLE_CONTIGS_FIELD_ID + ", " + TABLE_CONTIGS_FIELD_SEQ_USER + ");";
  return aux;
}
////////////////////////////////////////////////////////////////////////////////
tableContig.prototype.defineView = function()
{
  // clear view
  this.clearView();

  var conts  = "cs" + TAG_TABLE_CONTIGS_FIELD_ID;
  var inputID = "input_contig_" + TAG_INTERNAL_ROW + "_" + TAG_INTERNAL_COL;

  ///////////////////////////////////////////////////////////////////////////////
  // View for contig list
  ////////////////////////////////////////
  // Table colTypes has the following structure:

  // colTypes[0] . (CTstring) Contig index
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_CONTIGS_0;
  auxS.text         = TAG_TABLE_CONTIGS_FIELD_ID; //"«0»";
  auxS.sortDataCol  = TABLE_CONTIGS_FIELD_ID;
  this.colTypes.push(auxS);

  // colTypes[1] . (CTstring) Number of spectra
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_CONTIGS_1;
  auxS.text         = TAG_TABLE_CONTIGS_FIELD_SPECTRA;
  auxS.sortDataCol  = TABLE_CONTIGS_FIELD_SPECTRA;
  this.colTypes.push(auxS);

  // colTypes[2] . (CTstring) Tool involved
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_CONTIGS_2;
  auxS.text         = TAG_TABLE_CONTIGS_FIELD_TOOL;
  auxS.sortDataCol  = TABLE_CONTIGS_FIELD_TOOL;
  this.colTypes.push(auxS);


  // colTypes[3] . (CTIOD) Contig image
  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.link              = "#";
  auxI.onClick           = "javascript:TablesAll.loadPage(" + PAGE_CONTIG + "," + TAG_TABLE_CONTIGS_FIELD_ID + ");";
  auxI.columnLabel       = REPORT_HEADER_CONTIGS_3;
  auxI.iconRenderer      = CONTIG_RENDERER;
  auxI.iconSequence      = TAG_TABLE_CONTIGS_FIELD_SEQ_USER;
  auxI.id                = conts;

  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_STAR,           CONTPLOT_VAL_STAR,          CONTPLOT_COND_STAR            ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_ABRUIJN,        CONTPLOT_VAL_ABRUIJN,       CONTPLOT_COND_ABRUIJN         ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_SEQS,           CONTPLOT_VAL_SEQS,          CONTPLOT_COND_SEQS            ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_CONTIG,         CONTPLOT_VAL_CONTIG,        CONTPLOT_COND_CONTIG          ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_MASS_REF,       CONTPLOT_VAL_MASS_REF,      CONTPLOT_COND_MASS_REF        ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_MASS_HOM,       CONTPLOT_VAL_MASS_HOM,      CONTPLOT_COND_MASS_HOM        ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_OFF_REF,        CONTPLOT_VAL_OFF_REF,       CONTPLOT_COND_OFF_REF         ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_OFF_HOM,        CONTPLOT_VAL_OFF_HOM,       CONTPLOT_COND_OFF_HOM         ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_REVERSE,        CONTPLOT_VAL_REVERSE,       CONTPLOT_COND_REVERSE         ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_TARGET,         CONTPLOT_VAL_TARGET,        CONTPLOT_COND_TARGET          ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_ENCODING,       CONTPLOT_VAL_ENCODING,      CONTPLOT_COND_ENCODING        ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_NO_TITLE,       CONTPLOT_VAL_NO_TITLE,      CONTPLOT_COND_NO_TITLE        ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_ZOOM,           CONTPLOT_VAL_ZOOM,          CONTPLOT_COND_ZOOM            ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_SEQ_REFERENCE,  CONTPLOT_VAL_SEQ_REFERENCE, CONTPLOT_COND_SEQ_REFERENCE   ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_SEQ_HOMOLOG,    CONTPLOT_VAL_SEQ_HOMOLOG,   CONTPLOT_COND_SEQ_HOMOLOG     ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_SEQ_DENOVO,     CONTPLOT_VAL_SEQ_DENOVO,    CONTPLOT_COND_SEQ_DENOVO      ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_IMAGE_LIMIT_X,  CONTPLOT_VAL_IMAGE_LIMIT_X_SMALL, CONTPLOT_COND_IMAGE_LIMIT_X    ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_IMAGE_LIMIT_Y,  CONTPLOT_VAL_IMAGE_LIMIT_Y, CONTPLOT_COND_IMAGE_LIMIT_Y    ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_SEQ_USER,       CONTPLOT_VAL_SEQ_USER,      CONTPLOT_COND_SEQ_USER,     0 ) );

  this.colTypes.push(auxI);


  // colTypes[2] . (CTseqsBox)
  var auxB = new ReportColumnTypeBox();
  auxB.columnLabel  = REPORT_HEADER_CONTIGS_4;

  auxI = new ReportColumnTypeImageOnDemand();
  auxI.columnLabel  = REPORT_SEQ_NAME_REFERENCE;
  auxI.label        = TAG_TABLE_CONTIGS_FIELD_SEQ_REF;
  auxI.validator    = TAG_TABLE_CONTIGS_FIELD_SEQ_REF;
  auxI.splitLabel   = "true";
  auxB.sequences.push(auxI);

  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.columnLabel  = REPORT_SEQ_NAME_HOMOLOG;
  auxI.label        = TAG_TABLE_CONTIGS_FIELD_SEQ_HOM;
  auxI.validator    = TAG_TABLE_CONTIGS_FIELD_SEQ_HOM;
  auxI.splitLabel   = "true";
  auxB.sequences.push(auxI);

  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.columnLabel  = REPORT_SEQ_NAME_DENOVO;
  auxI.label        = TAG_TABLE_CONTIGS_FIELD_SEQ_NOVO;
  auxI.validator    = TAG_TABLE_CONTIGS_FIELD_SEQ_NOVO;
  auxI.splitLabel   = "true";
  auxB.sequences.push(auxI);

  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.dynamic      = true;
  auxI.columnLabel  = REPORT_SEQ_NAME_USER;
  auxI.label        = TAG_TABLE_CONTIGS_FIELD_SEQ_USER;
  auxI.splitLabel   = "true";
  auxI.id           = conts;
  auxB.sequences.push(auxI);

  var auxS = new ReportColumnTypeString();
  auxS.isInput      = true;
  auxS.dynamic      = true;
  auxS.id           = inputID;
  auxB.sequences.push(auxS);

  var auxS = new ReportColumnTypeString();
  auxS.isButton     = true;
  auxS.dynamic      = true;
  auxS.text         = REPORT_BUTTON_UPDATE;
  auxS.onClick      = this.buildUpdateCall(inputID, conts);
  auxB.sequences.push(auxS);

  this.colTypes.push(auxB);


  // colTypes[3] . (CTstring) protein
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_CONTIGS_5;
  auxS.sortDataCol  = TABLE_CONTIGS_FIELD_PROTEIN_NAME;
  auxS.text         = TAG_TABLE_CONTIGS_FIELD_PROTEIN_NAME + "<br><br>" + TAG_TABLE_CONTIGS_FIELD_PROTEIN_DESC;
  auxS.link         = "#";
  auxS.onClick      = "javascript:TablesAll.loadPage(" + PAGE_PROTEIN + "," + TAG_TABLE_CONTIGS_FIELD_PROTEIN + ");";
  this.colTypes.push(auxS);
}
////////////////////////////////////////////////////////////////////////////////
tableContig.prototype.defineView2 = function()
{
  // clear view
  this.clearView();

  var cont  = "c" + TAG_TABLE_CONTIGS_FIELD_ID;
  var inputID = "input_contig_" + TAG_INTERNAL_ROW + "_" + TAG_INTERNAL_COL;

  var auxB = new ReportColumnTypeBox();
  auxB.columnLabel  = "";

  // the image
  auxI = new ReportColumnTypeImageOnDemand();
  auxI.columnLabel       = "";
  auxI.iconRenderer      = CONTIG_RENDERER;
  auxI.iconSequence      = TAG_TABLE_CONTIGS_FIELD_SEQ_USER;
  auxI.id                = cont;

  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_STAR,           CONTPLOT_VAL_STAR,          CONTPLOT_COND_STAR            ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_ABRUIJN,        CONTPLOT_VAL_ABRUIJN,       CONTPLOT_COND_ABRUIJN         ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_SEQS,           CONTPLOT_VAL_SEQS,          CONTPLOT_COND_SEQS            ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_TITLE,          CONTPLOT_VAL_TITLE,         CONTPLOT_COND_TITLE           ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_CONTIG,         CONTPLOT_VAL_CONTIG,        CONTPLOT_COND_CONTIG          ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_MASS_REF,       CONTPLOT_VAL_MASS_REF,      CONTPLOT_COND_MASS_REF        ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_MASS_HOM,       CONTPLOT_VAL_MASS_HOM,      CONTPLOT_COND_MASS_HOM        ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_OFF_REF,        CONTPLOT_VAL_OFF_REF,       CONTPLOT_COND_OFF_REF         ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_OFF_HOM,        CONTPLOT_VAL_OFF_HOM,       CONTPLOT_COND_OFF_HOM         ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_REVERSE,        CONTPLOT_VAL_REVERSE,       CONTPLOT_COND_REVERSE         ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_TARGET,         CONTPLOT_VAL_TARGET,        CONTPLOT_COND_TARGET          ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_ENCODING,       CONTPLOT_VAL_ENCODING,      CONTPLOT_COND_ENCODING        ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_SEQ_REFERENCE,  CONTPLOT_VAL_SEQ_REFERENCE, CONTPLOT_COND_SEQ_REFERENCE   ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_SEQ_HOMOLOG,    CONTPLOT_VAL_SEQ_HOMOLOG,   CONTPLOT_COND_SEQ_HOMOLOG     ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_SEQ_DENOVO,     CONTPLOT_VAL_SEQ_DENOVO,    CONTPLOT_COND_SEQ_DENOVO      ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_IMAGE_LIMIT_X,  CONTPLOT_VAL_IMAGE_LIMIT_X, CONTPLOT_COND_IMAGE_LIMIT_X   ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_IMAGE_LIMIT_Y,  CONTPLOT_VAL_IMAGE_LIMIT_Y, CONTPLOT_COND_IMAGE_LIMIT_Y   ) );
  auxI.iconParams.push( new ReportParamsOption(CONTPLOT_PAR_SEQ_USER,       CONTPLOT_VAL_SEQ_USER,      CONTPLOT_COND_SEQ_USER,     0 ) );

  auxB.sequences.push(auxI);


  // the input sequence
  var auxS = new ReportColumnTypeString();
  auxS.isInput      = true;
  auxS.dynamic      = true;
  auxS.id           = inputID;
  auxB.sequences.push(auxS);

  // the "update" button
  var auxS = new ReportColumnTypeString();
  auxS.isButton     = true;
  auxS.dynamic      = true;
  auxS.text         = REPORT_BUTTON_UPDATE;
  auxS.onClick      = this.buildUpdateCall(inputID, cont);
  auxB.sequences.push(auxS);

  this.colTypes.push(auxB);
}
////////////////////////////////////////////////////////////////////////////////
// Table Cluster consensus
////////////////////////////////////////////////////////////////////////////////
function tableCluster()
{
  this.tableType = TABLE_CLUSTER_ID;
}
////////////////////////////////////////////////////////////////////////////////
tableCluster.prototype = new table();

////////////////////////////////////////////////////////////////////////////////
tableCluster.prototype.getId = function()
{
  var aux = [];

  if(this.tableIndex.length) {
    aux.push(this.theArray[this.tableIndex[0]][2]);
    aux.push(this.theArray[this.tableIndex[0]][1]);
  } else
    if(this.theArray.length) {
      aux.push(this.theArray[0][2]);
      aux.push(this.theArray[0][1]);
    }

  //if(this.theArray.length) {
  //  aux.push(this.theArray[0][2]);
  //  aux.push(this.theArray[0][1]);
  //  //aux.push(this.theArray[0][0]);
  //}
  return aux;
}
////////////////////////////////////////////////////////////////////////////////
tableCluster.prototype.buildUpdateCall = function(inputID, suffix, icon)
{
  var aux = "";

  if(typeof(icon) != 'undefined' && icon) {
    aux = "javascript:TablesAll.updateCluster(\"" + inputID + "\", \"" + suffix + "\", \"" + IMAGE_LARGE_ID_PREFIX + suffix + "\", \"" + IMAGE_LARGE_CTRL_ID_PREFIX + suffix + "\", \"href\", " + TAG_TABLE_CLUSTER_FIELD_ID + "," + TABLE_CLUSTER_FIELD_USER + ", false);";
    aux += "triggerClick(\"" + IMAGE_LARGE_ID_PREFIX + suffix + "\", false);";
  } else {
    aux = "javascript:TablesAll.updateCluster(\"" + inputID + "\", null, \"" + IMAGE_ICON_ID_PREFIX + suffix + "\", \"" + IMAGE_ICON_CTRL_ID_PREFIX + suffix + "\", \"src\", " + TAG_TABLE_CLUSTER_FIELD_ID + "," + TABLE_CLUSTER_FIELD_USER + ", true);";
  }

  return aux;
}
////////////////////////////////////////////////////////////////////////////////
tableCluster.prototype.defineView = function()
{
  // clear view
  this.clearView();

  var clusts  = "ls" + TAG_TABLE_CLUSTER_FIELD_ID;
  var clustR  = "lR" + TAG_TABLE_CLUSTER_FIELD_ID;
  var clustH  = "lH" + TAG_TABLE_CLUSTER_FIELD_ID;
  var clustN  = "lN" + TAG_TABLE_CLUSTER_FIELD_ID;
  var clustU  = "lU" + TAG_TABLE_CLUSTER_FIELD_ID;
  var inputID = "input_cluster_" + TAG_INTERNAL_ROW + "_" + TAG_INTERNAL_COL;

  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_CLUSTERS_0;
  auxS.sortDataCol  = TABLE_CLUSTER_FIELD_ID;
  auxS.text         = TAG_TABLE_CLUSTER_FIELD_ID;
  this.colTypes.push(auxS);

  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_CLUSTERS_1;
  auxS.sortDataCol  = TABLE_CLUSTER_FIELD_TOOL;
  auxS.text         = TAG_TABLE_CLUSTER_FIELD_TOOL;
  this.colTypes.push(auxS);


  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.link            = "#";
  auxI.onClick         = "javascript:TablesAll.loadPage(" + PAGE_CLUSTER + "," + TAG_TABLE_CLUSTER_FIELD_ID + ");";
  auxI.columnLabel     = REPORT_HEADER_CLUSTERS_2;
  auxI.label           = "";
  auxI.iconRenderer    = SPECTRUM_RENDERER;
  auxI.validator       = TAG_CLUSTER_PEPTIDE_ALL;
  auxI.id              = clusts;

  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,     SPECPLOT_VAL_CLUSTER_PKLBIN,      SPECPLOT_COND_CLUSTER_PKLBIN      ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM,   SPECPLOT_VAL_CLUSTER_SPECTURM,    SPECPLOT_COND_CLUSTER_SPECTURM    ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,    SPECPLOT_VAL_CLUSTER_PEPTIDE_ALL, SPECPLOT_COND_CLUSTER_PEPTIDE_ALL ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,     SPECPLOT_VAL_TARGET,              SPECPLOT_COND_TARGET              ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING,   SPECPLOT_VAL_ENCODING,            SPECPLOT_COND_ENCODING            ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_ZOOM,       SPECPLOT_VAL_CLUSTER_ZOOM,        SPECPLOT_COND_CLUSTER_ZOOM        ) );
  //auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_MODEL,      SPECPLOT_VAR_CLUSTER_MODEL,       SPECPLOT_COND_CLUSTER_MODEL       ) );
  //auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_MASS_SHIFT, SPECPLOT_VAR_CLUSTER_MASS_SHIFT,  SPECPLOT_COND_CLUSTER_MASS_SHIFT  ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_NOTITLE,    SPECPLOT_VAL_CLUSTER_NOTITLE,     SPECPLOT_COND_CLUSTER_NOTITLE     ) );

  this.colTypes.push(auxI);

  // colTypes[2] . (CTseqsBox)
  var auxB = new ReportColumnTypeBox();
  auxB.columnLabel  = REPORT_HEADER_CLUSTERS_3;

  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.columnLabel  = REPORT_SEQ_NAME_REFERENCE;
  auxI.label        = TAG_TABLE_CLUSTER_FIELD_REFERENCE;
  auxI.renderer     = SPECTRUM_RENDERER;
  auxI.validator    = TAG_TABLE_CLUSTER_FIELD_REFERENCE;
  auxI.splitLabel   = "true";
  auxI.id           = clustR;

  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TITLE,      SPECPLOT_VAL_CLUSTER_TITLE,       SPECPLOT_COND_CLUSTER_TITLE       ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,     SPECPLOT_VAL_CLUSTER_PKLBIN,      SPECPLOT_COND_CLUSTER_PKLBIN      ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM,   SPECPLOT_VAL_CLUSTER_SPECTURM,    SPECPLOT_COND_CLUSTER_SPECTURM    ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,    SPECPLOT_VAL_CLUSTER_PEPTIDE_REF, SPECPLOT_COND_CLUSTER_PEPTIDE_REF ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,     SPECPLOT_VAL_TARGET,              SPECPLOT_COND_TARGET              ) );
  //auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_MODEL,      SPECPLOT_VAR_CLUSTER_MODEL,       SPECPLOT_COND_CLUSTER_MODEL       ) );
  //auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_MASS_SHIFT, SPECPLOT_VAR_CLUSTER_MASS_SHIFT,  SPECPLOT_COND_CLUSTER_MASS_SHIFT  ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING,   SPECPLOT_VAL_ENCODING,            SPECPLOT_COND_ENCODING            ) );

  auxB.sequences.push(auxI);


  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.columnLabel  = REPORT_SEQ_NAME_HOMOLOG;
  auxI.label        = TAG_TABLE_CLUSTER_FIELD_HOMOLOG;
  auxI.renderer     = SPECTRUM_RENDERER;
  auxI.validator    = TAG_TABLE_CLUSTER_FIELD_HOMOLOG;
  auxI.splitLabel   = "true";
  auxI.id           = clustH;

  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TITLE,      SPECPLOT_VAL_CLUSTER_TITLE,       SPECPLOT_COND_CLUSTER_TITLE       ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,     SPECPLOT_VAL_CLUSTER_PKLBIN,      SPECPLOT_COND_CLUSTER_PKLBIN      ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM,   SPECPLOT_VAL_CLUSTER_SPECTURM,    SPECPLOT_COND_CLUSTER_SPECTURM    ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,    SPECPLOT_VAL_CLUSTER_PEPTIDE_HOM, SPECPLOT_COND_CLUSTER_PEPTIDE_HOM ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,     SPECPLOT_VAL_TARGET,              SPECPLOT_COND_TARGET              ) );
  //auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_MODEL,      SPECPLOT_VAR_CLUSTER_MODEL,       SPECPLOT_COND_CLUSTER_MODEL       ) );
  //auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_MASS_SHIFT, SPECPLOT_VAR_CLUSTER_MASS_SHIFT,  SPECPLOT_COND_CLUSTER_MASS_SHIFT  ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING,   SPECPLOT_VAL_ENCODING,            SPECPLOT_COND_ENCODING            ) );

  auxB.sequences.push(auxI);

  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.columnLabel  = REPORT_SEQ_NAME_DENOVO;
  auxI.label        = TAG_TABLE_CLUSTER_FIELD_DENOVO;
  auxI.renderer     = SPECTRUM_RENDERER;
  auxI.validator    = TAG_TABLE_CLUSTER_FIELD_DENOVO;
  auxI.splitLabel   = "true";
  auxI.id           = clustN;

  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TITLE,      SPECPLOT_VAL_CLUSTER_TITLE,         SPECPLOT_COND_CLUSTER_TITLE         ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,     SPECPLOT_VAL_CLUSTER_PKLBIN,        SPECPLOT_COND_CLUSTER_PKLBIN        ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM,   SPECPLOT_VAL_CLUSTER_SPECTURM,      SPECPLOT_COND_CLUSTER_SPECTURM      ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,    SPECPLOT_VAL_CLUSTER_PEPTIDE_NOVO,  SPECPLOT_COND_CLUSTER_PEPTIDE_NOVO  ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,     SPECPLOT_VAL_TARGET,                SPECPLOT_COND_TARGET                ) );
  //auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_MODEL,      SPECPLOT_VAR_CLUSTER_MODEL,         SPECPLOT_COND_CLUSTER_MODEL         ) );
  //auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_MASS_SHIFT, SPECPLOT_VAR_CLUSTER_MASS_SHIFT,    SPECPLOT_COND_CLUSTER_MASS_SHIFT    ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING,   SPECPLOT_VAL_ENCODING,              SPECPLOT_COND_ENCODING              ) );

  auxB.sequences.push(auxI);


  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.dynamic      = true;
  auxI.columnLabel  = REPORT_SEQ_NAME_USER;
  auxI.label        = TAG_TABLE_CLUSTER_FIELD_USER;
  auxI.renderer     = SPECTRUM_RENDERER;
  auxI.imgSequence  = TAG_TABLE_CLUSTER_FIELD_USER;
  auxI.splitLabel   = "true";
  auxI.id           = clustU;
  //auxI.validator    = TAG_TABLE_CLUSTER_FIELD_USER;

  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TITLE,      SPECPLOT_VAL_CLUSTER_TITLE,         SPECPLOT_COND_CLUSTER_TITLE           ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,     SPECPLOT_VAL_CLUSTER_PKLBIN,        SPECPLOT_COND_CLUSTER_PKLBIN          ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM,   SPECPLOT_VAL_CLUSTER_SPECTURM,      SPECPLOT_COND_CLUSTER_SPECTURM        ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,    SPECPLOT_VAL_CLUSTER_PEPTIDE_USER,  SPECPLOT_COND_CLUSTER_PEPTIDE_USER, 0 ) );
  //auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_MODEL,      SPECPLOT_VAR_CLUSTER_MODEL,         SPECPLOT_COND_CLUSTER_MODEL           ) );
  //auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_MASS_SHIFT, SPECPLOT_VAR_CLUSTER_MASS_SHIFT,    SPECPLOT_COND_CLUSTER_MASS_SHIFT      ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,     SPECPLOT_VAL_TARGET,                SPECPLOT_COND_TARGET                  ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING,   SPECPLOT_VAL_ENCODING,              SPECPLOT_COND_ENCODING                ) );

  auxB.sequences.push(auxI);

  var auxS = new ReportColumnTypeString();
  auxS.isInput      = true;
  auxS.dynamic      = true;
  auxS.id           = inputID;
  auxB.sequences.push(auxS);

  var auxS = new ReportColumnTypeString();
  auxS.isButton     = true;
  auxS.dynamic      = true;
  auxS.text         = REPORT_BUTTON_UPDATE;
  auxS.onClick      = this.buildUpdateCall(inputID, clustU, true);
  auxB.sequences.push(auxS);

  this.colTypes.push(auxB);


// colTypes[2] . (CTstring) mass
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_CLUSTERS_4;
  auxS.sortDataCol  = TABLE_CLUSTER_FIELD_MASS;
  auxS.text         = TAG_TABLE_CLUSTER_FIELD_MASS;
  this.colTypes.push(auxS);

// colTypes[3] . (CTstring) charge
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_CLUSTERS_5;
  auxS.sortDataCol  = TABLE_CLUSTER_FIELD_CHARGE;
  auxS.text         = TAG_TABLE_CLUSTER_FIELD_CHARGE;
  this.colTypes.push(auxS);

// colTypes[4] . (CTstring) B%
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_CLUSTERS_6;
  auxS.sortDataCol  = TABLE_CLUSTER_FIELD_B_PER;
  auxS.text         = TAG_TABLE_CLUSTER_FIELD_B_PER;
  this.colTypes.push(auxS);

// colTypes[5] . (CTstring) Y%
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_CLUSTERS_7;
  auxS.sortDataCol  = TABLE_CLUSTER_FIELD_Y_PER;
  auxS.text         = TAG_TABLE_CLUSTER_FIELD_Y_PER;
  this.colTypes.push(auxS);

// colTypes[6] . (CTstring) BY intensity %
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_CLUSTERS_8;
  auxS.sortDataCol  = TABLE_CLUSTER_FIELD_BY_INT;
  auxS.text         = TAG_TABLE_CLUSTER_FIELD_BY_INT;
  this.colTypes.push(auxS);

// colTypes[6] . (CTstring) BY intensity %
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_CLUSTERS_9;
  auxS.sortDataCol  = TABLE_CLUSTER_FIELD_MODEL_NAME;
  auxS.text         = TAG_TABLE_CLUSTER_FIELD_MODEL_NAME;
  this.colTypes.push(auxS);
}
////////////////////////////////////////////////////////////////////////////////
tableCluster.prototype.defineView2 = function()
{
  // clear view
  this.clearView();

  var clust   = "l" + TAG_TABLE_CLUSTER_FIELD_ID;
  var inputID = "input_cluster_" + TAG_INTERNAL_ROW + "_" + TAG_INTERNAL_COL;

  var auxB = new ReportColumnTypeBox();
  auxB.columnLabel  = "Sequences";

  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.columnLabel     = "";
  auxI.label           = "";
  auxI.iconRenderer    = SPECTRUM_RENDERER;
  auxI.id              = clust;

  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_TITLE,      SPECPLOT_VAL_CLUSTER_TITLE,       SPECPLOT_COND_CLUSTER_TITLE           ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,     SPECPLOT_VAL_CLUSTER_PKLBIN,      SPECPLOT_COND_CLUSTER_PKLBIN          ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM,   SPECPLOT_VAL_CLUSTER_SPECTURM,    SPECPLOT_COND_CLUSTER_SPECTURM        ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,     SPECPLOT_VAL_TARGET,              SPECPLOT_COND_TARGET                  ) );
  //auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_MODEL,      SPECPLOT_VAR_CLUSTER_MODEL,       SPECPLOT_COND_CLUSTER_MODEL           ) );
  //auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_MASS_SHIFT, SPECPLOT_VAR_CLUSTER_MASS_SHIFT,  SPECPLOT_COND_CLUSTER_MASS_SHIFT      ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING,   SPECPLOT_VAL_ENCODING,            SPECPLOT_COND_ENCODING                ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,    SPECPLOT_VAL_CLUSTER_PEPTIDE_ALL, SPECPLOT_COND_CLUSTER_PEPTIDE_ALL,  0 ) );

  auxB.sequences.push(auxI);


  var auxS = new ReportColumnTypeString();
  auxS.isInput      = true;
  auxS.dynamic      = true;
  auxS.id           = inputID;
  auxB.sequences.push(auxS);

  var auxS = new ReportColumnTypeString();
  auxS.isButton     = true;
  auxS.dynamic      = true;
  auxS.text         = REPORT_BUTTON_UPDATE;
  auxS.onClick      = this.buildUpdateCall(inputID, clust, false);
  auxB.sequences.push(auxS);

  this.colTypes.push(auxB);
}
////////////////////////////////////////////////////////////////////////////////
// Table Input Spectra
////////////////////////////////////////////////////////////////////////////////
function tableInputSpectra()
{
  this.tableType = TABLE_SPECTRA_ID;
}
////////////////////////////////////////////////////////////////////////////////
tableInputSpectra.prototype = new table();

////////////////////////////////////////////////////////////////////////////////
tableInputSpectra.prototype.getId = function()
{
  var aux = [];
  if(this.theArray.length) {
    //aux.push(this.theArray[0][2]);
    //aux.push(this.theArray[0][1]);
    //aux.push(this.theArray[0][0]);
  }
  return aux;
}
////////////////////////////////////////////////////////////////////////////////
tableInputSpectra.prototype.getSingleId = function(row)
{
  if(row < this.theArray.length)
    return this.theArray[row][2];
  return -1;
}
////////////////////////////////////////////////////////////////////////////////
tableInputSpectra.prototype.buildUpdateCall = function(inputID, suffix)
{
  var aux = "javascript:TablesAll.updateSpectra(\"" + inputID + "\", \"" + suffix + "\", \"" + IMAGE_LARGE_ID_PREFIX + suffix + "\", \"" + IMAGE_LARGE_CTRL_ID_PREFIX + suffix + "\", \"href\", " + TAG_TABLE_SPECTRA_FIELD_ID + ", " + TABLE_SPECTRA_FIELD_SEQ_USER + ", false);";
  aux += "triggerClick(\"" + IMAGE_LARGE_ID_PREFIX + suffix + "\");";
  return aux;
}
////////////////////////////////////////////////////////////////////////////////
tableInputSpectra.prototype.defineView = function()
{
  // clear view
  this.clearView();

  var specs   = "ss" + TAG_TABLE_SPECTRA_FIELD_ID;
  var specR   = "sR" + TAG_TABLE_SPECTRA_FIELD_ID;
  var specH   = "sH" + TAG_TABLE_SPECTRA_FIELD_ID;
  var specN   = "sN" + TAG_TABLE_SPECTRA_FIELD_ID
  var specU   = "sU" + TAG_TABLE_SPECTRA_FIELD_ID;
  var inputID = "input_spectra_" + TAG_INTERNAL_ROW + "_" + TAG_INTERNAL_COL;

  // colTypes[0] . (CTstring) Spectrum index
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel   = REPORT_HEADER_SPECTRA_0;
  auxS.sortDataCol   = TABLE_SPECTRA_FIELD_IDX;
  auxS.text          = TAG_TABLE_SPECTRA_FIELD_IDX;
  this.colTypes.push(auxS);

  var auxS = new ReportColumnTypeString();
  auxS.columnLabel   = REPORT_HEADER_SPECTRA_1;
  auxS.sortDataCol   = TABLE_SPECTRA_FIELD_SCAN;
  auxS.text          = TAG_TABLE_SPECTRA_FIELD_SCAN;
  this.colTypes.push(auxS);

  var auxS = new ReportColumnTypeString();
  auxS.columnLabel   = REPORT_HEADER_SPECTRA_2;
  auxS.sortDataCol   = TABLE_SPECTRA_FIELD_TOOL;
  auxS.text          = TAG_TABLE_SPECTRA_FIELD_TOOL;
  this.colTypes.push(auxS);

  // colTypes[1] . (CTseqsBox)
  var auxB = new ReportColumnTypeBox();
  auxB.columnLabel   = REPORT_HEADER_SPECTRA_3;
  //auxB.link          = "javascript:TablesAll.loadClusterPage(" + TAG_TABLE_SPECTRA_FIELD_CLUSTER + ");";

  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.iconRenderer  = SPECTRUM_RENDERER;
  auxI.validator     = TAG_SPECTRA_PEPTIDE_ALL;
  auxI.id            = specs;

  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,   SPECPLOT_VAL_SPECTRA_PKLBIN,      SPECPLOT_COND_SPECTRA_PKLBIN      ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM, SPECPLOT_VAL_SPECTRA_SPECTURM,    SPECPLOT_COND_SPECTRA_SPECTURM    ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,  SPECPLOT_VAL_SPECTRA_PEPTIDE_ALL, SPECPLOT_COND_SPECTRA_PEPTIDE_ALL ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,   SPECPLOT_VAL_TARGET,              SPECPLOT_COND_TARGET              ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING, SPECPLOT_VAL_ENCODING,            SPECPLOT_COND_ENCODING            ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_ZOOM,     SPECPLOT_VAL_SPECTRA_ZOOM,        SPECPLOT_COND_SPECTRA_ZOOM        ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_NOTITLE,  SPECPLOT_VAL_SPECTRA_NOTITLE,     SPECPLOT_COND_SPECTRA_NOTITLE     ) );

  auxB.sequences.push(auxI);


  var auxS = new ReportColumnTypeString();
  auxS.text          = TAG_TABLE_SPECTRA_FIELD_INPUT_FILENAME;
  auxS.splitText     = true;
  auxB.sequences.push(auxS);

  this.colTypes.push(auxB);


  // colTypes[2] . (CTseqsBox)
  var auxB = new ReportColumnTypeBox();
  auxB.columnLabel   = REPORT_HEADER_SPECTRA_4;

  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.columnLabel  = REPORT_SEQ_NAME_REFERENCE;
  auxI.label        = TAG_TABLE_SPECTRA_FIELD_SEQ_REFERENCE;
  auxI.renderer     = SPECTRUM_RENDERER;
  auxI.validator    = TAG_TABLE_SPECTRA_FIELD_SEQ_REFERENCE;
  auxI.splitLabel   = "true";
  auxI.id           = specR;

  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,   SPECPLOT_VAL_SPECTRA_PKLBIN,      SPECPLOT_COND_SPECTRA_PKLBIN      ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM, SPECPLOT_VAL_SPECTRA_SPECTURM,    SPECPLOT_COND_SPECTRA_SPECTURM    ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,  SPECPLOT_VAL_SPECTRA_PEPTIDE_REF, SPECPLOT_COND_SPECTRA_PEPTIDE_REF ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,   SPECPLOT_VAL_TARGET,              SPECPLOT_COND_TARGET              ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING, SPECPLOT_VAL_ENCODING,            SPECPLOT_COND_ENCODING            ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TITLE,    SPECPLOT_VAL_SPECTRA_TITLE,       SPECPLOT_COND_SPECTRA_TITLE       ) );

  auxB.sequences.push(auxI);


  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.columnLabel  = REPORT_SEQ_NAME_HOMOLOG;
  auxI.label        = TAG_TABLE_SPECTRA_FIELD_SEQ_HOMOLOG;
  auxI.renderer     = SPECTRUM_RENDERER;
  auxI.validator    = TAG_TABLE_SPECTRA_FIELD_SEQ_HOMOLOG;
  auxI.splitLabel   = "true";
  auxI.id           = specH;

  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,   SPECPLOT_VAL_SPECTRA_PKLBIN,      SPECPLOT_COND_SPECTRA_PKLBIN      ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM, SPECPLOT_VAL_SPECTRA_SPECTURM,    SPECPLOT_COND_SPECTRA_SPECTURM    ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,  SPECPLOT_VAL_SPECTRA_PEPTIDE_HOM, SPECPLOT_COND_SPECTRA_PEPTIDE_HOM ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,   SPECPLOT_VAL_TARGET,              SPECPLOT_COND_TARGET              ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING, SPECPLOT_VAL_ENCODING,            SPECPLOT_COND_ENCODING            ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TITLE,    SPECPLOT_VAL_SPECTRA_TITLE,       SPECPLOT_COND_SPECTRA_TITLE       ) );

  auxB.sequences.push(auxI);


  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.columnLabel  = REPORT_SEQ_NAME_DENOVO;
  auxI.label        = TAG_TABLE_SPECTRA_FIELD_SEQ_DENOVO;
  auxI.renderer     = SPECTRUM_RENDERER;
  auxI.validator    = TAG_TABLE_SPECTRA_FIELD_SEQ_DENOVO;
  auxI.splitLabel   = "true";
  auxI.id           = specN;

  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,   SPECPLOT_VAL_SPECTRA_PKLBIN,        SPECPLOT_COND_SPECTRA_PKLBIN        ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM, SPECPLOT_VAL_SPECTRA_SPECTURM,      SPECPLOT_COND_SPECTRA_SPECTURM      ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,  SPECPLOT_VAL_SPECTRA_PEPTIDE_NOVO,  SPECPLOT_COND_SPECTRA_PEPTIDE_NOVO  ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,   SPECPLOT_VAL_TARGET,                SPECPLOT_COND_TARGET                ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING, SPECPLOT_VAL_ENCODING,              SPECPLOT_COND_ENCODING              ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TITLE,    SPECPLOT_VAL_SPECTRA_TITLE,         SPECPLOT_COND_SPECTRA_TITLE         ) );

  auxB.sequences.push(auxI);


  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.dynamic      = true;
  auxI.columnLabel  = REPORT_SEQ_NAME_USER;
  auxI.label        = TAG_TABLE_SPECTRA_FIELD_SEQ_USER;
  auxI.renderer     = SPECTRUM_RENDERER;
  auxI.imgSequence  = TAG_TABLE_SPECTRA_FIELD_SEQ_USER;
  auxI.splitLabel   = "true";
  auxI.id           = specU;
  //auxI.validator    = TAG_TABLE_SPECTRA_FIELD_SEQ_USER;

  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,   SPECPLOT_VAL_SPECTRA_PKLBIN,        SPECPLOT_COND_SPECTRA_PKLBIN          ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM, SPECPLOT_VAL_SPECTRA_SPECTURM,      SPECPLOT_COND_SPECTRA_SPECTURM        ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,  SPECPLOT_VAL_SPECTRA_PEPTIDE_USER,  SPECPLOT_COND_SPECTRA_PEPTIDE_USER, 0 ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,   SPECPLOT_VAL_TARGET,                SPECPLOT_COND_TARGET                  ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING, SPECPLOT_VAL_ENCODING,              SPECPLOT_COND_ENCODING                ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TITLE,    SPECPLOT_VAL_SPECTRA_TITLE,         SPECPLOT_COND_SPECTRA_TITLE           ) );

  auxB.sequences.push(auxI);


  var auxS = new ReportColumnTypeString();
  auxS.dynamic      = true;
  auxS.isInput      = true;
  auxS.id           = inputID;
  auxB.sequences.push(auxS);

  var auxS = new ReportColumnTypeString();
  auxS.dynamic      = true;
  auxS.isButton     = true;
  auxS.text         = REPORT_BUTTON_UPDATE;
  auxS.onClick      = this.buildUpdateCall(inputID, specU);
  auxB.sequences.push(auxS);

  this.colTypes.push(auxB);


  // colTypes[3] . (CTstring) mass
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_5;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_PROTEIN_NAME;
  auxS.onClick      = "javascript:TablesAll.loadPage(" + PAGE_PROTEIN + "," + TAG_TABLE_SPECTRA_FIELD_PROTEIN_INDEX + ");";
  auxS.link         = '#';
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_PROTEIN_NAME;
  this.colTypes.push(auxS);

  // colTypes[3] . (CTstring) mass
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_6;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_CONTIG_INDEX;
  auxS.onClick      = "javascript:TablesAll.loadPage(" + PAGE_CONTIG + "," + TAG_TABLE_SPECTRA_FIELD_CONTIG_INDEX + ");";
  auxS.link         = '#';
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_CONTIG_INDEX;
  this.colTypes.push(auxS);

  // colTypes[3] . (CTstring) mass
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_7;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_MASS;
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_MASS;
  this.colTypes.push(auxS);

  // colTypes[4] . (CTstring) charge
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_8;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_CHARGE;
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_CHARGE;
  this.colTypes.push(auxS);

  // colTypes[5] . (CTstring) B%
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_9;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_B_PER;
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_B_PER;
  this.colTypes.push(auxS);

  // colTypes[6] . (CTstring) Y%
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_10;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_Y_PER;
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_Y_PER;
  this.colTypes.push(auxS);

  // colTypes[7] . (CTstring) BY intensity %
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_11;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_BY_INTENSITY;
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_BY_INTENSITY;
  this.colTypes.push(auxS);

  // colTypes[8] . Model
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_12;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_MODEL;
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_MODEL;
  this.colTypes.push(auxS);
}
////////////////////////////////////////////////////////////////////////////////
tableInputSpectra.prototype.defineView2 = function()
{
  // clear view
  this.clearView();

  var specs   = "ss" + TAG_TABLE_SPECTRA_FIELD_ID;
  var specR   = "sR" + TAG_TABLE_SPECTRA_FIELD_ID;
  var specH   = "sH" + TAG_TABLE_SPECTRA_FIELD_ID;
  var specN   = "sN" + TAG_TABLE_SPECTRA_FIELD_ID
  var specU   = "sU" + TAG_TABLE_SPECTRA_FIELD_ID;
  var inputID = "input_spectra_" + TAG_INTERNAL_ROW + "_" + TAG_INTERNAL_COL;

  // colTypes[0] . (CTstring) Spectrum index
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel   = REPORT_HEADER_SPECTRA_0;
  auxS.sortDataCol   = TABLE_SPECTRA_FIELD_IDX;
  auxS.text          = TAG_TABLE_SPECTRA_FIELD_IDX;
  this.colTypes.push(auxS);

  // colTypes[0] . (CTstring) Spectrum index
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel   = REPORT_HEADER_SPECTRA_1;
  auxS.sortDataCol   = TABLE_SPECTRA_FIELD_SCAN;
  auxS.text          = TAG_TABLE_SPECTRA_FIELD_SCAN;
  this.colTypes.push(auxS);

  var auxS = new ReportColumnTypeString();
  auxS.columnLabel   = REPORT_HEADER_SPECTRA_2;
  auxS.sortDataCol   = TABLE_SPECTRA_FIELD_TOOL;
  auxS.text          = TAG_TABLE_SPECTRA_FIELD_TOOL;
  this.colTypes.push(auxS);

  // colTypes[1] . (CTseqsBox)
  var auxB = new ReportColumnTypeBox();
  auxB.columnLabel   = REPORT_HEADER_SPECTRA_3;
  //auxB.link          = "javascript:TablesAll.loadClusterPage(" + TAG_TABLE_SPECTRA_FIELD_CLUSTER + ")";

  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.iconRenderer  = SPECTRUM_RENDERER;
  auxI.validator     = TAG_SPECTRA_PEPTIDE_ALL;
  auxI.id            = specs;

  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,   SPECPLOT_VAL_SPECTRA_PKLBIN,       SPECPLOT_COND_SPECTRA_PKLBIN       ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM, SPECPLOT_VAL_SPECTRA_SPECTURM,     SPECPLOT_COND_SPECTRA_SPECTURM     ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,  SPECPLOT_VAL_SPECTRA_PEPTIDE_ALL,  SPECPLOT_COND_SPECTRA_PEPTIDE_ALL  ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,   SPECPLOT_VAL_TARGET,               SPECPLOT_COND_TARGET               ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING, SPECPLOT_VAL_ENCODING,             SPECPLOT_COND_ENCODING             ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_ZOOM,     SPECPLOT_VAL_SPECTRA_ZOOM,         SPECPLOT_COND_SPECTRA_ZOOM         ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_NOTITLE,  SPECPLOT_VAL_SPECTRA_NOTITLE,      SPECPLOT_COND_SPECTRA_NOTITLE      ) );

  auxB.sequences.push(auxI);


  var auxS = new ReportColumnTypeString();
  auxS.text          = TAG_TABLE_SPECTRA_FIELD_INPUT_FILENAME;
  auxS.splitText     = true;
  auxB.sequences.push(auxS);

  this.colTypes.push(auxB);


  // colTypes[2] . (CTseqsBox)
  var auxB = new ReportColumnTypeBox();
  auxB.columnLabel   = REPORT_HEADER_SPECTRA_4;

  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.columnLabel  = REPORT_SEQ_NAME_REFERENCE;
  auxI.label        = TAG_TABLE_SPECTRA_FIELD_SEQ_REFERENCE;
  auxI.renderer     = SPECTRUM_RENDERER;
  auxI.validator    = TAG_TABLE_SPECTRA_FIELD_SEQ_REFERENCE;
  auxI.splitLabel   = "true";
  auxI.id           = specR;

  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,   SPECPLOT_VAL_SPECTRA_PKLBIN,      SPECPLOT_COND_SPECTRA_PKLBIN      ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM, SPECPLOT_VAL_SPECTRA_SPECTURM,    SPECPLOT_COND_SPECTRA_SPECTURM    ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,  SPECPLOT_VAL_SPECTRA_PEPTIDE_REF, SPECPLOT_COND_SPECTRA_PEPTIDE_REF ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,   SPECPLOT_VAL_TARGET,              SPECPLOT_COND_TARGET              ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING, SPECPLOT_VAL_ENCODING,            SPECPLOT_COND_ENCODING            ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TITLE,    SPECPLOT_VAL_SPECTRA_TITLE,       SPECPLOT_COND_SPECTRA_TITLE       ) );

  auxB.sequences.push(auxI);


  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.columnLabel  = REPORT_SEQ_NAME_HOMOLOG;
  auxI.label        = TAG_TABLE_SPECTRA_FIELD_SEQ_HOMOLOG;
  auxI.renderer     = SPECTRUM_RENDERER;
  auxI.validator    = TAG_TABLE_SPECTRA_FIELD_SEQ_HOMOLOG;
  auxI.splitLabel   = "true";
  auxI.id           = specH;

  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,   SPECPLOT_VAL_SPECTRA_PKLBIN,      SPECPLOT_COND_SPECTRA_PKLBIN      ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM, SPECPLOT_VAL_SPECTRA_SPECTURM,    SPECPLOT_COND_SPECTRA_SPECTURM    ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,  SPECPLOT_VAL_SPECTRA_PEPTIDE_HOM, SPECPLOT_COND_SPECTRA_PEPTIDE_HOM ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,   SPECPLOT_VAL_TARGET,              SPECPLOT_COND_TARGET              ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING, SPECPLOT_VAL_ENCODING,            SPECPLOT_COND_ENCODING            ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TITLE,    SPECPLOT_VAL_SPECTRA_TITLE,       SPECPLOT_COND_SPECTRA_TITLE       ) );

  auxB.sequences.push(auxI);


  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.columnLabel  = REPORT_SEQ_NAME_DENOVO;
  auxI.label        = TAG_TABLE_SPECTRA_FIELD_SEQ_DENOVO;
  auxI.renderer     = SPECTRUM_RENDERER;
  auxI.validator    = TAG_TABLE_SPECTRA_FIELD_SEQ_DENOVO;
  auxI.splitLabel   = "true";
  auxI.id           = specN;

  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,   SPECPLOT_VAL_SPECTRA_PKLBIN,        SPECPLOT_COND_SPECTRA_PKLBIN        ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM, SPECPLOT_VAL_SPECTRA_SPECTURM,      SPECPLOT_COND_SPECTRA_SPECTURM      ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,  SPECPLOT_VAL_SPECTRA_PEPTIDE_NOVO,  SPECPLOT_COND_SPECTRA_PEPTIDE_NOVO  ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,   SPECPLOT_VAL_TARGET,                SPECPLOT_COND_TARGET                ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING, SPECPLOT_VAL_ENCODING,              SPECPLOT_COND_ENCODING              ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TITLE,    SPECPLOT_VAL_SPECTRA_TITLE,         SPECPLOT_COND_SPECTRA_TITLE         ) );

  auxB.sequences.push(auxI);


  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.dynamic      = true;
  auxI.columnLabel  = REPORT_SEQ_NAME_USER;
  auxI.label        = TAG_TABLE_SPECTRA_FIELD_SEQ_USER;
  auxI.renderer     = SPECTRUM_RENDERER;
  auxI.imgSequence  = TAG_TABLE_SPECTRA_FIELD_SEQ_USER;
  auxI.splitLabel   = "true";
  auxI.id           = specU;
  //auxI.validator    = TAG_TABLE_SPECTRA_FIELD_SEQ_USER;

  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,   SPECPLOT_VAL_SPECTRA_PKLBIN,        SPECPLOT_COND_SPECTRA_PKLBIN          ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM, SPECPLOT_VAL_SPECTRA_SPECTURM,      SPECPLOT_COND_SPECTRA_SPECTURM        ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,  SPECPLOT_VAL_SPECTRA_PEPTIDE_USER,  SPECPLOT_COND_SPECTRA_PEPTIDE_USER, 0 ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,   SPECPLOT_VAL_TARGET,                SPECPLOT_COND_TARGET                  ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING, SPECPLOT_VAL_ENCODING,              SPECPLOT_COND_ENCODING                ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TITLE,    SPECPLOT_VAL_SPECTRA_TITLE,         SPECPLOT_COND_SPECTRA_TITLE           ) );

  auxB.sequences.push(auxI);


  var auxS = new ReportColumnTypeString();
  auxS.dynamic      = true;
  auxS.isInput      = true;
  auxS.id           = inputID;
  auxB.sequences.push(auxS);

  var auxS = new ReportColumnTypeString();
  auxS.dynamic      = true;
  auxS.isButton     = true;
  auxS.text         = REPORT_BUTTON_UPDATE;
  auxS.onClick      = this.buildUpdateCall(inputID, specU);
  auxB.sequences.push(auxS);

  this.colTypes.push(auxB);


  // colTypes[3] . (CTstring) mass
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_5;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_PROTEIN_NAME;
  auxS.onClick      = "javascript:TablesAll.loadPage(" + PAGE_PROTEIN + "," + TAG_TABLE_SPECTRA_FIELD_PROTEIN_INDEX + ");";
  auxS.link         = '#';
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_PROTEIN_NAME;
  this.colTypes.push(auxS);

  // colTypes[3] . (CTstring) mass
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_6;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_CONTIG_INDEX;
  auxS.onClick      = "javascript:TablesAll.loadPage(" + PAGE_CONTIG + "," + TAG_TABLE_SPECTRA_FIELD_CONTIG_INDEX + ");";
  auxS.link         = '#';
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_CONTIG_INDEX;
  this.colTypes.push(auxS);

  // colTypes[3] . (CTstring) mass
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_7;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_MASS;
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_MASS;
  this.colTypes.push(auxS);

  // colTypes[4] . (CTstring) charge
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_8;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_CHARGE;
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_CHARGE;
  this.colTypes.push(auxS);

  // colTypes[5] . (CTstring) B%
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_9;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_B_PER;
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_B_PER;
  this.colTypes.push(auxS);

  // colTypes[6] . (CTstring) Y%
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_10;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_Y_PER;
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_Y_PER;
  this.colTypes.push(auxS);

  // colTypes[7] . (CTstring) BY intensity %
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_11;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_BY_INTENSITY;
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_BY_INTENSITY;
  this.colTypes.push(auxS);

  // colTypes[8] . Model
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_12;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_MODEL;
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_MODEL;
  this.colTypes.push(auxS);
}
////////////////////////////////////////////////////////////////////////////////
tableInputSpectra.prototype.defineViewNoClusters = function()
{
  // clear view
  this.clearView();

  var specs   = "ss" + TAG_TABLE_SPECTRA_FIELD_ID;
  var specR   = "sR" + TAG_TABLE_SPECTRA_FIELD_ID;
  var specH   = "sH" + TAG_TABLE_SPECTRA_FIELD_ID;
  var specN   = "sN" + TAG_TABLE_SPECTRA_FIELD_ID
  var specU   = "sU" + TAG_TABLE_SPECTRA_FIELD_ID;
  var inputID = "input_spectra_" + TAG_INTERNAL_ROW + "_" + TAG_INTERNAL_COL;

  // colTypes[0] . (CTstring) Spectrum index
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel   = REPORT_HEADER_SPECTRA_0;
  auxS.sortDataCol   = TABLE_SPECTRA_FIELD_IDX;
  auxS.text          = TAG_TABLE_SPECTRA_FIELD_IDX;
  this.colTypes.push(auxS);

  // colTypes[0] . (CTstring) Spectrum index
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel   = REPORT_HEADER_SPECTRA_1;
  auxS.sortDataCol   = TABLE_SPECTRA_FIELD_SCAN;
  auxS.text          = TAG_TABLE_SPECTRA_FIELD_SCAN;
  this.colTypes.push(auxS);

  var auxS = new ReportColumnTypeString();
  auxS.columnLabel   = REPORT_HEADER_SPECTRA_2;
  auxS.sortDataCol   = TABLE_SPECTRA_FIELD_TOOL;
  auxS.text          = TAG_TABLE_SPECTRA_FIELD_TOOL;
  this.colTypes.push(auxS);

  // colTypes[1] . (CTseqsBox)
  var auxB = new ReportColumnTypeBox();
  auxB.columnLabel   = REPORT_HEADER_SPECTRA_3;
  //auxB.link          = "javascript:TablesAll.loadClusterPage(" + TAG_TABLE_SPECTRA_FIELD_CLUSTER + ")";

  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.iconRenderer  = SPECTRUM_RENDERER;
  auxI.validator     = TAG_SPECTRA_PEPTIDE_ALL;
  auxI.id            = specs;

  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,   SPECPLOT_VAL_SPECTRA_PKLBIN,       SPECPLOT_COND_SPECTRA_PKLBIN       ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM, SPECPLOT_VAL_SPECTRA_SPECTURM,     SPECPLOT_COND_SPECTRA_SPECTURM     ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,  SPECPLOT_VAL_SPECTRA_PEPTIDE_ALL,  SPECPLOT_COND_SPECTRA_PEPTIDE_ALL  ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,   SPECPLOT_VAL_TARGET,               SPECPLOT_COND_TARGET               ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING, SPECPLOT_VAL_ENCODING,             SPECPLOT_COND_ENCODING             ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_ZOOM,     SPECPLOT_VAL_SPECTRA_ZOOM,         SPECPLOT_COND_SPECTRA_ZOOM         ) );
  auxI.iconParams.push( new ReportParamsOption(SPECPLOT_PAR_NOTITLE,  SPECPLOT_VAL_SPECTRA_NOTITLE,      SPECPLOT_COND_SPECTRA_NOTITLE      ) );

  auxB.sequences.push(auxI);


  var auxS = new ReportColumnTypeString();
  auxS.text          = TAG_TABLE_SPECTRA_FIELD_INPUT_FILENAME;
  auxS.splitText     = true;
  auxB.sequences.push(auxS);

  this.colTypes.push(auxB);


  // colTypes[2] . (CTseqsBox)
  var auxB = new ReportColumnTypeBox();
  auxB.columnLabel   = REPORT_HEADER_SPECTRA_4;

  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.columnLabel  = REPORT_SEQ_NAME_REFERENCE;
  auxI.label        = TAG_TABLE_SPECTRA_FIELD_SEQ_REFERENCE;
  auxI.renderer     = SPECTRUM_RENDERER;
  auxI.validator    = TAG_TABLE_SPECTRA_FIELD_SEQ_REFERENCE;
  auxI.splitLabel   = "true";
  auxI.id           = specR;

  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,   SPECPLOT_VAL_SPECTRA_PKLBIN,      SPECPLOT_COND_SPECTRA_PKLBIN      ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM, SPECPLOT_VAL_SPECTRA_SPECTURM,    SPECPLOT_COND_SPECTRA_SPECTURM    ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,  SPECPLOT_VAL_SPECTRA_PEPTIDE_REF, SPECPLOT_COND_SPECTRA_PEPTIDE_REF ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,   SPECPLOT_VAL_TARGET,              SPECPLOT_COND_TARGET              ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING, SPECPLOT_VAL_ENCODING,            SPECPLOT_COND_ENCODING            ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TITLE,    SPECPLOT_VAL_SPECTRA_TITLE,       SPECPLOT_COND_SPECTRA_TITLE       ) );

  auxB.sequences.push(auxI);


  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.columnLabel  = REPORT_SEQ_NAME_HOMOLOG;
  auxI.label        = TAG_TABLE_SPECTRA_FIELD_SEQ_HOMOLOG;
  auxI.renderer     = SPECTRUM_RENDERER;
  auxI.validator    = TAG_TABLE_SPECTRA_FIELD_SEQ_HOMOLOG;
  auxI.splitLabel   = "true";
  auxI.id           = specH;

  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,   SPECPLOT_VAL_SPECTRA_PKLBIN,      SPECPLOT_COND_SPECTRA_PKLBIN      ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM, SPECPLOT_VAL_SPECTRA_SPECTURM,    SPECPLOT_COND_SPECTRA_SPECTURM    ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,  SPECPLOT_VAL_SPECTRA_PEPTIDE_HOM, SPECPLOT_COND_SPECTRA_PEPTIDE_HOM ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,   SPECPLOT_VAL_TARGET,              SPECPLOT_COND_TARGET              ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING, SPECPLOT_VAL_ENCODING,            SPECPLOT_COND_ENCODING            ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TITLE,    SPECPLOT_VAL_SPECTRA_TITLE,       SPECPLOT_COND_SPECTRA_TITLE       ) );

  auxB.sequences.push(auxI);


  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.columnLabel  = REPORT_SEQ_NAME_DENOVO;
  auxI.label        = TAG_TABLE_SPECTRA_FIELD_SEQ_DENOVO;
  auxI.renderer     = SPECTRUM_RENDERER;
  auxI.validator    = TAG_TABLE_SPECTRA_FIELD_SEQ_DENOVO;
  auxI.splitLabel   = "true";
  auxI.id           = specN;

  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,   SPECPLOT_VAL_SPECTRA_PKLBIN,        SPECPLOT_COND_SPECTRA_PKLBIN        ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM, SPECPLOT_VAL_SPECTRA_SPECTURM,      SPECPLOT_COND_SPECTRA_SPECTURM      ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,  SPECPLOT_VAL_SPECTRA_PEPTIDE_NOVO,  SPECPLOT_COND_SPECTRA_PEPTIDE_NOVO  ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,   SPECPLOT_VAL_TARGET,                SPECPLOT_COND_TARGET                ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING, SPECPLOT_VAL_ENCODING,              SPECPLOT_COND_ENCODING              ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TITLE,    SPECPLOT_VAL_SPECTRA_TITLE,         SPECPLOT_COND_SPECTRA_TITLE         ) );

  auxB.sequences.push(auxI);


  var auxI = new ReportColumnTypeImageOnDemand();
  auxI.dynamic      = true;
  auxI.columnLabel  = REPORT_SEQ_NAME_USER;
  auxI.label        = TAG_TABLE_SPECTRA_FIELD_SEQ_USER;
  auxI.renderer     = SPECTRUM_RENDERER;
  auxI.imgSequence  = TAG_TABLE_SPECTRA_FIELD_SEQ_USER;
  auxI.splitLabel   = "true";
  auxI.id           = specU;
  //auxI.validator    = TAG_TABLE_SPECTRA_FIELD_SEQ_USER;

  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PKLBIN,   SPECPLOT_VAL_SPECTRA_PKLBIN,        SPECPLOT_COND_SPECTRA_PKLBIN          ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_SPECTURM, SPECPLOT_VAL_SPECTRA_SPECTURM,      SPECPLOT_COND_SPECTRA_SPECTURM        ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_PEPTIDE,  SPECPLOT_VAL_SPECTRA_PEPTIDE_USER,  SPECPLOT_COND_SPECTRA_PEPTIDE_USER, 0 ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TARGET,   SPECPLOT_VAL_TARGET,                SPECPLOT_COND_TARGET                  ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_ENCODING, SPECPLOT_VAL_ENCODING,              SPECPLOT_COND_ENCODING                ) );
  auxI.params.push( new ReportParamsOption(SPECPLOT_PAR_TITLE,    SPECPLOT_VAL_SPECTRA_TITLE,         SPECPLOT_COND_SPECTRA_TITLE           ) );

  auxB.sequences.push(auxI);


  var auxS = new ReportColumnTypeString();
  auxS.dynamic      = true;
  auxS.isInput      = true;
  auxS.id           = inputID;
  auxB.sequences.push(auxS);

  var auxS = new ReportColumnTypeString();
  auxS.dynamic      = true;
  auxS.isButton     = true;
  auxS.text         = REPORT_BUTTON_UPDATE;
  auxS.onClick      = this.buildUpdateCall(inputID, specU);
  auxB.sequences.push(auxS);

  this.colTypes.push(auxB);


  // colTypes[3] . (CTstring) mass
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_5;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_PROTEIN_NAME;
  auxS.onClick      = "javascript:TablesAll.loadPage(" + PAGE_PROTEIN + "," + TAG_TABLE_SPECTRA_FIELD_PROTEIN_INDEX + ");";
  auxS.link         = '#';
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_PROTEIN_NAME;
  this.colTypes.push(auxS);

  // colTypes[3] . (CTstring) mass
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_6;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_CONTIG_INDEX;
  auxS.onClick      = "javascript:TablesAll.loadPage(" + PAGE_CONTIG + "," + TAG_TABLE_SPECTRA_FIELD_CONTIG_INDEX + ");";
  auxS.link         = '#';
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_CONTIG_INDEX;
  this.colTypes.push(auxS);

  // colTypes[3] . (CTstring) mass
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_7;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_MASS;
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_MASS;
  this.colTypes.push(auxS);

  // colTypes[4] . (CTstring) charge
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_8;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_CHARG;
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_CHARGE;
  this.colTypes.push(auxS);

  // colTypes[5] . (CTstring) B%
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_9;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_B_PER;
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_B_PER;
  this.colTypes.push(auxS);

  // colTypes[6] . (CTstring) Y%
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_10;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_Y_PER;
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_Y_PER;
  this.colTypes.push(auxS);

  // colTypes[7] . (CTstring) BY intensity %
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_11;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_BY_INTENSITY;
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_BY_INTENSITY;
  this.colTypes.push(auxS);

  // colTypes[8] . Model
  var auxS = new ReportColumnTypeString();
  auxS.columnLabel  = REPORT_HEADER_SPECTRA_12;
  auxS.sortDataCol  = TABLE_SPECTRA_FIELD_MODEL;
  auxS.text         = TAG_TABLE_SPECTRA_FIELD_MODEL;
  this.colTypes.push(auxS);
}
////////////////////////////////////////////////////////////////////////////////
// Report base class
////////////////////////////////////////////////////////////////////////////////
function Report()
{
  // the table vector
  this.tables = new Array();
}
////////////////////////////////////////////////////////////////////////////////
Report.prototype.clearData = function()
{
  this.tables = [];
}
////////////////////////////////////////////////////////////////////////////////
Report.prototype.getData = function()
{
  for(var i = 0 ; i < this.tables.length ; i++)
    this.tables[i].getData();
}
////////////////////////////////////////////////////////////////////////////////
Report.prototype.getId = function()
{
  if(this.tables.length)
    return this.tables[0].getId();
}
////////////////////////////////////////////////////////////////////////////////
Report.prototype.getField = function(tab, row, col)
{
  if(tab < this.tables.length)
    return this.tables[tab].getField(row, col);
}
////////////////////////////////////////////////////////////////////////////////
// Report protein class
////////////////////////////////////////////////////////////////////////////////
function ReportProtein()
{
  this.tables = new Array();
}

ReportProtein.prototype = new Report();
////////////////////////////////////////////////////////////////////////////////
ReportProtein.prototype.proteinsPage = function(proteinsTable)
{
  var c = proteinsTable;
  if(typeof(c) == 'undefined') {
    // Define contig list view, not filtered
    c = new tableProtein();
  }
  // define view for this table
  c.defineView();
  // Add the table to table list
  this.tables.push(c);
}
////////////////////////////////////////////////////////////////////////////////
ReportProtein.prototype.proteinPage = function(protein, proteinsTable, contigsTable)
{
  // Define contig list view, not filtered
  var c = proteinsTable;
  if(typeof(c) == 'undefined') {
    // Define contig list view, not filtered
    c = new tableProtein();
  }
  // define view for this table
  c.defineView2();
  // set fitler field, value
  c.setFilter(0, protein);
  // Add the table to table list
  this.tables.push(c);

  // Define contig list view, not filtered
  var d = contigsTable;
  if(typeof(d) == 'undefined') {
    // Define contig list view, not filtered
    d = new tableContig();
  }
  // define view for this table
  d.defineView();
  // set filter field, value
  d.setFilter(1, protein);
  // Add the table to table list
  this.tables.push(d);
}
////////////////////////////////////////////////////////////////////////////////
// Report protein coverage class
////////////////////////////////////////////////////////////////////////////////
function ReportProteinCoverage()
{
  this.tables = new Array();
}

ReportProteinCoverage.prototype = new Report();
////////////////////////////////////////////////////////////////////////////////
ReportProteinCoverage.prototype.proteinCoveragePage = function(protein, tableProtCoverage)
{
  // Define contig list view, not filtered
  var f = tableProtCoverage;
  if(typeof(f) == 'undefined') {
    // Define contig list view, not filtered
    f = new tableProteinCoverage();
  }

  // define view for this table
  f.defineView();
  // set filter field, value
  f.setFilter(0, protein);
  // Add the table to table list
  this.tables.push(f);
}
////////////////////////////////////////////////////////////////////////////////
ReportProteinCoverage.prototype.proteinCoverageCSVPage = function(protein, tableProtCoverage)
{
  // Define contig list view, not filtered
  var f = tableProtCoverage;
  if(typeof(f) == 'undefined') {
    // Define contig list view, not filtered
    f = new tableProteinCoverage();
  }

  // define view for this table
  f.defineView2();
  // set filter field, value
  f.setFilter(0, protein);
  // Add the table to table list
  this.tables.push(f);
}
////////////////////////////////////////////////////////////////////////////////
// Report contig class
////////////////////////////////////////////////////////////////////////////////
function ReportContig()
{
  this.tables = new Array();
}

ReportContig.prototype = new Report();
////////////////////////////////////////////////////////////////////////////////
ReportContig.prototype.contigsPage = function(contigTable)
{
  var c = contigTable;
  if(typeof(c) == 'undefined') {
    // Define contig list view, not filtered
    c = new tableContig();
  }
  // define view for this table
  c.defineView();
  // Add the table to table list
  this.tables.push(c);
}
////////////////////////////////////////////////////////////////////////////////
ReportContig.prototype.contigPage = function(contig, noClusters, contigTable, clusterTable, spectraTable)
{
  // Define contig list view, not filtered
  var c = contigTable;
  if(typeof(c) == 'undefined') {
    // Define contig list view, not filtered
    c = new tableContig();
  }

  // Define contig list view, not filtered
  var d = clusterTable;
  if(typeof(d) == 'undefined') {
    // Define contig list view, not filtered
    d = new tableCluster();
  }

  // Define contig list view, not filtered
  var e = spectraTable;
  if(typeof(e) == 'undefined') {
    // Define contig list view, not filtered
    e = new tableInputSpectra();
  }

  // define view for this table
  c.defineView2();
  // set fitler field, value
  c.setFilter(0, contig);
  //disable borders
  c.drawBorders = 0;
  // Add the table to table list
  this.tables.push(c);

  if(noClusters == 0) {
    // define view for this table
    d.defineView();
    // set fitler field, value
    d.setFilter(1, contig);
    // Add the table to table list
    this.tables.push(d);

  } else {

    // define view for this table
    e.defineViewNoClusters();
    // set fitler field, value
    e.setFilter(17, contig);
    // Add the table to table list
    this.tables.push(e);

  }
}
////////////////////////////////////////////////////////////////////////////////
// Report cluster class
////////////////////////////////////////////////////////////////////////////////
function ReportCluster()
{
  this.tables = new Array();
}

ReportCluster.prototype = new Report();
////////////////////////////////////////////////////////////////////////////////
ReportCluster.prototype.clusterPage = function(cluster, tabClusters, tabSpectra)
{
  // Define contig list view, not filtered
  var d = tabClusters;
  if(typeof(d) == 'undefined') {
    // Define contig list view, not filtered
    d = new tableCluster();
  }

  // Define contig list view, not filtered
  var e = tabSpectra;
  if(typeof(e) == 'undefined') {
    // Define contig list view, not filtered
    e = new tableInputSpectra();
  }

  // define view for this table
  d.defineView2();
  // set fitler field, value
  d.setFilter(0, cluster);
  //disable borders
  d.drawBorders = 0;
  // Add the table to table list
  this.tables.push(d);

  // define view for this table
  e.defineView();
  // set fitler field, value
  e.setFilter(3, cluster);
  // Add the table to table list
  this.tables.push(e);
}
////////////////////////////////////////////////////////////////////////////////
// Report Inpust Spectra class
////////////////////////////////////////////////////////////////////////////////
function ReportInputSpectra()
{
  this.tables = new Array();
}

ReportInputSpectra.prototype = new Report();
////////////////////////////////////////////////////////////////////////////////
ReportInputSpectra.prototype.inputSpectraPage = function(fileIndex, noClusters, tabSpectra)
{
  // Define contig list view, not filtered
  //var c = new tableInputSpectra();
  // define view for this table
  //c.defineView2();
  // set fitler field, value
  //c.filterField = 0;
  //c.filterData  = cluster;
  // Add the table to table list
  //this.tables.push(c);

   // Define contig list view, not filtered
  var e = tabSpectra;
  if(typeof(e) == 'undefined') {
    // Define contig list view, not filtered
    e = new tableInputSpectra();
  }

  // define view for this table
  if(noClusters == 0)
    e.defineView2();
  else
    e.defineViewNoClusters();
  // set fitler field, value
  e.setFilter(5, fileIndex);
  // Add the table to table list
  this.tables.push(e);
}
////////////////////////////////////////////////////////////////////////////////
// Renderer
////////////////////////////////////////////////////////////////////////////////
function renderer(d)
{
  this.dynamic = true;

  if(typeof(d) != 'undefined')
    this.dynamic = d;

  this.currentRow     = 0;  // keeps track of row being drawn
  this.currentCol     = 0;  // keeps track of co; being drawn
  this.reportType     = -1; // stores current report type
  this.reportData     = -1; // stores current report data ID

  this.queueSize      = -1; // tables queue size
  this.queueLocation  = -1; // tables queue location
}
////////////////////////////////////////////////////////////////////////////////
// build the report:
// div      -> where to put the generate page code
// rep      -> the report object
// barType  -> navigation bar
// ipp      -> items (table rows) per page
renderer.prototype.buildReport = function(div, rep, start, ipp, functionName , barType)
{
  // global row counter for this report
  this.currentRow = 0;

  // create reference for storing return data
  var out = createReference("");

  // at this point, tables are supposed to already have all data
  for(var i = 0 ; i < rep.tables.length ; i++) {
    // build table
    this.buildTable(out, rep.tables[i], start, ipp, functionName);
    // clear
    //setReference(out, "");
  };

  // create reference for storing the navigation bar data
  var nav = createReference("");
  // build the navigation bar
  this.buildNavigationBar(nav, rep, barType);
  // horizontal line under
  nav += "<div><table width='100%'><tr></td><td class='ln'></td></tr><tr><td class='VHSep'></td></tr></table></div>";

  if(div == 'NEW') {

    // open in a new window
    var winRef = window.open( "","" )
    winRef.document.writeln("<pre>" + out + "</pre>");
    winRef.document.close();

  } else {

    // set data on page
    var target = document.getElementById(div);
    if(target)
      target.innerHTML = nav + out;
  }
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.addBarLink = function(out, func, img, text, doubleSpace)
{
  var sep = "&nbsp;&nbsp;&nbsp;";

  addToReference(out, "<a href='#' onclick='javascript:" + func + "'>");
  if(SHOW_NAVIGATION_BAR_ICONS)
    addToReference(out, "<img height='24' width='24' src='data:image/png;base64," + img + "' />");
  addToReference(out, "<span style='font-family:Calibri;font-size:140%;color:blue'><u>" + text + "</u></span>");
  addToReference(out, "</a>");
  addToReference(out, sep);
  if(typeof(doubleSpace) == 'undefined')
    return;
  if(doubleSpace == true)
    addToReference(out, sep);
}

renderer.prototype.buildNavigationBar = function(out, rep, barType)
{
  if(this.queueLocation > 0)
    this.addBarLink(out, "TablesAll.goBack();", iconArrowLeft1, "");
  else
    this.addBarLink(out, "", iconArrowLeft2, "");

  if(this.queueLocation < this.queueSize  - 1)
    this.addBarLink(out, "TablesAll.goForward();", iconArrowRight1, "", true);
  else
    this.addBarLink(out, "", iconArrowRight2, "", true);


  // initial page
  this.addBarLink(out, "TablesAll.loadPage(" + PAGE_INITIAL + ",1);", iconHome, "Initial page");
  // initial links
  this.addBarLink(out, "TablesAll.loadPage(" + PAGE_PROTEINS + ",0);", iconProteinList, "Protein list");
  this.addBarLink(out, "TablesAll.loadPage(" + PAGE_CONTIGS + ",0);", iconContigList, "Contig list");

  // if no bartype defined, end here
  if(typeof(barType) == 'undefined')
    return;

  // protein --> add protein list
  //if(barType == 1 || barType == 2) {
  //  this.addBarLink(out, "TablesAll.loadProteinsPage();", iconProteinList, "Protein list");
  //}

  // contig --> add jump to protein
  if(barType == 2) {
    var aux = rep.getId();
    if(aux.length >= 1) {
      this.addBarLink(out, "TablesAll.loadPage(" + PAGE_PROTEIN + "," + aux[0] + ");", iconProtein, "Protein");
      this.addBarLink(out, "TablesAll.loadPage(" + PAGE_PROTEIN_COVERAGE + "," + aux[0] + ");", iconProteinCoverage, "Protein coverage");
    }

    if(aux.length >= 2) {
      this.addBarLink(out, "TablesAll.loadPage(" + PAGE_CONTIG + "," + aux[1] + ");", iconContig, "Contig");
    }
  }

  //if(barType == 3) {
  //  this.addBarLink(out, "TablesAll.loadContigsPage();", iconContigList, "Contig list");
  //}

  //if(barType == 4) {

  //  var aux = rep.getId();
  //  this.addBarLink(out, "TablesAll.loadPage(" + PAGE_CONTIGS + "0,);", iconContigList, "Contig list");
  //  this.addBarLink(out, "TablesAll.loadPage(" + PAGE_CONTIG + "," + aux[1] + ");", iconContig, "Contig");
  //}
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.buildTable = function(out, tab, start, ipp, functionName)
{
  if(tab.exception == "ProteinException")
    return this.renderTableExceptionProteinHeader(out, tab);
  if(tab.exception == "ProteinCoverageException")
    return this.renderTableExceptionProteinCoverage(out, tab);
  if(tab.exception == "ProteinCoverageExceptionCSV")
    return this.renderTableExceptionProteinCoverageCSV(out, tab);

  // create reference for storing return data
  var paginationSequenceBefore = createReference("");
  var paginationSequenceAfter  = createReference("");

  // draw table pagination, in case there is need for it
  if(ipp != -1 && tab.getSize() > PAGE_LENGTH)
    this.paginate(paginationSequenceBefore, paginationSequenceAfter, tab, functionName, start);

  // add pagination sequence at beggining of table
  if(ipp != -1 && tab.getSize() > PAGE_LENGTH)
    addToReference(out, paginationSequenceBefore);


  // table initiator
  var aux;
  if(tab.drawBorders == 1)
    aux = "<table class='result sortable' align='center' id='dataTable'>";
  else
    aux = "<table border='0' align='center'>";

  addToReference(out, aux);

  // column types vector for this tables
  var colTypes = tab.colTypes;

  // draw table header
  if(tab.drawBorders == 1)
    this.buildTableHeaderRow(out, colTypes, tab.tableType, tab.sortColumn, tab.sortDirection);

  // check for empty tables
  if(tab.theArray.length < 1)
    return;

  if(tab.theArray.length == 1 && tab.theArray[0].length == 1)
    return;

  // set initial element index
  var theStart = 0;

  // check if 'start' is defined. if so, use it
  if(typeof(start) != 'undefined')
    theStart = start;

  // Check in pagination is NOT to be used
  if(ipp == -1)
    theStart = 0;

  // when there is only one row and it is not the one showing, that means it is the top. Draw it, anyway
  if(tab.getSize() == 1 && theStart > 1) {
    // get the idx
    var idx = tab.getFirst();
    // the the data row
    var row = tab.theArray[idx];
    // add row
    this.buildTableRow(out, row, colTypes);
    // increase row counter
    this.currentRow++;
    // add table end
    addToReference(out, "</table>");
    return;
  }

  var j = 0;
  var i = tab.moveTo(theStart);
  while(i >= 0 && (j < ipp || ipp == -1)) {
    // get the data row
    var row = tab.theArray[i];
    // build the table row
    this.buildTableRow(out, row, colTypes);
    // move to next item
    i = tab.getNext();
    j++;
    // increase row counter
    this.currentRow++;
  }

  // add table end
  addToReference(out, "</table>");

  // add pagination sequence at beggining of table
  if(ipp != -1 && tab.getSize() > PAGE_LENGTH)
    addToReference(out, paginationSequenceAfter);
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.buildTableHeaderRow = function(out, colTypes, tabType, sortCol, sortDir)
{
  addToReference(out, "<tr>");
  for(var j = 0 ; j < colTypes.length ; j++) {
    var sortThisColumn = (colTypes[j].sortDataCol == sortCol) && (sortCol != -1);
    this.buildTableHeaderCell(out, colTypes[j], tabType, sortThisColumn, sortDir);
  }
    addToReference(out, "</tr>");
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.buildTableHeaderCell = function(out, colType, tabType, sortCol, sortDir)
{
  var aux = "<th>";
  if(colType.sortDataCol != -1)
    aux = "<th onclick='javascript:TablesAll.sortTable(" + tabType + "," + colType.sortDataCol + "," + this.reportType + "," + this.reportData + ");'>";

  addToReference(out, aux);
  //addToReference(out, "<a style='text-decoration: none; font-weight: bold; color: black; ' onmouseover='this.oldstyle=this.style.cssText;this.style.color=\"blue\"' onmouseout='this.style.cssText=this.oldstyle;' class='abc' href='#' title='Click here to Sort!' onclick='javascript:ml_tsort.resortTable(this.parentNode);return false'><span style='color:white'>");

  addToReference(out, "<span style='color: white; '>");
  addToReference(out, colType.columnLabel.replace(/ /g, '&nbsp;'));

  if(sortCol) {
    if(sortDir)
      aux = (stIsIE ? "&nbsp<font face='webdings'>6</font>" : "&nbsp;&#x25BE;");
    else
      aux = (stIsIE ? "&nbsp<font face='webdings'>5</font>" : "&nbsp;&#x25B4;");
    addToReference(out, aux);
  }

  addToReference(out, "</span>");

  //addToReference(out, "</a>");
  addToReference(out, "</th>");
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.buildTableRow = function(out, row, colTypes)
{
  this.currentCol = 0;
  addToReference(out, "<tr>");
  for(var j = 0 ; j < colTypes.length ; j++) {
    this.buildTableCell(out, row, colTypes[j]);
    this.currentCol++;
  }
  addToReference(out, "</tr>");
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.buildTableCell = function(out, row, colType)
{
  // auxiliary variables
  var cls = "", slink = "";

  // gather needed attributes
  if(colType.link.length)
    slink = this.parseTemplates(colType.link, row, TAG_OPEN, TAG_CLOSE, 0);

  if(colType.cssClass.length)
    cls = " class='" + base.cssClass + "'";

  // cell begin HTML tag with class
  var aux = "<td align='center' valign='middle'" + cls + ">";
  addToReference(out, aux);
  // Link section
  if(colType.link.length) {
    aux = "<a href='" + slink + "'>";
    addToReference(out, aux);
  }
  // process base class cell renderer
  this.buildTableCellSpecific(out, row, colType);
  // Link section
  if(colType.link.length) {
    aux = "</a>";
    addToReference(out, aux);
  }
  // cell end HTML tag
  addToReference(out, "</td>");

  //addToReference(out, "<td>");
  //var content = this.parseTemplates(colType.text, row, TAG_OPEN, TAG_CLOSE, 0);
  //addToReference(out, content);
  //addToReference(out, "</td>");
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.buildTableCellSpecific = function(out, row, colType)
{
  // check if cell is dynamic in a non-dynamic report
  if(!this.dynamic && colType.dynamic)
    return;

  // check for valid cells
  if(colType.validator.length) {
    var aux = this.parseTemplates(colType.validator, row, TAG_OPEN, TAG_CLOSE, 0);
    if(aux.length == 0)
      return;
  }

  // test for Image On Demand column type
  if(colType.rtti == REPORT_CELL_TYPE_IOD)
    return this.buildCellImageOnDemand(out, row, colType);

  // test for String column type
  if(colType.rtti == REPORT_CELL_TYPE_STRING)
    return this.buildCellString(out, row, colType);

  // test for String column type
  if(colType.rtti == REPORT_CELL_TYPE_STRING_MULTIPLE)
    return this.buildCellStringMultiple(out, row, colType);

  // test for Box column type
  if(colType.rtti == REPORT_CELL_TYPE_BOX)
    return this.buildCellBox(out, row, colType);

  // something's wrong...
  return -1;
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.buildCellImageOnDemand = function(out, row, colType)
{
  // auxiliary variables
  var icon = "", label = "", url = "", tag = "", tag2 = "", tag3 = "", tag4 = "", id = "";

  // set ids for images.
  if(colType.id.length) {
    id = this.parseTemplates(colType.id, row, TAG_OPEN, TAG_CLOSE, 0);
    tag  = IMAGE_ICON_ID_PREFIX       + id;
    tag2 = IMAGE_ICON_CTRL_ID_PREFIX  + id;
    tag3 = IMAGE_LARGE_ID_PREFIX      + id;
    tag4 = IMAGE_LARGE_CTRL_ID_PREFIX + id;
  } else {
    tag  = IMAGE_ICON_ID_PREFIX       + globalImage;
    tag2 = IMAGE_ICON_CTRL_ID_PREFIX  + globalImage++;
    tag3 = IMAGE_LARGE_ID_PREFIX      + globalImage;
    tag4 = IMAGE_LARGE_CTRL_ID_PREFIX + globalImage++;
  }

  // Icon path/image (src)
  if(colType.iconParams.length) {
    // get parsed parameters / URL
    var pars = new Array();
    var pars2 = new Array();
    this.parseParamsVector(pars, pars2, colType.iconParams, row);
    // if there is a renderer, use it to render the image
    if(colType.iconRenderer.length) {
      var seqi = this.parseTemplates(colType.iconSequence, row, TAG_OPEN, TAG_CLOSE, 0);
      this.getImage(colType.iconRenderer, pars, pars2, tag, "src", tag2, seqi);
    }
    // URL
    if(colType.link.length) {
      url = colType.link;
    }
    // the tag
    var aux = "<img id='" + tag + "'";
    if(colType.onClick.length) {
      url = this.parseTemplates(colType.onClick, row, TAG_OPEN, TAG_CLOSE, 0);
      aux += " onclick='" + url + "'";
    }
    aux += " src='data:image/gif;base64," + loadingImage + "' />";
    // the hidden command
    aux += "<input id='" + tag2 + "' type='hidden' text=''>";
    // store
    addToReference(out, aux);
  }


  // URL template to be used to get the image (href)
  if(colType.renderer.length) {
    // get parsed parameters / URL
    var pars = new Array();
    var pars2 = new Array();
    this.parseParamsVector(pars, pars2, colType.params, row);
    var seq = this.parseTemplates(colType.imgSequence, row, TAG_OPEN, TAG_CLOSE, 0);
    this.getImage(colType.renderer, pars, pars2, tag3, "href", tag4, seq);
    // url for IOD
    var image64 = "data:image/png;base64," + loadingImage;
    var aux =  "<a id='" + tag3 + "' href=\"" + image64 + "\" rel=\"lightbox\">";
    // the hidden command
    aux += "<input id='" + tag4 + "' type='hidden' text=''>";
    // store
    addToReference(out, aux);
  }

  // clickable label
  if(colType.label.length) {
    label = this.parseTemplates(colType.label, row, TAG_OPEN, TAG_CLOSE, 0);
    // split the sequence, if so
    if(colType.splitLabel == "true")
      label = this.splitSequence(label);
    var labelId = "";
    if(colType.id.length)
      labelId = " ID='" + id + "'";
    var aux = "<div" + labelId + ">" + label + "</div>";
    addToReference(out, aux);
  }

  // url for IOD - terminator
  if(colType.renderer.length) {
    var aux = "</a>";
    addToReference(out, aux);
  }

  return 1;
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.buildCellString = function(out, row, colType)
{
  // auxiliary variables
  var onclick = "", id = "", text = "", aux= "";

  // gather needed attributes
  if(colType.text.length) {
    text = this.parseTemplates(colType.text, row, TAG_OPEN, TAG_CLOSE, 0);
    if(colType.splitText)
      text = this.splitText(text);
  }

  if(colType.onClick.length)
    onclick = " onclick='" + this.parseTemplates(colType.onClick, row, TAG_OPEN, TAG_CLOSE, 0) + "'";

  if(colType.id.length)
    id = " ID='" + this.parseTemplates(colType.id, row, TAG_OPEN, TAG_CLOSE, 0) + "'";


  // edit box
  if(colType.isInput) {
    aux = "<br /><input class='iud' type='text'" + id + onclick + " />";
  }

  // button
  else if(colType.isButton) {
    aux = "<br /><input type='button' value='" + text + "'" + onclick + id + " />";

  // regular text
  } else {
    aux = "<p" + id + onclick + ">" + text + "</p>";
  }

  addToReference(out, aux);

  return 1;
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.buildCellStringMultiple = function(out, row, colType)
{
  // auxiliary variables
  var text = "", link = "";
  var links = new Array();
  var texts = new Array();

  // gather needed attributes
  if(colType.link.size())
    link = this.parseTemplates(colType.link, row, TAG_OPEN, TAG_CLOSE, 0);

  if(colType.text.size())
    text = this.parseTemplates(colType.text, row, TAG_OPEN, TAG_CLOSE, 0);

  links = link.split(TABLE_SEP_L1);
  texts = text.split(TABLE_SEP_L1);

  for(var i = 0 ; i < texts.length ; i++) {

    // the ith link
    if(links.length > i) {
      aux = "<a href='" + colType.linkPrefix + links[i] + colType.linkSuffix + "'>";
      addToReference(out, aux);
    }

    // regular text
    aux = "<p>" + texts[i] + "</p>";
    addToReference(out, aux);

    // the ith link
    if(links.size() > i) {
      aux = "</a>";
      addToReference(out, aux);
    }

    // line break
    if(i < texts.size()-1) {
      aux = "<br>";
      addToReference(out, aux);
    }
  }

  return 1;
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.buildCellBox = function(out, row, colType)
{
  // sequences box begin sequence
  var aux = "<table align='center' border='0' width='100%'><tr align='center'><td>";
  addToReference(out, aux);

  // sequences box cycle thru all cells
  var sequences = colType.sequences;

  var begin = true;

  for(var i = 0 ; i < sequences.length ; i++) {

    if(!this.dynamic && sequences[i].dynamic)
      continue;

    // validate cell
    if( sequences[i].validator.length) {
      aux = this.parseTemplates(sequences[i].validator, row, TAG_OPEN, TAG_CLOSE, 0);
      if(!aux.length) {
        continue;
      }
    }

    // if there is a column label
    if(sequences[i].columnLabel.length) {
      //new line, if it is not the first one
      if(!begin) {
        aux = "<br>"; //"<br><br>";
        addToReference(out, aux);
      }

      // the column label
      aux = "<b>" + sequences[i].columnLabel + "</b>";
      //new line
      aux += "<br>";
      // add to queue
      addToReference(out, aux);
      // subsequent new lines between items will be inserted
      begin = false;
    }

    var link = "";

    // gather needed attributes
    if(sequences[i].link.length)
      link = this.parseTemplates(sequences[i].link, row, TAG_OPEN, TAG_CLOSE, 0);

    // Link section
    if(sequences[i].link.length) {
      aux = "<a href='" + link + "'>";
      addToReference(out, aux);
    }

    // call base class to render cell
    this.buildTableCellSpecific(out, row, sequences[i]);

    // Link section
    if(sequences[i].link.length) {
      aux = "</a>";
      addToReference(out, aux);
    }
  }

  // sequences box end sequence
  aux = "</td></tr></table>";
  addToReference(out, aux);

  return 1;
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.parseTemplates = function(str, row, tagOpen, tagClose, add)
{
  // return string and auxiliary string to store tag contents
  var ret = "", tag;
  // store the position after each tag
  var lastPosition = 0;
  // get the first tag
  var first = str.indexOf(tagOpen, lastPosition);
  var second = str.indexOf(tagClose, first+1);
  // repeat until all the tags are processed
  while(first != -1 && second != -1) {
    // copy in beetwen tags
    ret += str.substr(lastPosition, first - lastPosition);
    // copy the tag contents to an auxiliary string
    tag = str.substr(first+1, second - first - 1);
    // get the tag contents
    ret += this.getTag(tag, row, tagOpen, tagClose, add);
    // update last position to past the tag
    lastPosition = second + 1;
    // get next tag
    first = str.indexOf(tagOpen, lastPosition);
    second = str.indexOf(tagClose, first+1);
  }

  // the remaining of the string
  ret += str.substr(lastPosition);
  // return the string
  return ret;
}
///////////////////////////////////////////////////////////////////////////////
renderer.prototype.getTag = function(tag, row, tagOpen, tagClose, add)
{
  // set default return value
  var ret = "";
  //ret = tagOpen;
  //ret += tag;
  //ret += tagClose;

  // find multi-tag contents
  var aux = tag.split('|');

  for(var i = 0 ; i < aux.length ; i++) {
    // translate the tag contents
    var content = this.translateTag(aux[i], row, add);
    // check for non-empty contents, and stop earching if not empty
    if(content.length)
      return content;
  }

  // return the translated attribute
  return ret;
}
///////////////////////////////////////////////////////////////////////////////
renderer.prototype.translateTag = function(tag, row, add)
{
  // set default return value
  var ret = "";

  // search for a number
  var myRegExp = /[a-z,A-Z]/;

  var matchPos1 = tag.search(myRegExp);

  if(matchPos1 == -1) {
    var aux = parseInt(tag);
    if(aux < row.length)
      ret = row[aux];

    if(add) {
      var aux2 = parseInt(ret);
      aux2 += add;
      ret = String(aux2);
    }
  }

  // seach for row
  if(tag == INTERNAL_ROW)
    ret = String(this.currentRow);
  // search for col
  else if(tag == INTERNAL_COL)
    ret = String(this.currentCol);
  // projectdir tag
  else if(tag == INTERNAL_PROJDIR)
    ret = PROJECT_DIR;
  else if(tag == INTERNAL_MS_FNAME)
    ret = GLOBAL_SPECS_MS_FILENAME;

  // return the translated attribute
  return ret;
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.paginate = function(out, out2, tab, functionName, start)
{
  if(typeof(start) == 'undefined')
    start = 0;

  // auxiliary vars used
  var aux, aux2, aux3 = "";

  // initial sequence - table beggining
  aux = "<table border='0' align='center'><tr><td>";
  aux2  = aux + "&nbsp;</td></tr><tr><td>";

  var k = 0;
  var pos = tab.getFirst();
  while(pos >= 0) {

    var id1 = tab.getSingleId(pos);
    var j = tab.peek(pos + PAGE_LENGTH - 1);
    var id2 = tab.getSingleId(j);

    var aux4 = "[" + id1;
    if(j > pos)
      aux4 += "&nbsp;-&nbsp;" + id2;
    aux4 += "]";

    if(start >= k && start < k + PAGE_LENGTH) {
      aux3 += "<span style='color:#FF0000'>";
      aux3 += aux4;
      aux3 += "</span>";

    } else {
      aux3 += "<a href='#' onclick='javascript:" + functionName + k + ");'>";
      aux3 += aux4;
      aux3 += "</a>";
    }
    aux3 += " ";

    pos = tab.getNext(PAGE_LENGTH);
    k += PAGE_LENGTH;
  }


  aux  += aux3 + "</td></tr><tr><td>&nbsp;</td></tr></table>";
  aux2 += aux3 + "</td></tr></table>";

  addToReference(out, aux);
  addToReference(out2, aux2);
}
///////////////////////////////////////////////////////////////////////////////
// generate params vector based on options object
renderer.prototype.parseParamsVector = function(params, paramsReload, options, row)
{
  // go thru all options
  for(var i = 0 ; i < options.length ; i++) {

    // validate option
    if(options[i].validator.length) {
      var aux = this.parseTemplates(options[i].validator, row, TAG_OPEN, TAG_CLOSE, 0);
      if(!aux.length) {
        continue;
      }
    }

    // store params
    params.push(options[i].param);
    if(options[i].option.length) {
      var aux = this.parseTemplates(options[i].option, row, TAG_OPEN, TAG_CLOSE, 0);
      params.push(aux);

      if(options[i].store == 1) {
        paramsReload.push(options[i].param);
        paramsReload.push(aux);
      }
    }
  }
}
///////////////////////////////////////////////////////////////////////////////
// Store an image request in the image queue
renderer.prototype.getImage = function(renderer, params, paramsReload, tag, target, tag2, seq)
{
  // initialize parameters variables
  var allParams = "", tag2params = "";

  // compose parameters into a single string
  for(var i = 0 ; i < params.length ; i++, allParams += "&")
    allParams += params[i];

  for(var i = 0 ; i < paramsReload.length ; i++, tag2params += "&")
    tag2params += paramsReload[i];

  // build element
  var elem = new cacheElement();
  elem.renderer   = renderer;
  elem.params     = allParams;
  elem.tag        = tag;
  elem.tag2       = tag2;
  elem.tag2params = tag2params;
  elem.sequence   = seq;
  elem.target   = target;

  // store it
  TablesAll.iCache.queue.push(elem);
}
///////////////////////////////////////////////////////////////////////////////
// Table rendering exceptions
///////////////////////////////////////////////////////////////////////////////
renderer.prototype.breakProteinIntoChunks = function(inData)
{
  var count = 0;
  for(var i = 0 ; i < inData.length ; i++) {
    // string container
    var aux = "";
    for(var j = 0 ; j < inData[i].length ; j++) {
      // line break;
      if(count % AAS_PER_LINE == 0) {
        aux += "<br>";
      // spacer
      } else if(count % AAS_GROUP_SIZE == 0) {
        aux += "&nbsp;";
      }
      // copy element
      aux += inData[i][j];
      count++;
    }
    inData[i] = aux;
  }
  return count;
}
///////////////////////////////////////////////////////////////////////////////
renderer.prototype.colorProteinString = function(inData, out)
{
  var aux = "";

  for(var i = 0 ; i < inData.length ; i++) {
    if(inData[i].length) {
      aux += "<font color='";
      if(i % 2) {
        aux += "0";
      } else {
        aux += "#AAAAAA";
      }
      aux += "'>";
      aux += inData[i];
      aux += "</font>";
    }
  }
  addToReference(out, aux);
}
///////////////////////////////////////////////////////////////////////////////
renderer.prototype.renderTableExceptionProteinHeader = function(out, tab)
{
  var idx = tab.getFirst();
  var row = tab.theArray[idx];
  // get the protein name, at indice 1
  var proteinId    = row[TABLE_PROTEINS_FIELD_ID];
  var proteinName  = row[TABLE_PROTEINS_FIELD_NAME];
  var contigs      = row[TABLE_PROTEINS_FIELD_CONTIGS];
  var spectra      = row[TABLE_PROTEINS_FIELD_SPECTRA];
  var aas          = row[TABLE_PROTEINS_FIELD_AAS];
  var coverage     = row[TABLE_PROTEINS_FIELD_COVERAGE];
  var sequence     = row[TABLE_PROTEINS_FIELD_SEQUENCE];

  // format protein sequence
  var count = 0;
  var coloredProtein = createReference("");
  var breaked = sequence.split(TABLE_SEP_L1);
  var count = this.breakProteinIntoChunks(breaked);
  this.colorProteinString(breaked, coloredProtein);

  // build legend for protein sequence
  var legend = "";
  var current = 1;
  while(current <= count) {
    legend += "<br>";
    legend += parseInt(current);
    current += AAS_PER_LINE;
  }

  // protein header HTML code
  var aux = "";
  aux += "<table class='result' width='100%' style='border-spacing: 0px;' align='center'>";
  aux += "<tr>";
  aux += "<td colspan='0'><h2><i>" + proteinName + "</i></h2>";
  aux += "<hr><b>" + contigs + " contigs, " + spectra + " spectra, " + aas + " amino acids, " + coverage + " coverage" + "</b></td>";
  aux += "<td></td>";
  aux += "</tr>";
  aux += "<tr> ";
  aux += "<td align='right'><tt>" + legend + "</tt></td>";
  aux += "<td><tt>" + coloredProtein + "</tt></td>";
  aux += "</tr>";
  aux += "</table>";

  // link to protein detains page
  aux += "<div align='center'>";
  aux += "<br><a href='#' onclick='javascript:TablesAll.loadPage(" + PAGE_PROTEIN_COVERAGE + "," + proteinId + ");'>Protein coverage</a>";
  aux += "</div>";
  aux += "<br>";

  addToReference(out, aux);

    // return status OK
  return 1;
}
////////////////////////////////////////////////////////////////////////////////
// Table Protein Coverage
////////////////////////////////////////////////////////////////////////////////
// Generated table, per row:
//
// cells[row][0] -> text          --> Protein ID
// cells[row][1] -> text          --> Protein name
// cells[row][2] -> text          --> Protein length (AAs)
// cells[row][3] -> text list     --> Protein sequence, separated by |
// cells[row][4] -> Contig data   --> CSPS Contigs, separated by |
// cells[row][5] -> Contig data   --> SPS Contigs, separated by |
//      Contig data: : items separated by &
//        0 -> Contig ID
//        1 -> Contig name
//        2 -> Contig start
//        3 -> Contig end
//        4 -> Contig items
//           Contig Item: items separated by @. Contents separated by !
//              0 -> Beginning
//              1 -> Span
//              0 -> Content
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.renderTableExceptionProteinCoverage = function(out, tab)
{
  var idx = tab.getFirst();
  var row = tab.theArray[idx];

  // get the protein coverage data
  var proteinId       = parseInt(row[TABLE_COVERAGE_FIELD_ID]);
  var proteinName     = row[TABLE_COVERAGE_FIELD_NAME];
  var proteinLength   = parseInt(row[TABLE_COVERAGE_FIELD_SEQ_REFERENCE]);
  var proteinSequence = row[TABLE_COVERAGE_FIELD_PROT_SEQUENCE];
  var contigCsps      = row[TABLE_COVERAGE_CSPS_DATA];
  var contigSps       = row[TABLE_COVERAGE_SPS_DATA];

  // global protein length used to send protein sequence back to server
  globalProteinLength = proteinLength;

  // split the protein
  var proteinData = proteinSequence.split(TABLE_SEP_L1);

  // variables to hold contig data
  var contigDataCsps = new Array();
  var contigDataSps  = new Array();

  // get CSPS contig data
  this.buildContigDataStructure(contigDataCsps, contigCsps);
  // get SPS contig data
  this.buildContigDataStructure(contigDataSps, contigSps);

  // protein header HTML code
  var page = "";
  page += "<table class='result' width='100%' style='border-spacing: 0px;' align='center'>";
  page += "<tr>";
  page += "<td colspan='0'><h2><i>" + proteinName + "</i></h2><hr></td>";
  page += "</tr>";
  page += "<tr><td>&nbsp;</td></tr>";
  page += "</table>";

  // CSV protein coverage info
  page += "<table><tr><td><a href='#' onclick='javascript:TablesAll.loadProteinDetailsCSV(" + proteinId + ");'>Protein coverage as Excel-ready format (TXT file)</a></td></tr><tr><td>&nbsp;</td></tr></table>";


  addToReference(out, page);

  // general position indexer
  var i = 0;

  // Keep it under protein size
  while(i < proteinLength) {

    // Build a map key index. This is used to maintain the contig index order when outputing them under the protein sequence
    var spsID  = new Array();
    var cspsID = new Array();
    // get the csps contig indexes
    this.getOrder(contigDataCsps, i, CELLS_PER_LINE, cspsID);
    // get the sps contig indexes
    this.getOrder(contigDataSps, i, CELLS_PER_LINE, spsID);

    // if we are starting a new table, add table beggining
    page = "<table class=\"result2\" width=\"100%\" style=\"background-color: #CCCFFF\">\n";

    // store data so far
    addToReference(out, page);

    // output protein
    this.generateProteinSequence(out, i, proteinData, proteinLength);

    // generate input sequence slots
    if(this.dynamic)
      this.generateInputSequence(out, i, proteinData, proteinLength);

    // Add CSPS contig information (if exists)
    this.generateOutputContig(i, proteinLength, cspsID, out, CELLS_PER_LINE, contigDataCsps, false);

    // Add SPS contig information (if exists)
    this.generateOutputContig(i, proteinLength, spsID, out, CELLS_PER_LINE, contigDataSps, true);

    // HTML table terminator
    page = "</table><br>\n";
    addToReference(out, page);

    i += CELLS_PER_LINE;
  }

  if(this.dynamic) {
    page += "<table width='100%'><tr><td>&nbsp;</td></tr>";
    page += "<table width='100%'><tr><td>By clicking '" + REPORT_BUTTON_ALIGN + "', the modified protein will be added to the protein database file with the ID and description provided below.</td></tr>";
    page += "<table width='100%'><tr><td>Protein ID: <input id='ProtID' type='text' size='40'></td></tr>";
    page += "<table width='100%'><tr><td>Description: <input id='ProtDESC' type='text' size='130'></td></tr>";
    page += "<table width='100%'><tr><td>&nbsp;</td></tr>";
    page += "<tr><td style='text-align:center;' width='100%'><input type='button' value='" + REPORT_BUTTON_ALIGN + "' onclick='javascript:submitCoverage();' width='300px' /></td></tr></table>";
  }

  //page  = "</div></div>";
  //page += "</body>";
  addToReference(out, page);
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.renderTableExceptionProteinCoverageCSV = function(out, tab)
{
  var idx = tab.getFirst();
  var row = tab.theArray[idx];

  // get the protein coverage data
  var proteinId       = parseInt(row[TABLE_COVERAGE_FIELD_ID]);
  var proteinName     = row[TABLE_COVERAGE_FIELD_NAME];
  var proteinLength   = parseInt(row[TABLE_COVERAGE_FIELD_SEQ_REFERENCE]);
  var proteinSequence = row[TABLE_COVERAGE_FIELD_PROT_SEQUENCE];
  var contigCsps      = row[TABLE_COVERAGE_CSPS_DATA];
  var contigSps       = row[TABLE_COVERAGE_SPS_DATA];

  // split the protein
  var proteinData = proteinSequence.split(TABLE_SEP_L1);

  // variables to hold contig data
  var contigDataCsps = new Array();
  var contigDataSps  = new Array();

  // get CSPS contig data
  this.buildContigDataStructure(contigDataCsps, contigCsps);
  // get SPS contig data
  this.buildContigDataStructure(contigDataSps, contigSps);

  // general position indexer
  var i = 0;

  // Keep it under protein size
  while(i < proteinLength) {

    // Build a map key index. This is used to maintain the contig index order when outputing them under the protein sequence
    var spsID  = new Array();
    var cspsID = new Array();
    // get the csps contig indexes
    this.getOrder(contigDataCsps, i, CELLS_PER_LINE, cspsID);
    // get the sps contig indexes
    this.getOrder(contigDataSps, i, CELLS_PER_LINE, spsID);

    // output protein
    this.generateProteinSequenceCSV(out, i, proteinData, proteinLength);

    // Add CSPS contig information (if exists)
    this.generateOutputContigCSV(i, proteinLength, cspsID, out, CELLS_PER_LINE, contigDataCsps, false);

    // Add SPS contig information (if exists)
    this.generateOutputContigCSV(i, proteinLength, spsID, out, CELLS_PER_LINE, contigDataSps, true);

    i += CELLS_PER_LINE;
  }
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.generateProteinSequence = function(out, i, proteinData, proteinLength)
{
  var page = "";

  page += "<tr>";
  page += "<td class='rc3' align='center'>";
  page += parseInt(i+1);
  page += "&nbsp;</td>";

  for(var j = i ; ( j < i + CELLS_PER_LINE ) && ( j < proteinLength ) ; j++) {

    page += "<td align='center' id='" + PEP_ELEM_PREFIX + j + "'";
    // if an empty cell, it's a separator column. It should be 1 pixel wide
    if( proteinData[j].length == 0 )
      page += "class='rh2' ";
    else {
      page += "class='rh1' ";
    }
    page += ">";
    // The AA from the protein sequence
    page +=  proteinData[j];
    // header cell terminator
    page += "</td>";
  }
  // Header row terminator
  page += "</tr>\n";

  // store data so far
  addToReference(out, page);
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.generateProteinSequenceCSV = function(out, i, proteinData, proteinLength)
{
  var page = "";

  // if we are starting a new table, add table beggining
  page += '\n';
  page += parseInt(i+1);
  page += CSV_SEP;

  for(var j = i ; ( j < i + CELLS_PER_LINE ) && ( j < proteinLength ) ; j++)
    page += CSV_SEP + proteinData[j] + CSV_SEP;

  // Header row terminator
  page += "\n";

  // store data so far
  addToReference(out, page);
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.generateInputSequence = function(out, i, proteinData, proteinLength)
{
  var page = "";

  page += "<tr>";
  page += "<td class='rc3' align='right'>";
  //page += parseInt(i+1);
  page += "<input type='checkbox' onchange='javascript:fillCoverageRow(this, " + i + ");' id='ck" + i + "' />";
  //page += "<input type='checkbox' id='ck" + i + "' />";
  page += "&nbsp;</td>";

  for(var j = i ; ( j < i + CELLS_PER_LINE ) && ( j < proteinLength ) ; j++) {

    page += "<td ";
    // if an empty cell, it's a separator column. It should be 1 pixel wide
    if( proteinData[j].length == 0 )
      page += "class='rh2' ";
    else {
      page += "class='rh1' ";
    }
    page += ">";
    // The AA from the protein sequence
    page += "<input class='iuc' type='text' id='" + INP_ELEM_PREFIX + j + "' />";
    // header cell terminator
    page += "</td>";
  }
  // Header row terminator
  page += "</tr>\n";

  // store data so far
  addToReference(out, page);
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.generateOutputContig = function(i, proteinSize, vectorID, out, cellPerLine, contig, link)
{
  var page = "";
  // Add contig information (if exists)
  for(var j = 0 ; j < vectorID.length ; j++)  {
    // get the contig sequence info
    var contigSequence = contig[vectorID[j]];
    // Check if sequence in the range we are outputing now
    if( (contigSequence[2] < i + cellPerLine) &&
        (contigSequence[3] > i              )    ) {

      // Write the contig id and link
      if(link) {
        page += "<tr><th align='right'><a href='#' onclick='javascript:TablesAll.loadPage(" + PAGE_CONTIG + ",";
        page += this.getIntFromSeqName(contigSequence[1]); // 1 = name
        page += ");' style='color: white'>";
        page += contigSequence[1];
        page += "</a></th>";

        //page += "<tr><th align=\"right\">";
        //page += contigSequence.name;
        //page += "</th>";
      } else {
        page += "<tr>";
        page += "<td class='rc4'>";
        page += "CSPS ";
        //page += contigSequence.name;
        page += parseInt(contigSequence[0] + 1);
        page += "&nbsp;";
        page += "</TD>";
      }

      // find first cell to output
      var l = 0;
      while( (l < contigSequence[4].length) &&
             (i > contigSequence[4][l][0] + contigSequence[4][l][1]) )
        l++;

      // cycle thru
      for(var k = i ; (k < i + cellPerLine) && (k < proteinSize) ; k++) {

        // if start position is lower than current position, output an empty cell
        if(k < contigSequence[2])
          page += "<td class='rc2' />\n";
        else if( (l >= contigSequence[4].length) )
          page += "<td class='rc2' />\n";
        // otherwise, the content
        else {

          page += "<td ";
          // page += " class=\"rc1\" style=\"background-color: transparent; border: solid 0 #060; border-left-width:1px;border-right-width:1px;\" ";

          var border = 0;

          var outputString = contigSequence[4][l][2];

          // Calc colspan nr of occupied cells
          var colspan = contigSequence[4][l][1] + 1;
          // careful with split cells at the beggining or end -- end
          if(contigSequence[4][l][0] + contigSequence[4][l][1] >= i + cellPerLine) {
            colspan -= contigSequence[4][l][0] + contigSequence[4][l][1] - i - cellPerLine + 1;
            border += 2;
            if(colspan < (contigSequence[4][l][1] + 1) / 2 )
              outputString = "";
          }
          // beggining
          if(contigSequence[4][l][0] < i) {
            colspan -= i - contigSequence[4][l][0];
            border++;
            if(colspan <= (contigSequence[4][l][1] + 1) / 2 )
              outputString = "";
          }

          page += " class='rca";
          page += parseInt(border);
          page += "' ";

          if(colspan > 1) {
            page += " colspan='";
            page += parseInt(colspan);
            page += "'";
            k += colspan-1;
          }
          page += '>';
          page +=  outputString;
          page += "</td>";
          l++;
        }
      }
      page += "</tr>\n";
    }
  }
  addToReference(out, page);
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.generateOutputContigCSV = function(i, proteinSize, vectorID, out, cellPerLine, contig, link)
{
  var page = "";
  // Add contig information (if exists)
  for(var j = 0 ; j < vectorID.length ; j++)  {
    // get the contig sequence info
    var contigSequence = contig[vectorID[j]];
    // Check if sequence in the range we are outputing now
    if( (contigSequence[2] < i + cellPerLine) &&
        (contigSequence[3] > i              )    ) {

      // Write the contig id and link
      if(link) {
        page += contigSequence[1];
      } else {
        page += parseInt(contigSequence[0] + 1);
      }
      // separator
      page += CSV_SEP;

      // find first cell to output
      var l = 0;
      while( (l < contigSequence[4].length) &&
             (i > contigSequence[4][l][0] + contigSequence[4][l][1]) )
        l++;

      // cycle thru
      for(var k = i ; (k < i + cellPerLine) && (k < proteinSize) ; k++) {

        // if start position is lower than current position, output an empty cell
        if(k < contigSequence[2]) {
          page += CSV_SEP;
          page += CSV_SEP;
        } else if( (l >= contigSequence[4].length) ) {
          page += CSV_SEP;
          page += CSV_SEP;
        // otherwise, the content
        } else {

          var border = 0;

          var outputString = contigSequence[4][l][2];

          // Calc colspan nr of occupied cells
          var colspan = contigSequence[4][l][1] + 1;
          // careful with split cells at the beggining or end -- end
          if(contigSequence[4][l][0] + contigSequence[4][l][1] >= i + cellPerLine) {
            colspan -= contigSequence[4][l][0] + contigSequence[4][l][1] - i - cellPerLine + 1;
            border += 2;
            if(colspan < (contigSequence[4][l][1] + 1) / 2 )
              outputString = "";
          }
          // beggining
          if(contigSequence[4][l][0] < i) {
            colspan -= i - contigSequence[4][l][0];
            border++;
            if(colspan <= (contigSequence[4][l][1] + 1) / 2 )
              outputString = "";
          }

          if(!(border & 0x01))
            page += '|';

          if(colspan == 1) {
            // cell content
            page += CSV_SEP;
            page += outputString;
          } else {

            if((outputString.length > 0) && (outputString[0] == '(')) {
              // outputing (xx, yy), and empty cells following
              page += CSV_SEP;
              page += outputString;
              // until the end of cell
              while(--colspan && (k < i+cellPerLine)) {
                page += CSV_SEP;
                page += CSV_SEP;
                k++;
              }

            } else {
              // outputing A.B.C.D
              var cells = 0;
              while( (cells < colspan-1) && (k < i+cellPerLine)) {
                page += CSV_SEP;
                page += outputString[cells];
                page += CSV_SEP;
                page += '.';
                k++;
                cells++;
              }
              page += CSV_SEP;
              page += outputString[cells];

            }

          }
          // cell end
          page += CSV_SEP;
          // right border content (separator)
          if( (!(border & 0x02)) && (true) && (true) ) ;
//            page += '|';

          l++;
        }
      }
      page += '\n';
    }
  }
  addToReference(out, page);
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.getOrder = function(contig, i, size, order)
{
  // temporary vector to hold contig start position per contig
  var aux = new Array();
  // cycle thru all contigs
  for(var j = 0 ; j < contig.length ; j++ ) {
    // Check for empty contigs
    if(contig[j][4].length == 0) continue;
    // Check if sequence in the range we are outputing now
    if( (contig[j][2] < i + size) &&
        (contig[j][3] > i              )    ) {
      // create ordering cell with contig info
      var orderingCell = new Array();
      orderingCell[0] = j; //contig[j][0];
      orderingCell[1] = contig[j][2];
      orderingCell[2] = contig[j][3];
      aux.push(orderingCell);
    }
  }

  // Order
  aux.sort(orderSortingFunction);
  // set order in order vector
  for(var k = 0 ; k < aux.size() ; k++)
    order.push(aux[k][0]);
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.getIntFromSeqName = function(seq)
{
  var aux = seq.split(":");
  if(aux.length > 1)
    return aux[1];
  return "";
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.splitSequence = function(sequence)
{
  var ret = "";
  var count = 0;

  for(var i = 0 ; i < sequence.length ; i++) {

    if(sequence[i] == '(')
      while(sequence[i] != ')' && i < sequence.length) {
        ret += sequence[i];
        count++;
        i++;
      }

    if(sequence[i] == '[')
      while(sequence[i] != ']' && i < sequence.length) {
        ret += sequence[i];
        count++;
        i++;
      }

    if(i < sequence.length)
      ret += sequence[i];
    count++;

    if(count >= 10) {
      ret += "<wbr>";
      count =0;
    }
  }
  return ret;
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.splitText = function(sequence)
{
  var ret = "";
  var count = 0;

  for(var i = 0 ; i < sequence.length ; i++) {

    ret += sequence[i];
    count++;

    if(count >= 10) {
      ret += "<wbr>";
      count =0;
    }
  }
  return ret;
}
////////////////////////////////////////////////////////////////////////////////
renderer.prototype.buildContigDataStructure = function(contigData, contig)
{
  // split by contig
  var aux = contig.split(TABLE_SEP_L1);
  // cycle thru all contigs
  for(var i = 0 ; i < aux.length ; i++) {
    // array to hold data for one contig
    contigData[i] = new Array();
    // get contig header info + elements
    var aux2 = aux[i].split(TABLE_SEP_L2);
    // put header data
    // ID
    contigData[i][0] = parseInt(aux2[0]);
    // Name
    contigData[i][1] = aux2[1];
    // start
    contigData[i][2] = parseInt(aux2[2]);
    // end
    contigData[i][3] = parseInt(aux2[3]);
    // array for contig elements
    contigData[i][4] = new Array();
    // get elements
    if(typeof(aux2[4]) != 'undefined') {
      var elems = aux2[4].split(TABLE_SEP_L3);
      // cycle thru elems
      for(var j = 0 ; j < elems.length ; j++) {
        // elemet storage space
        contigData[i][4][j] = new Array();
        // split elements
        var elem = elems[j].split(TABLE_SEP_L4);
        // copy start position
        contigData[i][4][j][0] = parseInt(elem[0]);
        // copy colspan
        contigData[i][4][j][1] = parseInt(elem[1]);
        // copy element data
        contigData[i][4][j][2] = elem[2];
      }
    }
  }
}
////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
