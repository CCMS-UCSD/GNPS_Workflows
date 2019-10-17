import pandas as pd
import argparse

def propogate_balance_score(input_file, output_file, quant_table_df):
    original_file_df = pd.read_csv(input_file,sep='\t')   

    if quant_table_df is None:
        original_file_df.to_csv(output_file,sep='\t', index=False)
        return

    scan_to_balance = {}
    for i, key in enumerate(quant_table_df.keys()):
        if "RTS:" in key:
            continue

        try:
            balance_score = key.split("(")[-1].split("%")[0]
            rt = key.split(" ")[0]
            scan_to_balance[i] = balance_score
        except:
            raise
            continue

    for idx, row in original_file_df.iterrows():
        scan = int(row["#Scan#"])
        if scan in scan_to_balance:
            original_file_df.loc[idx,"Balance_score(percentage)"] = scan_to_balance[scan]
        else:
            original_file_df.loc[idx,"Balance_score(percentage)"] = ""

    original_file_df.to_csv(output_file,sep='\t', index=False)

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

    quant_table_df = None
    if args.quantTable != None:
        quant_table_df = pd.read_csv(args.quantTable, skiprows=[0, 2, 3])

    propogate_balance_score(args.DB_result, args.DB_result_mshub, quant_table_df)
    propogate_balance_score(args.DB_result_filtered, args.DB_result_filtered_mshub, quant_table_df)
    propogate_balance_score(args.Kovats_Result_Filtered, args.Kovats_Result_Filtered_mshub, quant_table_df)
    propogate_balance_score(args.Kovats_Result_Nonfiltered, args.Kovats_Result_Nonfiltered_mshub, quant_table_df)

if __name__ == "__main__":
    main()
