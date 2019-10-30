import sys
sys.path.insert(0, "../tools/mshub-gc/")

def test_conversion():
    import create_quantification
    create_quantification.convert_quantification("data/data_integrals.csv", "/dev/null")