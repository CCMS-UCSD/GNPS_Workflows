import requests


def test_massive_apis():
    url = "https://massive.ucsd.edu/ProteoSAFe//proxi/v0.1/datasets?filter=MSV000084741&function=datasets"

    r = requests.get(url)
    r.raise_for_status()