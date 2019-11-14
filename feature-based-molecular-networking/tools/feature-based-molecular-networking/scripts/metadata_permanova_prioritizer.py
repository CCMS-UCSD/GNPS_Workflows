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

        #each label need to make up more than 10% of the population
        lowest_num_labels_allowed = number_of_labels * 0.1
        #counting the occurance of each label within a column 
        count_dictionary = Counter(templist)
                
        #iterating over looking to see if any category is under the limit
        for key,value in count_dictionary.items():
            #on the condition a label in ever under-represented
            if value < lowest_num_labels_allowed:
                break
                
        #should this loop never break, we accept this column for PERMANOVA
        else:
            columns_to_PERMANOVA.append(column)

    return(columns_to_PERMANOVA)
