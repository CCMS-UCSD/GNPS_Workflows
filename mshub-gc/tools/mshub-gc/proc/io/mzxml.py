"""
************************************************************
mzXML module
************************************************************

Module to load mzXML files

"""

#import xmltodict
import os
#import base64
import binascii
import struct
import zlib

class Spectrum(object):
    def __init__(self, peaks, scan, mz, charge, mslevel, parentscan=0, precursor_intensity=0, retention_time=0, collision_energy=0):
        self.peaks = peaks
        self.filename = ""
        self.scan = scan
        self.mz = mz
        self.charge = charge
        self.mslevel = mslevel
        self.parentscan = parentscan
        self.precursor_intensity = precursor_intensity
        self.retention_time = retention_time
        self.collision_energy = collision_energy

"""Load Entire mzXML file"""
def load_mzxml_file(filename, drop_ms1=False):
    output_ms1 = []
    output_ms2 = []

    struct_iter_ok = True
    canary = True

    with open(filename) as fd:
        mzxml = None#xmltodict.parse(fd.read())
        #mzxml = xmltodict.parse(fd.read())
        read_scans = mzxml['mzXML']['msRun']['scan']
        filename_output = os.path.split(filename)[1]
        index = 1
        for scan in read_scans:
            # print(scan)
            ms_level, spectrum, struct_iter_ok, canary = read_mzxml_scan(scan, index, filename_output, struct_iter_ok, canary, drop_ms1)
            index += 1
            if ms_level == 1:
                if drop_ms1 == False:
                    output_ms1.append(spectrum)
            if ms_level >= 2:
                output_ms2.append(spectrum)
            nested_scans = scan.get('scan',[])
            if not isinstance(nested_scans,list):
                nested_scans = [nested_scans]
            for nested_scan in nested_scans:
                ms_level, spectrum, struct_iter_ok, canary = read_mzxml_scan(nested_scan, index, filename_output, struct_iter_ok, canary, drop_ms1)
                index += 1
                output_ms2.append(spectrum)
    return output_ms1 + output_ms2

"""Read Single Scan"""
def read_mzxml_scan(scan, index, filename_output, struct_iter_ok, canary, drop_ms1):
    ms_level = int(scan['@msLevel'])
    retention_time_string = scan['@retentionTime']
    retention_time_string = retention_time_string.replace("PT", "")
    retention_time = 0.0
    if retention_time_string[-1] == "S":
        retention_time = float(retention_time_string[:-1])

    if drop_ms1 == True and ms_level == 1:
        return ms_level, None, struct_iter_ok, canary

    scan_number = int(scan['@num'])
    collision_energy = 0.0
    fragmentation_method = "NO_FRAG"

    try:
        collision_energy = float(scan['@collisionEnergy'])
    except KeyboardInterrupt:
        raise
    except:
        collision_energy = 0.0

    #Optional fields
    #base_peak_intensity = 0.0
    #base_peak_mz = 0.0
    base_peak_intensity = float(scan.get('@basePeakIntensity', 0.0))
    base_peak_mz = float(scan.get('@basePeakMz', 0.0))

    try:
        precursor_mz_tag = scan['precursorMz']
        precursor_mz = float(precursor_mz_tag['#text'])
        precursor_scan = int(precursor_mz_tag.get('@precursorScanNum', 0))
        precursor_charge = int(precursor_mz_tag.get('@precursorCharge', 0))
        precursor_intensity = float(precursor_mz_tag.get('@precursorIntensity', 0))

        try:
            fragmentation_method = precursor_mz_tag['@activationMethod']
        except KeyboardInterrupt:
            raise
        except:
            fragmentation_method = "NO_FRAG"

    except KeyboardInterrupt:
        raise
    except:
        if ms_level == 2:
            print("No PrecursorMZ")
            precursor_mz = 0
            precursor_scan = 0
            precursor_charge = 0
            precursor_intensity = 0
        #    raise


    peaks_precision = float(scan['peaks'].get('@precision', '32'))
    peaks_compression = scan['peaks'].get('@compressionType', 'none')
    peak_string = scan['peaks'].get('#text', '')
    if canary and peak_string != '':
        try:
            decode_spectrum(peak_string, peaks_precision, peaks_compression, struct_iter_ok)
        except:
            struct_iter_ok = False
        canary = False
    if peak_string != '':
        peaks = decode_spectrum(peak_string, peaks_precision, peaks_compression, struct_iter_ok)
    else:
        peaks = []
    if ms_level == 1:
        output = Spectrum(peaks, scan_number, 0, 0, ms_level, retention_time=retention_time)
    if ms_level >= 2:
        output = Spectrum(peaks, scan_number, precursor_mz, precursor_charge, ms_level, precursor_intensity=precursor_intensity, parentscan=precursor_scan, retention_time=retention_time, collision_energy=collision_energy)
    return ms_level, output, struct_iter_ok, canary

"""Decode peaks for mzXML"""
def decode_spectrum(line, peaks_precision, peaks_compression, struct_iter_ok):

    """https://groups.google.com/forum/#!topic/spctools-discuss/qK_QThoEzeQ"""

    decoded = binascii.a2b_base64(line)
    number_of_peaks = 0
    unpack_format1 = ""


    if peaks_compression == "zlib":
        decoded = zlib.decompress(decoded)

    #Assuming no compression
    if peaks_precision == 32:
        number_of_peaks = len(decoded)/4
        unpack_format1 = ">%df" % number_of_peaks
    else:
        number_of_peaks = len(decoded)/8
        unpack_format1 = ">%dd" % number_of_peaks

    peaks = [
       pair for pair in zip(*[iter(struct.unpack(unpack_format1,decoded))] * 2)
    ]
    return peaks
