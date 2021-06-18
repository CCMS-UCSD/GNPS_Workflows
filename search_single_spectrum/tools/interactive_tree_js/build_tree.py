import sys
import argparse
import logging

import bundle_to_html
import json_ontology_extender

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def create_tree_html(in_html, in_ontology, in_data, out_json_tree, format_out_json, out_html, compress_out_html,
                     node_key, data_key):
    """
    Merges extra data into an ontology and creates a single distributable html file. Compression reduces the size of
    the html file.

    :param in_html: the base html file with different dependencies
    :param in_ontology: the input ontology
    :param in_data: extra data (in tab-separated tsv) is merged into the ontology
    :param out_json_tree: the merged tree data is exported to a json file
    :param out_html: the final distributable html file, merged with all dependencies
    :param compress_out_html: apply compression (reduces readability)
    """
    json_ontology_extender.add_data_to_ontology_file(out_json_tree, in_ontology, in_data, node_key, data_key,
                                                     format_out_json)
    bundle_to_html.build_dist_html(in_html, out_html, out_json_tree, compress_out_html)


if __name__ == '__main__':
    # parsing the arguments (all optional)
    parser = argparse.ArgumentParser(description='Create tree data by merging extra data into an ontology. Then '
                                                 'create a distributable html file that internalizes all scripts, '
                                                 'data, etc. ')
    parser.add_argument('--in_html', type=str, help='The input html file',
                        default="collapsible_tree_v3.html")
    parser.add_argument('--ontology', type=str, help='the json ontology file with children',
                        default="../data/GFOP.json")
    parser.add_argument('--in_data', type=str, help='a tab separated file with additional data that is added to the '
                                                    'ontology', default="../examples/caffeic_acid.tsv")
    parser.add_argument('--out_html', type=str, help='output html file', default="dist/oneindex.html")
    parser.add_argument('--compress', type=bool, help='Compress output file (needs minify_html)',
                        default=True)
    parser.add_argument('--out_tree', type=str, help='output file', default="dist/merged_ontology_data.json")
    parser.add_argument('--format', type=bool, help='Format the json output False or True',
                        default=True)
    parser.add_argument('--node_key', type=str, help='the field in the ontology to be compare to the field in the '
                                                     'data file', default="name")
    parser.add_argument('--data_key', type=str,
                        help='the field in the data file to be compared to the field in the ontology',
                        default="group_value")
    args = parser.parse_args()

    # is a url - try to download file
    # something like https://raw.githubusercontent.com/robinschmid/GFOPontology/master/data/GFOP.owl
    # important use raw file on github!
    try:
        create_tree_html(args.in_html, args.ontology, args.in_data, args.out_tree, args.format, args.out_html,
                         args.compress, args.node_key, args.data_key)
    except Exception as e:
        # exit with error
        logger.exception(e)
        sys.exit(1)

    # exit with OK
    sys.exit(0)
