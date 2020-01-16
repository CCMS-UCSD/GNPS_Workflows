import sys
sys.path.insert(0, "../tools/mshub-gc/")

def test_conversion():
    import create_quantification
    create_quantification.convert_quantification("data/data_integrals.csv", "data/params.xml", "data/feature_table.csv")

def test_mgf_conversion():
    import process_gc
    process_gc.parse_peaks_for_output("data/data_ms_peaks.txt", "data/specs_ms.mgf")
    