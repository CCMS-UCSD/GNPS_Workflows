#!/usr/bin/python


import sys
import getopt
import os
import ming_proteosafe_library
import ming_fileio_library
import molecular_network_library

def usage():
    print("<param xml> <input clusterinfo file> <input usable cluster info summary file> <output ili filename>")

def load_filename_to_coordinate_mapping(metadata_file):
    filename_map = {}

    line_counts, table_data = ming_fileio_library.parse_table_with_headers(metadata_file)

    if not("COORDINATE_X" in table_data and "COORDINATE_Y" in table_data and "COORDINATE_Z" in table_data):
        print("COORDINATE_X, COORDINATE_Y, COORDINATE_Z not present in metadata file for ili")
        exit(1)

    for i in range(line_counts):
        filename = table_data["filename"][i].rstrip()
        x = table_data["COORDINATE_X"][i].rstrip()
        y = table_data["COORDINATE_Y"][i].rstrip()
        z = table_data["COORDINATE_Z"][i].rstrip()
        radius = "0.25"
        if "COORDINATE_radius" in table_data:
            radius = table_data["COORDINATE_radius"][i].rstrip()

        if len(x) < 1:
            continue

        coordinate_object = {}
        coordinate_object["x"] = x
        coordinate_object["y"] = y
        coordinate_object["z"] = z
        coordinate_object["radius"] = radius

        filename_map[filename] = coordinate_object

    return filename_map



def create_ili_output_from_clusterinfo(cluster_info_filename, param_filename, clusterinfosummary_filename, filename_coordinate_mapping, output_filename):
    output_file = open(output_filename, "w")
    test_network = molecular_network_library.MolecularNetwork()
    test_network.load_clustersummary(clusterinfosummary_filename)
    line_counts, table_data = ming_fileio_library.parse_table_with_headers(cluster_info_filename)
    param_object = ming_proteosafe_library.parse_xml_file(open(param_filename, "r"))
    mangled_mapping = ming_proteosafe_library.get_mangled_file_mapping(param_object)

    cluster_index_to_file_map = {}

    clusters_map = {}
    all_files = {}
    for i in range(line_counts):
        cluster_number = table_data["#ClusterIdx"][i]
        if test_network.get_cluster_index(cluster_number) == None:
            continue

        if not (cluster_number in clusters_map):
            clusters_map[cluster_number] = []
            cluster_index_to_file_map[cluster_number] = {}
            #Adding all file names to mapping
            for mangled_name in mangled_mapping.keys():
                cluster_index_to_file_map[cluster_number][mangled_name] = 0.0

        #print table_data["#Filename"][i].split("/")[1]
        mangled_filename_only = os.path.basename(table_data["#Filename"][i])
        cluster_index_to_file_map[cluster_number][mangled_filename_only] += float(table_data["#PrecIntensity"][i])
        spectrum_info = {"filename":table_data["#Filename"][i], "intensity": table_data["#PrecIntensity"][i]}
        all_files[table_data["#Filename"][i]] = 1
        clusters_map[cluster_number].append(spectrum_info)

    all_headers = ["filename", "X", "Y", "Z", "radius"]
    for cluster_idx in cluster_index_to_file_map:
        all_headers.append(cluster_idx)

    #writing header
    output_file.write(",".join(all_headers) + "\n")

    for sample_name in mangled_mapping:
        if sample_name.find("spec") == -1:
            continue
        real_filename = mangled_mapping[sample_name]

        if not os.path.basename(real_filename) in filename_coordinate_mapping:
            continue

        line_output = [real_filename]
        coordinate_object = filename_coordinate_mapping[os.path.basename(real_filename)]
        line_output.append(coordinate_object["x"])
        line_output.append(coordinate_object["y"])
        line_output.append(coordinate_object["z"])
        line_output.append(coordinate_object["radius"])
        print(line_output, coordinate_object)
        for cluster_idx in cluster_index_to_file_map:
            line_output.append(str(cluster_index_to_file_map[cluster_idx][sample_name]))
        output_file.write(",".join(line_output) + "\n")

    output_file.close()




def main():
    param_filename = sys.argv[1]
    metadata_folder = sys.argv[2]
    input_clusterinfo_file = sys.argv[3]
    input_clusterinfosummary = sys.argv[4]
    ili_stl_model_folder = sys.argv[5]
    output_ili_filename = sys.argv[6]
    view_ili_html_filename = sys.argv[7]

    create_output = True
    param_object = ming_proteosafe_library.parse_xml_file(open(param_filename, "r"))
    try:
        if param_object["CREATE_ILI_OUTPUT"][0] != "1":
            create_output = False
    except:
        create_output = False

    if create_output:
        ili_stl_model_files_in_folder = ming_fileio_library.list_files_in_dir(ili_stl_model_folder)
        metadata_files_in_folder = ming_fileio_library.list_files_in_dir(metadata_folder)
        if len(metadata_files_in_folder) != 1:
            print("Metadata file not provided, cannot create ili compatible output without coordinates")
            exit(1)
        filename_coordinate_mapping = load_filename_to_coordinate_mapping(metadata_files_in_folder[0])
        create_ili_output_from_clusterinfo(input_clusterinfo_file, param_filename, input_clusterinfosummary, filename_coordinate_mapping, output_ili_filename)

        if len(ili_stl_model_files_in_folder) == 1:
            output_ili_html_file = open(view_ili_html_filename, "w")
            output_ili_html_file.write("<script>\n")
            output_ili_html_file.write('window.location.replace("https://ili.embl.de/?https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=ili_stl_model/ili_stl_model-00000.stl;https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=ili_output/ili_quant.csv")\n' % (param_object["task"][0],param_object["task"][0]))
            output_ili_html_file.write("</script>\n")
            output_ili_html_file.close()

        if len(ili_stl_model_files_in_folder) == 0:
            output_ili_html_file = open(view_ili_html_filename, "w")
            output_ili_html_file.write("No STL file uploaded, cannot directly link to ili\n")
            output_ili_html_file.close()

        if len(ili_stl_model_files_in_folder) > 1:
            output_ili_html_file = open(view_ili_html_filename, "w")
            output_ili_html_file.write("Too many stl files uploaded\n")
            output_ili_html_file.close()
    else:
        open(output_ili_filename, "w").write("No Output")
        open(view_ili_html_filename, "w").write("ili output was not selected or no metadata file was provided")



if __name__ == "__main__":
    main()
