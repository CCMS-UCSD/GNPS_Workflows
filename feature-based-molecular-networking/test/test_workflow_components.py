import sys
sys.path.insert(0, "../tools/feature-based-molecular-networking/scripts/")


def test_written_description():
    import write_description
    input_xml = "reference_data/params.xml"
    write_description.write_description(input_xml, "/dev/null")
