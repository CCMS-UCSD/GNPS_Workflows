# constants for....

# edges
class EDGE:
    TYPE_ATTRIBUTE = "EdgeType"
    ION_TYPE = "MS1 annotation"  # ion identity molecular networking IIMN
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
    ION_NETWORK_ID_ATTRIBUTE = "Annotated Adduct Features ID"
    ABUNDANCE_ATTRIBUTE = "sum(precursor intensity)"
    ADDUCT_ATTRIBUTE = "Best Ion"
    # new attribute for collapsed ion identity molecular networks (IIMN)
    SUM_ION_INTENSITY_ATTRIBUTE = "sum ion intensity (collapsed nodes)"
    # number of nodes that were collapsed into this single node
    COLLAPSED_NODES_ATTRIBUTE = "# collapsed ion nodes"

    # add columns for each adduct_intensity that was merged into a collapsed node
    # [M+H]+_Intensity ...
    SPECIFIC_ION_ABUNDANCE_ATTRIBUTE = "_INTENSITY"