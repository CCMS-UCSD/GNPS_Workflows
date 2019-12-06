import sys
sys.path.insert(0, "../tools/molecularsearch-gc/")



def test_kovats():
    import calculate_kovats
    input_markerfile = "reference_data/kovats/carbonmarkerfile.csv"
    input_identificationsfile = "reference_data/kovats/input_ids.tsv"
    calculate_kovats.calculate_kovats(input_identificationsfile, input_markerfile, "output_ids_with_kovats.tsv")
