import pandas as pd
import argparse

def main():
    parser = argparse.ArgumentParser(description='wrapper')
    parser.add_argument('DB_result', help='input')
    parser.add_argument('DB_result_filtered', help='input')
    parser.add_argument('Kovats_Result_Nonfiltered', help='input_filtered')
    parser.add_argument('Kovats_Result_Filtered', help='workflow_parameters')
    parser.add_argument('workflowParameters', help='Carbon_Marker_File')
    parser.add_argument('quantTable', help='Kovats_Result_Nonfiltered')

    parser.add_argument('DB_result_mshub', help='Kovats_Result_Nonfiltered')
    parser.add_argument('DB_result_filtered_mshub', help='Kovats_Result_Nonfiltered')
    parser.add_argument('Kovats_Result_Nonfiltered_mshub', help='Kovats_Result_Nonfiltered')
    parser.add_argument('Kovats_Result_Filtered_mshub', help='Kovats_Result_Nonfiltered')


    args = parser.parse_args()
    mapping =  {args.DB_result:args.DB_result_mshub,\
                args.DB_result_filtered:args.DB_result_filtered_mshub,\
                args.Kovats_Result_Filtered: args.Kovats_Result_Filtered_mshub,\
                args.Kovats_Result_Nonfiltered: args.Kovats_Result_Nonfiltered_mshub}
    for k,v in mapping.items():
        original_file = pd.read_csv(k,sep='\t')
        print(original_file)
        original_file["Balance_score(percentage)"] = ""
        if not args.quantTable:
            original_file.to_csv(v,sep='\t')
            continue
        quantTable = pd.read_csv(args.quantTable)
        print(quantTable)
        for idx, row in original_file.iterrows():
            #print(row["#Scan#"],quantTable[str(row["#Scan#"])][0].split("(")[-1].split(")")[0])
            try:
                print("quantTable")
                print(quantTable[str(row["#Scan#"])][0])
                original_file.loc[idx,"Balance_score(percentage)"] = quantTable[str(row["#Scan#"])][0].split("(")[-1].split("%")[0]
            except:
                continue
        print(original_file)
        original_file.to_csv(v,sep='\t')
if __name__ == "__main__":
    main()
