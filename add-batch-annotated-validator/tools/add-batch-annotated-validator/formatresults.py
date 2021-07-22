import argparse
parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('input_annotation')
parser.add_argument('new_result')
parser.add_argument('output_formatted_result')

args = parser.parse_args()

print(args)