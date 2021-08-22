from pathlib import Path
import xmltodict
import argparse
from csv import DictReader
from collections import defaultdict
import sys
import shutil

def arguments():
    parser = argparse.ArgumentParser(description='Demangle collection as aliases to folder')
    parser.add_argument('-p','--params', type = Path, help='ProteoSAFe params.xml')
    parser.add_argument('-i','--input_folder', type = Path, help='Input folder path')
    parser.add_argument('-m','--input_mangled_prefix', type = str, help='Mangled prefix for input')
    parser.add_argument('-o','--output_folder', type = Path, help='Output folder path')
    parser.add_argument('-l','--output_list', type = Path, help='Output list of paths')
    parser.add_argument('-r','--reverse', dest='reverse', action='store_true', help='Flag to demangle file collection')
    parser.add_argument('-s','--preserve_suffix', dest='preserve_suffix', action='store_true', help='Flag to save suffix from demangled file collection')
    parser.add_argument('-c','--copy', dest='copy', action='store_true', help='Flag to copy files into destination instead of symlink them')
    return parser.parse_args()

def read_params(input_file, mangled_prefix):
    return get_mangled_file_mapping(parse_xml_file(input_file),mangled_prefix)

def get_mangled_file_mapping(params, mangled_prefix):
    all_mappings = params["upload_file_mapping"]
    mangled_mapping = {}
    demangled_mapping = {}
    for mapping in all_mappings:
        splits = mapping.split("|")
        mangled_name = splits[0]
        original_name = splits[1]
        if mangled_prefix in mangled_name:
            mangled_mapping[mangled_name] = Path(original_name)
            demangled_mapping[original_name] = Path(mangled_name)
    return mangled_mapping, demangled_mapping

def parse_xml_file(input_file):
    with open(input_file) as f:
        key_value_pairs = defaultdict(list)
        xml_obj = xmltodict.parse(f.read())

        #print(json.dumps(xml_obj["parameters"]))
        for parameter in xml_obj["parameters"]["parameter"]:
            name = parameter["@name"]
            value = parameter["#text"]
            key_value_pairs[name].append(value)

    return key_value_pairs

def main():

    # don't fail on error, since it is likely to be run without inputs
    args = arguments()

    if not (args.input_folder and args.output_folder and args.params and args.input_mangled_prefix):
        print("Input folder, output folder, params, and collection prefix are required.")
        sys.exit(0)
    mangled_mapping, demangled_mapping = read_params(args.params, args.input_mangled_prefix)
    output_list = None

    if args.output_list:
        output_list = open(args.output_list, 'w')

    for input_file in args.input_folder.rglob('*'):

        if input_file.is_file():

            input_path = args.input_folder.joinpath('/'.join(input_file.parts[1:])).absolute()

            if args.reverse:
                if args.preserve_suffix:
                    suffix = input_file.suffix
                    input_file_str_no_suffix = '/'.join(input_file.with_suffix('').parts[1:])
                    output_file = demangled_mapping.get(input_file_str_no_suffix).with_suffix(suffix)
                else:
                    output_file = demangled_mapping.get('/'.join(input_file.parts[1:]))
            else:
                output_file = mangled_mapping.get(input_file.name)

            output_path = args.output_folder.joinpath(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            if not args.copy:
                output_path.symlink_to(input_path)
            else:
                shutil.copyfile(input_path, output_path)

            if output_list:
                output_list.write('{}\n'.format(output_path))

    if output_list:
        output_list.close()

if __name__ == "__main__":
    main()