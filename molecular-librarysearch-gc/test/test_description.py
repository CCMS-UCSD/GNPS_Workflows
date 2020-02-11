import sys
sys.path.insert(0, "../tools/molecularsearch-gc/")


def test_written_description():
    import write_description
    input_filename = "reference_data/params.xml"
    write_description.write_description(input_filename, "/dev/null")
