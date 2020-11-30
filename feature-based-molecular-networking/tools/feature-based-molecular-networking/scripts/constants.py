# constants for....

# edges
class EDGE:
    TYPE_ATTRIBUTE = "EdgeType"
    ION_TYPE = "MS1 annotation"  # ion identity molecular networking IIMN
    COSINE_TYPE = "Cosine"  # molecular networking edge
    # list of all types
    TYPES = [ION_TYPE, COSINE_TYPE]


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