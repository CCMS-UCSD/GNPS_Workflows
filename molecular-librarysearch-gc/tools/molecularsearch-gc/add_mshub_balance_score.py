import pandas as pd
import argparse
import glob
import os

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
    parser.add_argument('library_identifications', help='input')
    parser.add_argument('mshub_balance_scores', help='mshub_balance_scores')
    parser.add_argument('library_identifications_with_balance', help='library_identifications_with_balance')

    args = parser.parse_args()

    quant_table_df = None

    quant_files_list = glob.glob(os.path.join(args.mshub_balance_scores, "*"))

    if len(quant_files_list) == 1:
        quant_table_df = pd.read_csv(quant_files_list[0], skiprows=[0, 2, 3])

    propogate_balance_score(args.library_identifications, args.library_identifications_with_balance, quant_table_df)

if __name__ == "__main__":
    main()
