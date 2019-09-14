#!/usr/bin/python

import re
import ming_numerical_utilities
import xmltodict
import base64
import binascii
import struct
import os
import time
import zlib
import spectrum_alignment

"""

Spectrum Utilities to manipulate and do things with spectra

"""

class MatchingResult:
    def __init__(self, filename, scan, score, mass_error, ppm_error, query_filename, query_scan):
        self.filename = filename
        self.scan = scan
        self.score = score
        self.mass_error = mass_error
        self.ppm_error = ppm_error

        #These are the query spectra, not the reference
        self.query_filename = query_filename
        self.query_scan = query_scan


class SpectrumCollection:
    def __init__(self, filename):
        self.filename = filename
        self.spectrum_list = []
        self.scandict = {}

    def load_from_file(self):
        self.spectrum_list = load_mgf_file(self.filename)

    def load_from_mgf(self):
        self.spectrum_list = load_mgf_file(self.filename)

    def load_from_mzXML(self):
        self.spectrum_list = load_mzxml_file(self.filename)
        file_idx = os.path.split(self.filename)[1]
        #Do indexing on scan number
        for spectrum in self.spectrum_list:
            self.scandict[spectrum.scan] = spectrum
            self.scandict[file_idx + ":" + str(spectrum.scan)] = spectrum

    def search_spectrum(self, otherspectrum, pm_tolerance, peak_tolerance, min_matched_peaks, min_score, top_k=1):
        if len(otherspectrum.peaks) < min_matched_peaks:
            return []

        match_list = []
        for myspectrum in self.spectrum_list:
            if len(myspectrum.peaks) < min_matched_peaks:
                continue
            if abs(myspectrum.mz - otherspectrum.mz) < pm_tolerance:
                score = myspectrum.cosine_spectrum(otherspectrum, peak_tolerance)
                #Also check for min matched peaks
                if score > min_score:
                    match_list.append(MatchingResult(myspectrum.filename, myspectrum.scan, score, 0, 0, otherspectrum.filename, otherspectrum.scan))

        match_list = sorted(match_list, key=lambda score_obj: score_obj.score)

        return match_list[:min(len(match_list), top_k)]

    #updates both the scans and the index
    def make_scans_sequential(self):
        self.scandict = {}
        scan = 1
        for spectrum in self.spectrum_list:
            spectrum.scan = scan
            spectrum.index = scan - 1
            self.scandict[scan] = spectrum
            scan += 1

    #outputs to an MGF and redoes the scan numbering
    def save_to_mgf(self, output_mgf, renumber_scans=True):
        if renumber_scans == True:
            self.make_scans_sequential()
        for spectrum in self.spectrum_list:
            output_mgf.write(spectrum.get_mgf_string() + "\n")

    def save_to_tsv(self, output_tsv_file, mgf_filename="", renumber_scans=True):
        output_tsv_file.write(self.spectrum_list[0].get_tsv_header() + "\n")
        for spectrum in self.spectrum_list:
            output_tsv_file.write(spectrum.get_tsv_line(mgf_filename) + "\n")


class Spectrum:
    def __init__(self, filename, scan, index, peaks, mz, charge, ms_level):
        self.filename = filename
        self.scan = scan
        self.peaks = peaks
        self.mz = mz
        self.charge = charge
        self.index = index
        self.ms_level = ms_level

    def get_mgf_string(self):
        return "PLACE HOLDER"

    def get_mgf_peak_string(self):
        output_string = ""
        for peak in self.peaks:
            output_string += str(peak[0]) + "\t" + str(peak[1]) + "\n"

        return output_string

    @staticmethod
    def get_tsv_header():
        return "filename\tspectrumindex\tspectrumscan\tcharge\tmz"

    def get_max_mass(self):
        max_mass = 0.0
        for peak in self.peaks:
            max_mass = max(max_mass, peak[0])
        return max_mass

    #Straight up cosine between two spectra
    def cosine_spectrum(self, other_spectrum, peak_tolerance):
        total_score, reported_alignments = spectrum_alignment.score_alignment(self.peaks, other_spectrum.peaks, self.mz, other_spectrum.mz, peak_tolerance)
        return total_score

    #def annotate_peaks(self, peak_annotations_list):
    #    for peak_annotation in peak_annotation_list:






class PeptideLibrarySpectrum(Spectrum):
    def __init__(self, filename, scan, index, peaks, mz, charge, peptide, protein):
        Spectrum.__init__(self, filename, scan, index, peaks, mz, charge)
        self.peptide = peptide
        self.protein = protein

    def get_tsv_line(self):
        output_string = self.filename + "\t"
        output_string += str(self.index) + "\t"
        output_string += str(self.scan) + "\t"
        output_string += str(self.charge) + "\t"
        output_string += str(self.mz) + "\t"
        output_string += self.peptide + "\t"
        output_string += self.protein + "\t"

        return output_string

    #Returns the peptide sequence without modifications
    def get_peptide_clean(self):
        return re.sub(r'[^A-Z]', '', self.peptide)

    def get_mgf_string(self):
        output_string = "BEGIN IONS\n"
        output_string += "PEPMASS=" + str(self.mz) + "\n"
        output_string += "CHARGE=" + str(self.charge) + "\n"
        output_string += "MSLEVEL=" + "2" + "\n"
        output_string += "FILENAME=" + self.filename + "\n"
        output_string += "SEQ=" + self.peptide + "\n"
        output_string += "PROTEIN=" + self.protein + "\n"
        output_string += "SCANS=" + str(self.scan) + "\n"
        output_string += "SCAN=" + str(self.scan) + "\n"
        output_string += self.get_mgf_peak_string()
        output_string += "END IONS\n"

        return output_string

    @staticmethod
    def get_tsv_header():
        return "mgf_filename\toriginalfilename\tspectrumindex\tspectrumscan\tcharge\tmz\tpeptide\tprotein"

    def get_tsv_line(self, output_mgf_filename=""):
        return "%s\t%s\t%d\t%d\t%d\t%f\t%s\t%s" % (output_mgf_filename, self.filename, self.index, self.scan, self.charge, self.mz, self.peptide, self.protein)


def load_mgf_peptide_library(filename):
    charge = 0
    mz = 0
    peaks = []
    scan = -1
    peptide = ""
    protein = ""
    spectrum_index = 0

    output_spectra = []

    for line in open(filename, "r"):
        mgf_file_line = line.rstrip()
        if len(mgf_file_line) < 4:
            continue
        if mgf_file_line == "BEGIN IONS":
            charge = 0
            mz = 0
            peaks = []
            scan = -1
            peptide = ""
            protein = ""
            continue

        if mgf_file_line == "END IONS":
            spectrum = Spectrum(filename, scan, spectrum_index, peaks, mz, charge)
            spectrum_index += 1
            lib_spectrum = PeptideLibrarySpectrum(spectrum, peptide, protein)
            output_spectra.append(lib_spectrum)
            print("Spectrum " + str(spectrum_index))
            continue

        if mgf_file_line.find("PEPMASS=") != -1:
            mz = float(mgf_file_line[8:])
            continue
        if mgf_file_line.find("CHARGE=") != -1:
            charge = int(mgf_file_line[7:].replace("+", ""))
            continue
        if mgf_file_line.find("SCANS=") != -1:
            scan = int(mgf_file_line[6:])
            continue

        if mgf_file_line.find("SEQ=") != -1:
            peptide = mgf_file_line[4:]
            continue

        if mgf_file_line.find("PROTEIN=") != -1:
            protein = mgf_file_line[8:]
            continue

        if mgf_file_line.find("=") == -1:
            peak_split = re.split(" |\t", mgf_file_line)
            peaks.append([float(peak_split[0]), float(peak_split[1])])

    return output_spectra





class LibrarySpectrum:
    def __init__(self, spectrum):
        self.spectrum = spectrum
        self.compound_name = ""
        self.adduct = ""
        self.ionmode = ""
        self.collision_energy = "N/A"
        self.CAS = "N/A"
        self.pi = "N/A"
        self.inchi = "N/A"
        self.smiles = "N/A"
        self.instrument = "N/A"
        self.libraryname = "N/A"
        self.libraryquality = "3"
        self.spectrumid = "N/A"
        self.activation = "CID"
        self.ionsource = "LC-ESI"
        self.pubmed = "N/A"
        self.acquisition = "Other"
        self.exactmass = "0.0"
        self.collector = "N/A"

    def get_mgf_string(self):
        output_string = "BEGIN IONS\n"
        output_string += "PEPMASS=" + str(self.spectrum.mz) + "\n"
        output_string += "CHARGE=" + str(self.spectrum.charge) + "\n"
        output_string += "MSLEVEL=" + "2" + "\n"
        output_string += "SOURCE_INSTRUMENT=" + self.instrument + "\n"
        output_string += "FILENAME=" + self.spectrum.filename + "\n"
        output_string += "SEQ=" + "*..*" + "\n"
        output_string += "NOTES=" + "" + "\n"
        output_string += "IONMODE=" + self.ionmode + "\n"
        output_string += "ORGANISM=" + self.libraryname + "\n"
        output_string += "NAME=" + self.compound_name + "\n"
        output_string += "SMILES=" + self.smiles + "\n"
        output_string += "INCHI=" + self.inchi + "\n"
        output_string += "LIBRARYQUALITY=" + self.libraryquality + "\n"
        output_string += "SPECTRUMID=" + self.spectrumid + "\n"
        output_string += "ACTIVATION=" + self.activation + "\n"
        output_string += "INSTRUMENT=" + self.instrument + "\n"
        output_string += "SCANS=" + str(self.spectrum.scan) + "\n"
        output_string += self.spectrum.get_mgf_peak_string()
        output_string += "END IONS\n"

        return output_string

    def get_gnps_library_creation_tsv_string(self, output_filename):
        output_string = output_filename + "\t"
        output_string += "*..*" + "\t"
        output_string += self.compound_name + "\t"
        output_string += str(self.spectrum.mz) + "\t"
        output_string += self.instrument + "\t"
        output_string += self.ionsource + "\t"
        output_string += str(self.spectrum.scan) + "\t"
        output_string += self.smiles + "\t"
        output_string += self.inchi + "\t"
        output_string += "N/A" + "\t"
        output_string += str(self.spectrum.charge) + "\t"
        output_string += self.ionmode + "\t"
        output_string += self.pubmed + "\t"
        output_string += self.acquisition + "\t"
        output_string += self.exactmass + "\t"
        output_string += self.collector + "\t"
        output_string += self.adduct + "\t"
        output_string += "N/A" + "\t"
        output_string += self.libraryquality + "\t"
        output_string += "N/A" + "\t"
        output_string += "N/A" + "\t"
        output_string += "N/A" + "\t"
        output_string += self.CAS + "\t"
        output_string += self.pi + "\t\n"
        return output_string

    @staticmethod
    def get_gnps_library_creation_header():
        output_string = ""
        output_string += "FILENAME" + "\t"
        output_string += "SEQ" + "\t"
        output_string += "COMPOUND_NAME" + "\t"
        output_string += "MOLECULEMASS" + "\t"
        output_string += "INSTRUMENT" + "\t"
        output_string += "IONSOURCE" + "\t"
        output_string += "EXTRACTSCAN" + "\t"
        output_string += "SMILES" + "\t"
        output_string += "INCHI" + "\t"
        output_string += "INCHIAUX" + "\t"
        output_string += "CHARGE" + "\t"
        output_string += "IONMODE" + "\t"
        output_string += "PUBMED" + "\t"
        output_string += "ACQUISITION" + "\t"
        output_string += "EXACTMASS" + "\t"
        output_string += "DATACOLLECTOR" + "\t"
        output_string += "ADDUCT" + "\t"
        output_string += "INTEREST" + "\t"
        output_string += "LIBQUALITY" + "\t"
        output_string += "GENUS" + "\t"
        output_string += "SPECIES" + "\t"
        output_string += "STRAIN" + "\t"
        output_string += "CASNUMBER" + "\t"
        output_string += "PI"
        return output_string


###



###
 # Returns a list of spectrum objects
###
def load_mgf_file(filename):
    charge = 0
    mz = 0
    peaks = []
    scan = 0
    peptide = ""
    protein = ""

    output_spectra = []

    for line in open(filename, "r"):
        mgf_file_line = line.rstrip()
        if len(mgf_file_line) < 4:
            continue
        if mgf_file_line == "BEGIN IONS":
            charge = 0
            mz = 0
            peaks = []
            scan = 0
            peptide = ""
            protein = ""
            continue

        if mgf_file_line == "END IONS":
            output_spectra.append(Spectrum(filename, scan, -1, peaks, mz, charge, 2))
            continue

        if mgf_file_line.find("PEPMASS=") != -1:
            mz = float(mgf_file_line[8:])
            continue
        if mgf_file_line.find("CHARGE=") != -1:
            charge = int(mgf_file_line[7:].replace("+", ""))
            continue
        if mgf_file_line.find("SCANS=") != -1:
            scan = int(mgf_file_line[6:])
            continue

        if mgf_file_line.find("SEQ=") != -1:
            peptide = mgf_file_line[4:]
            continue

        if mgf_file_line.find("PROTEIN=") != -1:
            protein = mgf_file_line[8:]
            continue

        if mgf_file_line.find("=") == -1:
            peak_split = re.split(" |\t", mgf_file_line)
            peaks.append([float(peak_split[0]), float(peak_split[1])])

    return output_spectra

#Decode peaks for mzXML
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

    # peaks = []
    # if struct_iter_ok:
    #     peak_iter = struct.iter_unpack(unpack_format1,decoded)
    #     peaks = [
    #        pair for pair in zip(*[peak_iter] * 2)
    #     ]
    # else:
    peaks = [
       pair for pair in zip(*[iter(struct.unpack(unpack_format1,decoded))] * 2)
    ]
    return peaks
    # peaks_list = struct.unpack(unpack_format1,decoded)
    # return [
    #     (peaks_list[i*2],peaks_list[i*2+1])
    #     for i in range(0,int(len(peaks_list)/2))
    # ]


def load_mzxml_file(filename):
    output_ms1 = []
    output_ms2 = []

    struct_iter_ok = True
    canary = True

    with open(filename) as fd:
        xmltodict_start = time.time()
        mzxml = xmltodict.parse(fd.read())
        xmltodict_end = time.time()
        print("XML time: " + str(xmltodict_end - xmltodict_start))
        read_scans = mzxml['mzXML']['msRun']['scan']
        filename_output = os.path.split(filename)[1]
        index = 1
        for scan in read_scans:
            # print(scan)
            ms_level, spectrum, struct_iter_ok, canary = read_mzxml_scan(scan, index, filename_output, struct_iter_ok, canary)
            index += 1
            if ms_level == 1:
                output_ms1.append(spectrum)
            if ms_level == 2:
                output_ms2.append(spectrum)
            nested_scans = scan.get('scan',[])
            if not isinstance(nested_scans,list):
                nested_scans = [nested_scans]
            for nested_scan in nested_scans:
                ms_level, spectrum, struct_iter_ok, canary = read_mzxml_scan(nested_scan, index, filename_output, struct_iter_ok, canary)
                index += 1
                output_ms2.append(spectrum)
    return output_ms1 + output_ms2

def read_mzxml_scan(scan, index, filename_output, struct_iter_ok, canary):
    ms_level = int(scan['@msLevel'])
    scan_number = int(scan['@num'])

    #Optional fields
    base_peak_intensity = 0.0
    base_peak_mz = 0.0
    base_peak_intensity = float(scan.get('@basePeakIntensity', 0.0))
    base_peak_mz = float(scan.get('@basePeakMz', 0.0))

    try:
        precursor_mz_tag = scan['precursorMz']
        precursor_mz = float(precursor_mz_tag['#text'])
        precursor_scan = int(precursor_mz_tag.get('@precursorScanNum', 0))
        precursor_charge = int(precursor_mz_tag.get('@precursorCharge', 0))
        precursor_intensity = float(precursor_mz_tag.get('@precursorIntensity', 0))
    except:
        if ms_level == 2:
            raise
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
        peaks = None
    if ms_level == 1:
        output = Spectrum(
            filename_output,
            scan_number,
            index,
            peaks,
            0,
            0,
            ms_level
        )
    if ms_level == 2:
        output = Spectrum(
            filename_output,
            scan_number,
            index,
            peaks,
            precursor_mz,
            precursor_charge,
            ms_level
        )
    return ms_level, output, struct_iter_ok, canary

def write_mgf_file(filename, spectrum_list):
    print("WRITING")
