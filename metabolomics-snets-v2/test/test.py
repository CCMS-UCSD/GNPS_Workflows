import requests
import sys
sys.path.insert(0, "../tools/metabolomicsnetsv2/scripts")
import format_metadata
def test():
    format_metadata.process("test_data/sheets_integration/params.xml", "/dev/null", ".")
    