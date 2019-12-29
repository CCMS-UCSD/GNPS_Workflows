from nose2.tools import params
import requests
import json
import zipfile
import os

@params("gnps.ucsd.edu", "proteomics3.ucsd.edu")
def test_continuous_id(server_url):
    url = "https://{}/ProteoSAFe/ContinuousIDServlet?task=ee21d1b9bca04a908d231e4048e6a14a".format(server_url)
    data = requests.get(url)
    continuous_id_object = json.loads(data.text)
    jobs = continuous_id_object["jobs"]

    assert(len(jobs) > 10)

    #Testing a specific continuosu ID
    url = "https://gnps.ucsd.edu/ProteoSAFe/result_json.jsp?task=e00e4bc53e8240389deaa68596ca8eaa&view=group_by_spectrum_all_beta"
    data = requests.get(url)
    all_identifications_list = json.loads(data.text)["blockData"]

    assert(len(all_identifications_list) > 50)


@params("gnps.ucsd.edu", "proteomics3.ucsd.edu")
def test_datasets(server_url):
    url = "https://{}/ProteoSAFe/datasets_json.jsp".format(server_url)
    data = requests.get(url)
    datasets = json.loads(data.text)
    datasets_list = datasets["datasets"]

    assert(len(datasets_list) > 500)

    #testing to make sure the massive servlet works for all GNPS datasets
    for dataset in datasets_list:
        if "GNPS" in dataset["title"].upper():
            task_id = dataset["task"]

            #print(dataset["title"].encode(encoding="ascii", errors="ignore"))
            url = "https://{}/ProteoSAFe/MassiveServlet?task={}&function=massiveinformation&_=1563563757014".format(server_url, task_id)
            r = requests.get(url)
            try:
                r.raise_for_status()
            except KeyboardInterrupt:
                raise
            except:
                print(url)
                raise


@params("gnps.ucsd.edu", "proteomics3.ucsd.edu")
def test_direct_network_download(server_url):
    test_urls = []
    test_urls.append("https://{}/ProteoSAFe/DownloadResultFile?task=3fdc6adc5c104652a78caf70d513c8c3&block=main&file=output_graphml/".format(server_url))
    test_urls.append("https://{}/ProteoSAFe/DownloadResultFile?task=047ef85223024f269e44492adc771d9c&block=main&file=gnps_molecular_network_graphml/".format(server_url))

    for url in test_urls:
        print(url)
        data = requests.get(url)
        assert(len(data.text) > 50000)


@params("gnps.ucsd.edu", "proteomics3.ucsd.edu")
def test_download_result_zip(server_url):
    task_id = "047ef85223024f269e44492adc771d9c"
    url_to_zip = "https://{}/ProteoSAFe/DownloadResult?task={}&show=true&view=download_cytoscape_data".format(server_url, task_id)
    r = requests.post(url_to_zip)

    zip_filename = os.path.join(".", "%s.zip" % (task_id))
    local_file = open(zip_filename, "wb")
    local_file.write(r.content)
    local_file.close()

    from zipfile import ZipFile
    with ZipFile(zip_filename, 'r') as zipObj:
        listOfFileNames = zipObj.namelist()
        assert(len(listOfFileNames) >= 5)

    os.remove(zip_filename)

@params("gnps.ucsd.edu", "proteomics3.ucsd.edu")
def test_gnps_library(server_url):
    import utils

    url = "https://{}/ProteoSAFe/gnpslibrary.jsp?library=GNPS-LIBRARY&test=true".format(server_url)
    r = requests.get(url)
    assert(len(r.text) > 20000)

    url = "https://{}/ProteoSAFe/SpectrumCommentServlet?SpectrumID=CCMSLIB00000001547".format(server_url)
    utils.test_load_time(url, 20000)
    
    url = "https://{}/ProteoSAFe/static/gnps-splash.jsp?test=true".format(server_url)
    utils.test_load_time(url, 20000)

    url = "https://{}/ProteoSAFe/gnpslibrary.jsp?library=GNPS-LIBRARY&test=true#%7B%22Library_Class_input%22%3A%221%7C%7C2%7C%7C3%7C%7CEXACT%22%7D".format(server_url)
    utils.test_load_time(url, 20000)

    url = "https://{}/ProteoSAFe/ContinuousIDRatingSummaryServlet?spectrum_id=CCMSLIB00000006885&summary_type=per_spectrum".format(server_url)
    data = requests.get(url)
    ratings_list = json.loads(data.text)["ratings"]
    assert(len(ratings_list) > 1)

    url = "https://{}/ProteoSAFe/ContinuousIDRatingSummaryServlet?dataset_id=MSV000078547&summary_type=per_dataset".format(server_url)
    data =  .get(url)
    ratings_list = json.loads(data.text)["ratings"]
    assert(len(ratings_list) > 1)

def test_gnps_library_provenance():
    import urllib.request

    url = "ftp://ccms-ftp.ucsd.edu/GNPS_Library_Provenance/47daa4396adb426eaa5fa54b6ce7dd5f/130618_Ger_Jenia_WT-3-Des-MCLR_MH981.4-qb.1.1..mgf"
    print(url)
    response = urllib.request.urlopen(url)
    html = response.read()
    assert(len(html) == 4615)
    

@params("gnps.ucsd.edu", "proteomics3.ucsd.edu")
def test_gnps_network_views(server_url):
    url = "https://{}/ProteoSAFe/result_json.jsp?task=d0e3af94f33f47acad56560de0c5a846&view=view_all_annotations_DB".format(server_url)
    data = requests.get(url)
    identication_data = json.loads(data.text)["blockData"]
    assert(len(identication_data) == 204)

    url = "https://{}/ProteoSAFe/result_json.jsp?task=d0e3af94f33f47acad56560de0c5a846&view=view_all_clusters_withID_beta".format(server_url)
    data = requests.get(url)
    clusters_object = json.loads(data.text)
    data = clusters_object["blockData"]
    assert(len(data) == 1373)
    
@params("gnps.ucsd.edu", "proteomics3.ucsd.edu")
def test_gnps_molecule_explorer(server_url):
    url = "https://{}/ProteoSAFe/result_json.jsp?task=698fc5a09db74c7492983b3673ff5bf6&view=view_aggregate_molecule_dataset".format(server_url)
    data = requests.get(url)
    clusters_object = json.loads(data.text)
    data = clusters_object["blockData"]
    assert(len(data) > 1000)


    url = "https://{}/ProteoSAFe/result_json.jsp?task=698fc5a09db74c7492983b3673ff5bf6&view=view_aggregate_dataset_network".format(server_url)
    data = requests.get(url)
    datasets = json.loads(data.text)
    dataset_network = datasets["blockData"]
    assert(len(dataset_network) > 500)
    