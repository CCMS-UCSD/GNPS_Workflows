import sys
import os
import requests

input_filename = sys.argv[1]

print(input_filename)

SERVER_URL = "https://gnps-quickstart.ucsd.edu/validatebatch"
multipart_form_data = {
    'file': (os.path.basename(input_filename), open(input_filename, 'rb'))
}
r = requests.post(SERVER_URL, files=multipart_form_data)
print(r.status_code)
r.raise_for_status()