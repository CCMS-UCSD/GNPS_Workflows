# constants for....

# edges
class EDGE:
    TYPE_ATTRIBUTE = "EdgeType"
    ION_TYPE = "MS1 annotation"  # ion identity molecular networking IIMN (MZmine and XCMS/CAMERA)
    ION_MS_DIAL_TYPE = "Adduct annotation"  # ion identity molecular networking IIMN (MS-DIAL)
    COSINE_TYPE = "Cosine"  # molecular networking edge
    # list of all types
    TYPES = [ION_TYPE, COSINE_TYPE]

    SCORE_ATTRIBUTE = "EdgeScore"  # score for all edge types (cosine, ion identity, ..)
    NODE1_ATTRIBUTE = "node1"  #
    NODE2_ATTRIBUTE = "node2"  #
    MASS_DIFF_ATTRIBUTE = "mass_difference"  #
    ANNOTATION_ATTRIBUTE = "EdgeAnnotation"  # edge annotation for all edge types
    EXPLAINED_INTENSITY_ATTRIBUTE = "explained_intensity"  # explained intensity between the two MS2 spectra from MN
    COMPONENT_ATTRIBUTE = "component"  #
    COSINE_SCORE_ATTRIBUTE = "cosine_score"  # only for molecular networking - rather use SCORE_ATTRIBUTE

class NODE:
    # the node type
    TYPE_ATTRIBUTE = "NODE_TYPE"
    # values
    MSCLUSTER_TYPE = "MSCluster Node"  # classical MN
    FEATURE_TYPE = "Feature Node"  # feature based MN
    ION_TYPE = "Ion Identity Node"  # ion identity molecular networking (IIMN)
    COLLAPSED_TYPE = "Collapsed Ion Network Node"  # collapsed node based on IIMN
    # list of all types
    TYPES = [MSCLUSTER_TYPE, FEATURE_TYPE, ION_TYPE, COLLAPSED_TYPE]

    # node attributes and values
    ABUNDANCE_ATTRIBUTE = "sum(precursor intensity)"
    NETWORK_URL_ATTRIBUTE = "GNPSLinkout_Network"
    CLUSTER_URL_ATTRIBUTE = "GNPSLinkout_Cluster"
    PROTEOSAFE_CLUSTER_URL_ATTRIBUTE = "ProteoSAFeClusterLink"
    CHARGE_ATTRIBUTE = "charge"
    PARENT_MASS_ATTRIBUTE = "parent mass"
    NUMBER_OF_SPECTRA_ATTRIBUTE = "number of spectra"
    CLUSTER_INDEX_ATTRIBUTE = "cluster index"
    RT_MEAN_ATTRIBUTE = "RTMean"  # retention time
    RT_CONSENSUS_ATTRIBUTE = "RTConsensus"
    ALL_GROUPS_ATTRIBUTE = "AllGroups"
    DEFAULT_GROUPS_ATTRIBUTE = "DefaultGroups"
    UNIQUE_FILE_SOURCE_ATTRIBUTE = "UniqueFileSources"
    COMPONENT_INDEX_ATTRIBUTE = "componentindex"
    G1_ATTRIBUTE = "G1"
    G2_ATTRIBUTE = "G2"
    G3_ATTRIBUTE = "G3"
    G4_ATTRIBUTE = "G4"
    G5_ATTRIBUTE = "G5"
    G6_ATTRIBUTE = "G6"
    METADATA_GROUP_PREFIX_ATTRIBUTE = "GNPSGROUP:"  # e.g., GNPSGROUP:BLANK, GNPSGROUP:CASE (from metadata file)

    # Library match specific
    ADDUCT_LIB_ATTRIBUTE = "Adduct"
    COMPOUND_NAME_LIB_ATTRIBUTE = "Compound_Name"
    INCHI_LIB_ATTRIBUTE = "INCHI"
    SMILES_LIB_ATTRIBUTE = "Smiles"
    SCORE_LIB_ATTRIBUTE = "MQScore"
    MASSDIFF_LIB_ATTRIBUTE = "MassDiff"
    MZ_ERROR_PPM_LIB_ATTRIBUTE = "MZErrorPPM"
    SHARED_PEAKS_LIB_ATTRIBUTE = "SharedPeaks"
    TAGS_LIB_ATTRIBUTE = "tags"
    LIBRARY_CLASS_LIB_ATTRIBUTE = "Library_Class"
    INSTRUMENT_LIB_ATTRIBUTE = "Instrument"
    ION_MODE_LIB_ATTRIBUTE = "IonMode"
    ION_SOURCE_LIB_ATTRIBUTE = "Ion_Source"
    PI_LIB_ATTRIBUTE = "PI"
    DATA_COLLECTOR_LIB_ATTRIBUTE = "Data_Collector"
    COMPOUND_SOURCE_LIB_ATTRIBUTE = "Compound_Source"
    SPECTRUM_ID_LIB_ATTRIBUTE = "SpectrumID"
    URL_LIB_ATTRIBUTE = "GNPSLibraryURL"

    # ion identity specific
    CORRELATION_GROUP_ID_ATTRIBUTE = "Correlated Features Group ID"  # feature correlation group
    ION_NETWORK_ID_ATTRIBUTE = "Annotated Adduct Features ID"  # ion identity network id
    IIN_ADDUCT_ATTRIBUTE = "Best Ion"  # ion identity
    IIN_ADDUCT_EQUALS_LIB_ATTRIBUTE = "IIN Best Ion=Library Adduct"
    IIN_NEUTRAL_MASS_ATTRIBUTE = "neutral M mass"  # ion identity
    IIN_MSMS_VERIFICATION_ATTRIBUTE = "MS2 Verification Comment"  # verification of ion identity by MS2
    # new attribute for collapsed ion identity molecular networks (IIMN)
    SUM_ION_INTENSITY_ATTRIBUTE = "sum ion intensity (collapsed nodes)"
    # lists all library matches
    COLLAPSED_LIST_LIB_MATCH_ATTRIBUTE = "Library Match Summary (collapsed)"
    # number of nodes that were collapsed into this single node
    COLLAPSED_NODES_ATTRIBUTE = "# collapsed ion nodes"

    # add columns for each adduct_intensity that was merged into a collapsed node
    # [M+H]+_Intensity ...
    SPECIFIC_ION_ABUNDANCE_ATTRIBUTE = "_INTENSITY"