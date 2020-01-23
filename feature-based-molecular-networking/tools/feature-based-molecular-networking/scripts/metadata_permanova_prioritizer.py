import numpy as np
import pandas as pd
from collections import Counter

###function takes in a .tsv metadata file and returns columns appropriate for PERMANOVA analysis
def permanova_validation(input_file):
    metadata = pd.read_csv(input_file, sep = "\t")
    columns_to_PERMANOVA = []
    
    for column in metadata:
       #writing the column into a list    
        templist = metadata[column].tolist()
        number_of_labels = len(templist)
        max_number_of_labels = float(number_of_labels) / 5.0
        min_number_of_labels = 2

        unique_labels = len(set(templist))
        if unique_labels > max_number_of_labels or unique_labels < min_number_of_labels:
            continue
        else:
            columns_to_PERMANOVA.append(column)

    return(columns_to_PERMANOVA)
