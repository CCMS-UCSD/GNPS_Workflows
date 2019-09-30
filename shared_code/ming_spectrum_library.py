#!/usr/bin/python

import re
import xmltodict
import base64
import binascii
import struct
import os
import time
import zlib
import spectrum_alignment
import ming_fileio_library
import ming_psm_library
import ming_numerical_utilities
import ming_sptxt_library
from collections import defaultdict

try:
    from pyteomics import mass
    from pyteomics import mzml as pyteomicsmzml
except:
    print("no pyteomics")

"""

Spectrum Utilities to manipulate and do things with spectra

"""

class SpectrumCollection:
    def __init__(self, filename):
        self.filename = filename
        self.spectrum_list = []
        self.scandict = {}

    def load_from_file(self, drop_ms1=False):
        extension = ming_fileio_library.get_filename_extension(self.filename)
        if extension == ".mzXML":
            self.load_from_mzXML(drop_ms1=drop_ms1)

        if extension == ".mzML":
            self.load_from_mzML(drop_ms1=drop_ms1)

        if extension == ".mgf":
            self.load_from_mgf()

    def load_from_mgf(self):
        self.spectrum_list = load_mgf_file(self.filename)
        #Only keep non-None spectra
        new_spectrum_list = []
        for spectrum in self.spectrum_list:
            if spectrum != None:
                new_spectrum_list.append(spectrum)
        self.spectrum_list = new_spectrum_list
        for spectrum in self.spectrum_list:
            self.scandict[spectrum.scan] = spectrum

    def load_from_mzXML(self, drop_ms1=False):
        self.spectrum_list = load_mzxml_file(self.filename, drop_ms1=drop_ms1)
        file_idx = os.path.split(self.filename)[1]
        #Do indexing on scan number
        for spectrum in self.spectrum_list:
            self.scandict[spectrum.scan] = spectrum
            self.scandict[file_idx + ":" + str(spectrum.scan)] = spectrum

    def load_from_mzML(self, drop_ms1=False):
        self.spectrum_list = load_mzml_file(self.filename, drop_ms1=drop_ms1)
        file_idx = os.path.split(self.filename)[1]
        #Do indexing on scan number
        for spectrum in self.spectrum_list:
            self.scandict[spectrum.scan] = spectrum
            self.scandict[file_idx + ":" + str(spectrum.scan)] = spectrum

    def search_spectrum(self, otherspectrum, pm_tolerance, peak_tolerance, min_matched_peaks, min_score, analog_search=False, top_k=1):
        if otherspectrum == None:
            return []

        if len(otherspectrum.peaks) < min_matched_peaks:
            return []

        match_list = []
        for myspectrum in self.spectrum_list:
            if myspectrum == None:
                continue

            if len(myspectrum.peaks) < min_matched_peaks:
                continue

            mz_delta = abs(myspectrum.mz - otherspectrum.mz)
            if mz_delta < pm_tolerance or analog_search == True:
                cosine_score, matched_peaks = myspectrum.cosine_spectrum(otherspectrum, peak_tolerance)
                #Also check for min matched peaks
                if cosine_score > min_score and matched_peaks >= min_matched_peaks:
                    #print(cosine_score, matched_peaks, mz_delta)
                    match_obj = {}
                    match_obj["filename"] = myspectrum.filename
                    match_obj["scan"] = myspectrum.scan
                    match_obj["queryfilename"] = otherspectrum.filename
                    match_obj["queryscan"] = otherspectrum.scan
                    match_obj["cosine"] = cosine_score
                    match_obj["matchedpeaks"] = matched_peaks
                    match_obj["mzerror"] = abs(myspectrum.mz - otherspectrum.mz)

                    match_list.append(match_obj)

        match_list = sorted(match_list, key=lambda score_obj: score_obj["cosine"])

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
            if spectrum != None:
                output_mgf.write(spectrum.get_mgf_string() + "\n")

    def save_to_tsv(self, output_tsv_file, mgf_filename="", renumber_scans=True):
        if renumber_scans == True:
            self.make_scans_sequential()
        output_tsv_file.write(self.spectrum_list[0].get_tsv_header() + "\n")
        for spectrum in self.spectrum_list:
            if spectrum != None:
                output_tsv_file.write(spectrum.get_tsv_line(mgf_filename) + "\n")

    def save_to_sptxt(self, output_sptxt_file):
        for spectrum in self.spectrum_list:
            if spectrum != None:
                output_sptxt_file.write(spectrum.get_sptxt_string() + "\n")


class Spectrum:
    def __init__(self, filename, scan, index, peaks, mz, charge, ms_level, collision_energy=0.0, fragmentation_method="NO_FRAG", precursor_intensity=0.0, totIonCurrent=0.0):
        self.filename = filename
        self.scan = scan
        self.peaks = peaks
        self.mz = mz
        self.charge = charge
        self.index = index
        self.ms_level = ms_level
        self.retention_time = 0.0
        self.collision_energy = collision_energy
        self.fragmenation_method = fragmentation_method
        self.precursor_intensity = precursor_intensity
        self.totIonCurrent = totIonCurrent

    def get_mgf_string(self):
        output_lines = []
        output_lines.append("BEGIN IONS")
        output_lines.append("SCANS=" + str(self.scan))
        output_lines.append("PEPMASS=" + str(self.mz))
        output_lines.append("CHARGE=" + str(self.charge))
        output_lines.append("COLLISION_ENERGY=" + str(self.collision_energy))
        output_lines.append(self.get_mgf_peak_string())
        output_lines.append("END IONS")

        return "\n".join(output_lines)

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
        total_score, reported_alignments = spectrum_alignment.score_alignment(self.peaks, other_spectrum.peaks, self.mz * self.charge, other_spectrum.mz * other_spectrum.charge, peak_tolerance, self.charge)
        return total_score, len(reported_alignments)

    #Looks at windows of a given size, and picks the top peaks in there
    def window_filter_peaks(self, window_size, top_peaks):
        new_peaks = window_filter_peaks(self.peaks, window_size, top_peaks)
        self.peaks = new_peaks

    def filter_to_top_peaks(self, top_k_peaks):
        sorted_peaks = sorted(self.peaks, key=lambda peak: peak[1], reverse=True)
        sorted_peaks = sorted_peaks[:top_k_peaks]
        sorted_peaks = sorted(sorted_peaks, key=lambda peak: peak[0], reverse=False)
        self.peaks = sorted_peaks

    def filter_precursor_peaks(self):
        new_peaks = filter_precursor_peaks(self.peaks, 20.0, self.mz)
        self.peaks = new_peaks

    def filter_noise_peaks(self, min_snr):
        average_noise_level = ming_numerical_utilities.calculate_noise_level_in_peaks(self.peaks)
        new_peaks = []
        for peak in self.peaks:
            if peak[1] > average_noise_level * min_snr:
                new_peaks.append(peak)
        self.peaks = new_peaks

    def filter_peak_mass_range(self, lower, higher):
        new_peaks = []
        for peak in self.peaks:
            if peak[0] < lower or peak[0] > higher:
                new_peaks.append(peak)
        self.peaks = new_peaks



    def generated_spectrum_vector(self, peptide=None, attenuation_ratio=0.0, tolerance=0.5, bin_size=1):
        peaks_to_vectorize = self.peaks
        max_mass = 1500

        if peptide != None:
            charge_set = range(1, self.charge + 1)
            theoretical_peaks = ming_psm_library.create_theoretical_peak_map(self.peptide, ["b", "y", "b-H2O", "b-NH3", "y-H2O", "y-NH3", "a"], charge_set=charge_set)
            annotated_peaks, unannotated_peaks = ming_psm_library.extract_annotated_peaks(theoretical_peaks, self.peaks, tolerance)
            new_peaks = annotated_peaks
            if attenuation_ratio > 0:
                for unannotated_peak in unannotated_peaks:
                    unannotated_peak[1] *= attenuation_ratio
                    new_peaks.append(unannotated_peak)
            peaks_to_vectorize = sorted(new_peaks, key=lambda peak: peak[0])

        #Doing
        peak_vector = ming_numerical_utilities.vectorize_peaks(self.peaks, max_mass, bin_size)

        return peak_vector

    def get_number_of_signal_peaks(self, SNR_Threshold=5):
        return ming_numerical_utilities.calculate_signal_peaks_in_peaklist(self.peaks, SNR_Threshold)

    def get_number_of_peaks_within_percent_of_max(self, percent=1.0):
        max_peak_intensity = 0.0
        for peak in self.peaks:
            max_peak_intensity = max(peak[1], max_peak_intensity)

        intensity_threshold = percent / 100.0 * max_peak_intensity

        number_of_peaks = 0
        for peak in self.peaks:
            if peak[1] > intensity_threshold:
                number_of_peaks += 1

        return number_of_peaks

    """Gives sum of intensity of all spectrum peaks"""
    def get_total_spectrum_intensity(self):
        total_peak_intensity = 0
        for peak in self.peaks:
            total_peak_intensity += peak[1]
        return total_peak_intensity


class PeptideLibrarySpectrum(Spectrum):
    def __init__(self, filename, scan, index, peaks, mz, charge, peptide, protein, collision_energy=0.0):
        Spectrum.__init__(self, filename, scan, index, peaks, mz, charge, 2)
        self.collision_energy = collision_energy
        self.peptide = peptide
        self.protein = protein
        self.annotated_peaks = 0
        self.explained_intensity = 0.0
        self.signal_peaks = 0
        self.number_of_peaks_within_1_percent_of_max = 0
        self.number_of_peaks_within_5_percent_of_max = 0
        self.annotated_ions = 0
        self.number_of_b_y_breaks = 0
        self.score = 0.0
        self.variant_score = 0.0
        self.fdr = 0.0
        self.num_spectra = 0
        self.spectrum_ranking = 0
        self.proteosafe_task = ""
        self.originalfile_scan = 0
        self.originalfile_filename = ""

    #Returns the peptide sequence without modifications
    def get_peptide_clean(self):
        return re.sub(r'[^A-Z]', '', self.peptide)

    def get_annotated_peak_count(self, tolerance):
        annotated_peak_count = ming_psm_library.calculated_number_annotated_peaks(self.peaks, self.charge, self.peptide, tolerance)
        return annotated_peak_count

    def get_mgf_string(self):
        output_string = "BEGIN IONS\n"
        output_string += "PEPMASS=" + str(self.mz) + "\n"
        output_string += "CHARGE=" + str(self.charge) + "\n"
        output_string += "MSLEVEL=" + "2" + "\n"
        output_string += "COLLISION_ENERGY=" + str(self.collision_energy) + "\n"
        output_string += "FILENAME=" + self.filename + "\n"
        output_string += "SEQ=" + self.peptide + "\n"
        output_string += "PROTEIN=" + self.protein + "\n"
        output_string += "SCANS=" + str(self.scan) + "\n"
        output_string += "SCAN=" + str(self.scan) + "\n"
        output_string += "SCORE=" + str(self.score) + "\n"
        output_string += "FDR=" + str(self.fdr) + "\n"
        output_string += self.get_mgf_peak_string()
        output_string += "END IONS\n"

        return output_string

    def get_sptxt_peaks(self):
        output_peaks_list = []
        peak_max_int = max([x[1] for x in self.peaks])
        for peak in self.peaks:
            output_peaks_list.append(str(peak[0]) + "\t" + str(peak[1]/peak_max_int * 10000) + "\t" + "\"?\"")
        return "\n".join(output_peaks_list)

    def get_sptxt_string(self):
        output_lines = []
        annotations_line = "Name: " + ming_sptxt_library.transform_peptide_to_msp_library_string(self.peptide) + "/" + str(self.charge)
        output_lines.append(annotations_line)

        mod_string = ming_sptxt_library.transform_peptide_to_msp_mods(self.peptide)
        comment_line = "Comment: " + "Parent=" + str(self.mz) + " " + "Mods=" + mod_string
        output_lines.append(comment_line)

        output_lines.append("Num peaks: " + str(len(self.peaks)))
        output_lines.append(self.get_sptxt_peaks())


        return "\n".join(output_lines) + "\n"

    def attentuate_unannotated_peaks(self, attenuation_ratio=0.0, tolerance=0.5):
        charge_set = range(1, self.charge + 1)
        theoretical_peaks = ming_psm_library.create_theoretical_peak_map(self.peptide, ["b", "y", "b-H2O", "b-NH3", "y-H2O", "y-NH3", "a"], charge_set=charge_set)
        annotated_peaks, unannotated_peaks = ming_psm_library.extract_annotated_peaks(theoretical_peaks, self.peaks, tolerance)
        new_peaks = annotated_peaks
        if attenuation_ratio > 0:
            for unannotated_peak in unannotated_peaks:
                unannotated_peak[1] *= attenuation_ratio
                new_peaks.append(unannotated_peak)
        new_peaks = sorted(new_peaks, key=lambda peak: peak[0])
        self.peaks = new_peaks

    @staticmethod
    def get_tsv_header():
        return "mgf_filename\toriginalfilename\toriginalfile_filename\toriginalfile_scan\tspectrumindex\tspectrumscan\tcharge\tmz\tpeptide\tprotein\tcollision_energy\tannotated_peaks\texplained_intensity\tsignal_peaks\tnumber_of_peaks_within_1_percent_of_max\tnumber_of_peaks_within_5_percent_of_max\tpeaks\tannotated_ions\tnumber_of_b_y_breaks\tscore\tvariant_score\tlength\tpercentagebreaks\tproteosafe_task\tnum_spectra\tspectrum_ranking"

    def get_tsv_line(self, output_mgf_filename=""):
        length_of_peptide = len(ming_psm_library.strip_sequence(self.peptide))
        percentage_breaks = float(self.number_of_b_y_breaks)/float(length_of_peptide)
        return "%s\t%s\t%s\t%s\t%d\t%d\t%d\t%f\t%s\t%s\t%f\t%d\t%f\t%d\t%d\t%d\t%d\t%d\t%d\t%f\t%f\t%d\t%f\t%s\t%d\t%d" % (output_mgf_filename, self.filename, self.originalfile_filename, self.originalfile_scan, self.index, self.scan, self.charge, self.mz, self.peptide, self.protein, self.collision_energy, self.annotated_peaks, self.explained_intensity, self.signal_peaks, self.number_of_peaks_within_1_percent_of_max, self.number_of_peaks_within_5_percent_of_max, len(self.peaks), self.annotated_ions, self.number_of_b_y_breaks, self.score, self.variant_score, length_of_peptide, percentage_breaks, self.proteosafe_task, self.num_spectra, self.spectrum_ranking)


def load_mgf_peptide_library(filename):
    charge = 0
    mz = 0
    peaks = []
    scan = -1
    peptide = ""
    protein = ""
    spectrum_index = 0
    collision_energy = 0
    score = 0.0
    fdr = 0.0

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
            score = 0.0
            fdr = 0.0
            continue

        if mgf_file_line == "END IONS":
            lib_spectrum = PeptideLibrarySpectrum(filename, scan, spectrum_index, peaks, mz, charge, peptide, protein, collision_energy=collision_energy)
            lib_spectrum.score = score
            lib_spectrum.fdr = fdr
            spectrum_index += 1
            output_spectra.append(lib_spectrum)
            if spectrum_index % 1000 == 0:
                print("Spectrum " + str(spectrum_index), lib_spectrum.peptide)
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

        if mgf_file_line.find("COLLISION_ENERGY=") != -1:
            collision_energy = float(mgf_file_line[17:])
            continue

        if mgf_file_line.find("SCORE=") != -1:
            score = float(mgf_file_line[6:])
            continue

        if mgf_file_line.find("FDR=") != -1:
            fdr = float(mgf_file_line[4:])
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
    spectrum_count = 0
    non_empty_spectrum = 0

    output_spectra = []

    for line in open(filename, "r"):
        mgf_file_line = line.rstrip()
        if len(mgf_file_line) < 4:
            continue

        if mgf_file_line[0] == "#":
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
            if spectrum_count % 10000 == 0:
                print("Spectra Loaded\t%d\tReal\t%d" % (spectrum_count, non_empty_spectrum))

            if len(peaks) > 0:
                non_empty_spectrum += 1
                adding_spectrum = Spectrum(filename, scan, -1, peaks, mz, charge, 2)
                output_spectra.append(adding_spectrum)
            else:
                output_spectra.append(None)
            spectrum_count += 1
            continue

        if mgf_file_line[:8] == "PEPMASS=":
            mz = float(mgf_file_line[8:])
            continue
        if mgf_file_line[:7] == "CHARGE=":
            try:
                if mgf_file_line[7:].find("-") != -1:
                    charge = - int(mgf_file_line[7:].replace("-", ""))
                else:
                    charge = int(mgf_file_line[7:].replace("+", ""))
            except:
                charge = 0

            continue
        if mgf_file_line[:6] == "SCANS=":
            scan = int(mgf_file_line[6:])
            continue

        if mgf_file_line[:4] == "SEQ=":
            peptide = mgf_file_line[4:]
            continue

        if mgf_file_line[:8] == "PROTEIN=":
            protein = mgf_file_line[8:]
            continue

        if mgf_file_line.find("=") == -1:
            peak_split = re.split("[ |\t]+", mgf_file_line)
            peaks.append([float(peak_split[0]), float(peak_split[1])])

    return output_spectra


def load_gnps_library_mgf_file(filename):
    charge = 0
    mz = 0
    peaks = []
    scan = 0
    peptide = ""
    protein = ""
    spectrum_count = 0
    non_empty_spectrum = 0
    spectrumid = ""
    inchi_string = ""
    smiles_string = "N/A"

    output_spectra = []

    for line in open(filename, "r"):
        mgf_file_line = line.rstrip()
        if len(mgf_file_line) < 4:
            continue

        if mgf_file_line[0] == "#":
            continue

        if mgf_file_line == "BEGIN IONS":
            charge = 0
            mz = 0
            peaks = []
            scan = 0
            peptide = ""
            protein = ""
            inchi_string = ""
            smiles_string = "N/A"
            continue

        if mgf_file_line == "END IONS":
            if spectrum_count % 10000 == 0:
                print("Spectra Loaded\t%d\tReal\t%d" % (spectrum_count, non_empty_spectrum))

            if len(peaks) > 0:
                if len(spectrumid) < 5:
                    print("Not a valid GNPS Library file")
                    exit(1)
                non_empty_spectrum += 1
                adding_spectrum = Spectrum(filename, scan, -1, peaks, mz, charge, 2)
                library_spectrum = LibrarySpectrum(adding_spectrum)
                library_spectrum.spectrumid = spectrumid
                library_spectrum.inchi = inchi_string
                library_spectrum.smiles = smiles_string
                output_spectra.append(library_spectrum)
            else:
                output_spectra.append(None)
            spectrum_count += 1
            continue

        if mgf_file_line[:8] == "PEPMASS=":
            mz = float(mgf_file_line[8:])
            continue
        if mgf_file_line[:7] == "CHARGE=":
            charge = int(mgf_file_line[7:].replace("+", ""))
            continue
        if mgf_file_line[:6] == "SCANS=":
            scan = int(mgf_file_line[6:])
            continue

        if mgf_file_line[:4] == "SEQ=":
            peptide = mgf_file_line[4:]
            continue

        if mgf_file_line[:8] == "PROTEIN=":
            protein = mgf_file_line[8:]
            continue

        if mgf_file_line[:11] == "SPECTRUMID=":
            spectrumid = mgf_file_line[11:]
            continue

        if mgf_file_line[:6] == "INCHI=":
            inchi_string = mgf_file_line[6:]
            continue

        if mgf_file_line[:7] == "SMILES=":
            smiles_string = mgf_file_line[7:]
            continue

        if mgf_file_line.find("=") == -1:
            peak_split = re.split("[ |\t]+", mgf_file_line)
            peaks.append([float(peak_split[0]), float(peak_split[1])])

    return output_spectra


def load_massbank_file(filename):
    peptide = "*..*"
    smiles = ""
    inchi = ""
    pepmass = ""
    title = ""
    instrument = ""
    compound_name = ""
    peaks = []
    retentiontime = ""
    ion_mode = ""
    peaks_start = 0;
    exactmass = "0"
    cas_number = ""
    adduct = "[M+H]"
    spectrum_level = 0
    charge = 1

    scan_number = 1

    output_spectra = []

    for line in open(filename):
        #writing out spectrum
        if line.find("//") != -1:
            if len(pepmass) == 0:
                resolved = 0
                if len(exactmass) > 1 and adduct == "[M+H]+":
                    pepmass =  str(float(exactmass) + 1.007825)
                    resolved = 1
                if len(exactmass) > 1 and adduct == "M+":
                    pepmass =  exactmass
                    resolved = 1
                if len(exactmass) > 1 and adduct == "[M+H-H2O]+":
                    pepmass =  str(float(exactmass) + 1.007825 - 18.010565)
                    resolved = 1
                if len(exactmass) > 1 and adduct == "[M+H-(C12H20O9)]+":
                    pepmass =  str(float(exactmass) + 1.007825 - 308.110735)
                    resolved = 1

                if resolved == 0:
                    print("FUCK THIS SHIT: " + title)

            output_spectra.append(Spectrum(filename, scan_number, -1, peaks, pepmass, charge, 2))

            scan_number += 1

            #Resetting variables
            peptide = "*..*"
            smiles = "N/A"
            inchi = "N/A"
            pepmass = ""
            title = ""
            instrument = ""
            compound_name = ""
            peaks = []
            retentiontime = ""
            ion_mode = ""
            exactmass = "0"
            cas_number = "N/A"
            adduct = "[M+H]"
            spectrum_level = 0



        if line.find("ACCESSION") != -1:
            peptide = "*..*"
            peaks_start = 0
            title = line.replace("ACCESSION: ","").replace("//","").rstrip()

        if line.find("CH$SMILES:") != -1:
            smiles = line[len("CH$SMILES: "):].rstrip()

        if line.find("CH$IUPAC: InChI=") != -1:
            inchi = line[len("CH$IUPAC: InChI="):].rstrip()

        if line.find("AC$MASS_SPECTROMETRY: ION_MODE") != -1:
            ion_mode = line[len("AC$MASS_SPECTROMETRY: ION_MODE "):].rstrip()

        if line.find("AC$INSTRUMENT_TYPE:") != -1:
            instrument = line[len("AC$INSTRUMENT_TYPE: "):].rstrip()

        if line.find("AC$CHROMATOGRAPHY: RETENTION_TIME ") != -1:
            retentiontime = line[len("AC$CHROMATOGRAPHY: RETENTION_TIME "):].rstrip()

        if line.find("MS$FOCUSED_ION: PRECURSOR_M/Z ") != -1:
            pepmass = line[len("MS$FOCUSED_ION: PRECURSOR_M/Z "):].rstrip()

        if line.find("MS$FOCUSED_ION: FULL_SCAN_FRAGMENT_ION_PEAK ") != -1:
            if len(pepmass) == 0:
                pepmass = line[len("MS$FOCUSED_ION: FULL_SCAN_FRAGMENT_ION_PEAK "):].rstrip()

        if line.find("CH$NAME: ") != -1:
            compound_name += line[len("CH$NAME: "):].rstrip() + "|"

        if line.find("CH$EXACT_MASS: ") != -1:
            exactmass = line[len("CH$EXACT_MASS: "):].rstrip()

        if line.find("CH$LINK: CAS ") != -1:
            cas_number = line[len("CH$LINK: CAS "):].rstrip()

        if line.find("MS$FOCUSED_ION: PRECURSOR_TYPE ") != -1:
            adduct = line[len("MS$FOCUSED_ION: PRECURSOR_TYPE "):].rstrip()

        if line.find("AC$MASS_SPECTROMETRY: MS_TYPE MS2") != -1:
            spectrum_level = 2

        if line.find("PK$PEAK") != -1:
            peaks_start = 1
            continue

        if (peaks_start == 1) and line.find("//") == -1:
            if line.find("int. rel.int") != -1:
                continue
            line = line.strip()
            splits = line.split(" ")
            peaks.append([float(splits[0]), float(splits[1])])
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

def load_mzml_file(filename, drop_ms1=False):
    output_ms1 = []
    output_ms2 = []

    for spectrum in pyteomicsmzml.read(filename):
        # print("==========================")
        #
        # for key in spectrum.keys():
        #     print(key, spectrum[key])

        ms_level = spectrum["ms level"]
        scan = -1
        index = int(spectrum["index"])
        peaks = []
        #peaks_zipped = zip(spectrum["m/z array"], spectrum["intensity array"])

        for i in range(len(spectrum["m/z array"])):
            peaks.append([float(spectrum["m/z array"][i]), float(spectrum["intensity array"][i])])



        #Determining scan
        for id_split in spectrum["id"].split(" "):
            if id_split.find("scan=") != -1:
                scan = int(id_split.replace("scan=", ""))

        if ms_level == 1:
            if drop_ms1 == False:
                output = Spectrum(
                        filename,
                        scan,
                        index,
                        peaks,
                        0,
                        0,
                        ms_level
                    )

                output_ms1.append(output)

        if ms_level == 2:
            precusor_list = spectrum["precursorList"]["precursor"][0]
            activation = precusor_list["activation"]
            collision_energy = float(activation["collision energy"])

            selected_ion_list = precusor_list["selectedIonList"]
            precursor_mz = float(selected_ion_list["selectedIon"][0]["selected ion m/z"])
            precursor_intensity = 0
            precursor_charge = 0

            try:
                precursor_intensity = float(selected_ion_list["selectedIon"][0]["peak intensity"])
            except:
                precursor_intensity = 0

            try:
                precursor_charge = int(selected_ion_list["selectedIon"][0]["charge state"])
            except:
                precursor_charge = 0


            fragmentation_method = "NO_FRAG"
            try:
                totIonCurrent = float(spectrum["total ion current"])
            except:
                totIonCurrent = 0

            try:
                for key in activation:
                    if key == "beam-type collision-induced dissociation":
                        fragmentation_method = "HCD"
            except:
                fragmentation_method = "NO_FRAG"

            output = Spectrum(
                    filename,
                    scan,
                    index,
                    peaks,
                    precursor_mz,
                    precursor_charge,
                    ms_level,
                    collision_energy=collision_energy,
                    fragmentation_method=fragmentation_method,
                    precursor_intensity=precursor_intensity,
                    totIonCurrent=totIonCurrent
                )
            output_ms1.append(output)

    return output_ms1 + output_ms2

def load_mzxml_file(filename, drop_ms1=False):
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
            ms_level, spectrum, struct_iter_ok, canary = read_mzxml_scan(scan, index, filename_output, struct_iter_ok, canary, drop_ms1)
            index += 1
            if ms_level == 1:
                if drop_ms1 == False:
                    output_ms1.append(spectrum)
            if ms_level == 2:
                output_ms2.append(spectrum)
            nested_scans = scan.get('scan',[])
            if not isinstance(nested_scans,list):
                nested_scans = [nested_scans]
            for nested_scan in nested_scans:
                ms_level, spectrum, struct_iter_ok, canary = read_mzxml_scan(nested_scan, index, filename_output, struct_iter_ok, canary, drop_ms1)
                index += 1
                output_ms2.append(spectrum)
    return output_ms1 + output_ms2

def read_mzxml_scan(scan, index, filename_output, struct_iter_ok, canary, drop_ms1):
    ms_level = int(scan['@msLevel'])

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
    base_peak_intensity = 0.0
    base_peak_mz = 0.0
    base_peak_intensity = float(scan.get('@basePeakIntensity', 0.0))
    base_peak_mz = float(scan.get('@basePeakMz', 0.0))
    totIonCurrent = 0

    try:
        totIonCurrent = float(scan.get('@totIonCurrent', 0.0))
    except KeyboardInterrupt:
        raise
    except:
        fragmentation_method = "NO_FRAG"

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
            raise

    #Loading retention time
    retention_time = 0.0
    try:
        retention_time_string = scan['@retentionTime']
        #print(retention_time_string)
        retention_time = float(retention_time_string[2:-1])
    except KeyboardInterrupt:
        raise
    except:
        print("ERROR")
        retention_time = 0.0

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
            ms_level,
            collision_energy=collision_energy,
            fragmentation_method=fragmentation_method,
            precursor_intensity=precursor_intensity,
            totIonCurrent=totIonCurrent
        )
        output.retention_time = retention_time
    return ms_level, output, struct_iter_ok, canary

def write_mgf_file(filename, spectrum_list):
    print("WRITING")

def filter_precursor_peaks(peaks, tolerance_to_precursor, mz):
    new_peaks = []
    for peak in peaks:
        if abs(peak[0] - mz) > tolerance_to_precursor:
            new_peaks.append(peak)
    return new_peaks

def filter_noise_peaks(peaks, min_snr):
    average_noise_level = ming_numerical_utilities.calculate_noise_level_in_peaks(peaks)
    new_peaks = []
    for peak in peaks:
        if peak[1] > average_noise_level * min_snr:
            new_peaks.append(peak)
    return new_peaks

def filter_peaks_noise_or_window(peaks, min_snr, window_size, top_peaks):
    window_filtered_peaks = window_filter_peaks(peaks, window_size, top_peaks)
    snr_peaks = filter_noise_peaks(peaks, min_snr)

    peak_masses_to_keep = []
    for peak in window_filtered_peaks:
        peak_masses_to_keep.append(peak[0])
    for peak in snr_peaks:
        peak_masses_to_keep.append(peak[0])

    peak_masses_to_keep = set(peak_masses_to_keep)

    new_peak = []
    for peak in peaks:
        if peak[0] in peak_masses_to_keep:
            new_peak.append(peak)

    return new_peak

def filter_to_top_peaks(peaks, top_k_peaks):
    sorted_peaks = sorted(peaks, key=lambda peak: peak[1], reverse=True)
    return sorted_peaks[:top_k_peaks]


def calculate_unique_ions_annotated(peaks, max_charge, peptide, tolerance):
    charge_set = range(1, max_charge + 1)
    theoretical_peaks = ming_psm_library.create_theoretical_peak_map(peptide, ["b",  "b-iso", "y", "y-iso", "b-H2O", "b-NH3", "y-H2O", "y-NH3", "a"], charge_set=charge_set)

    #Determining which ions are annotated
    annotated_ions = set()
    for peak in peaks:
        mass = peak[0]
        for ion_peak in theoretical_peaks:
            if abs(mass - theoretical_peaks[ion_peak]) < tolerance:
                annotated_ions.add(ion_peak)

    return list(annotated_ions)


def map_ions_to_peak(peaks, max_charge, tolerance, peptide, ions_to_consider=["b", "y", "b-H2O", "b-NH3", "y-H2O", "y-NH3", "a"]):
    charge_set = range(1, max_charge + 1)
    theoretical_peaks = ming_psm_library.create_theoretical_peak_map(peptide, ions_to_consider, charge_set=charge_set)

    ions_to_peaks = defaultdict(list)

    for peak in peaks:
        mass = peak[0]
        for ion_peak in theoretical_peaks:
            if abs(mass - theoretical_peaks[ion_peak]) < tolerance:
                ions_to_peaks[ion_peak].append(peak)
                break

    #Now lets choose the peak with biggest intensity
    ions_to_peak = {}
    for ion in ions_to_peaks:
        max_peak = ions_to_peaks[ion][0]
        for peak in ions_to_peaks[ion]:
            if peak[1] > max_peak[1]:
                max_peak = peak
        ions_to_peak[ion] = max_peak

    return ions_to_peak

def determine_b_y_breaks_total(peaks, max_charge, tolerance, peptide, SNR=2.0):
    if SNR > 1.0:
        peaks = filter_peaks_noise_or_window(peaks, SNR, 100, 20)

    ions_to_consider=["b", "y"]

    ions_to_peaks_mapping = map_ions_to_peak(peaks, max_charge, tolerance, peptide, ions_to_consider)

    all_ions = ions_to_peaks_mapping.keys()

    peptide_length = len(ming_psm_library.strip_sequence(peptide))

    all_prm_break_numbers = []
    for ion in all_ions:
        ion_splits = ion.split(":")
        ion_type = ion_splits[0]
        ion_number = int(ion_splits[1])
        ion_charge = int(ion_splits[2])

        prm_break_number = -1
        if ion_type == "b":
            prm_break_number = ion_number
        if ion_type == "y":
            prm_break_number = peptide_length - ion_number  + 1
        all_prm_break_numbers.append(prm_break_number)

    all_prm_break_numbers = list(set(all_prm_break_numbers))
    #print(peptide, max_charge, peptide_length, all_prm_break_numbers, all_ions, peaks)
    return len(all_prm_break_numbers)







def calculated_number_unique_ions_annotated_in_signal(peaks, max_charge, peptide, tolerance, SNR=2.0):
    new_peaks = filter_noise_peaks(peaks, SNR)
    ion_list = calculate_unique_ions_annotated(new_peaks, max_charge, peptide, tolerance)
    return len(ion_list)

def attenuate_unannotated_peaks(peaks, max_charge, tolerance, peptide, attenuation_ratio=0):
    charge_set = range(1, max_charge)
    theoretical_peaks = ming_psm_library.create_theoretical_peak_map(peptide, ["b", "y", "b-H2O", "b-NH3", "y-H2O", "y-NH3", "a"], charge_set=charge_set)
    annotated_peaks, unannotated_peaks = ming_psm_library.extract_annotated_peaks(theoretical_peaks, peaks, tolerance)
    new_peaks = annotated_peaks
    if attenuation_ratio > 0:
        for unannotated_peak in unannotated_peaks:
            unannotated_peak[1] *= attenuation_ratio
            new_peaks.append(unannotated_peak)
    new_peaks = sorted(new_peaks, key=lambda peak: peak[0])
    return new_peaks

def window_filter_peaks(peaks, window_size, top_peaks):
    peak_list_window_map = defaultdict(list)
    for peak in peaks:
        mass = peak[0]
        mass_bucket = int(mass/window_size)
        peak_list_window_map[mass_bucket].append(peak)

    new_peaks = []
    for bucket in peak_list_window_map:
        peaks_sorted_by_intensity = sorted(peak_list_window_map[bucket], key=lambda peak: peak[1], reverse=True)
        peaks_to_keep = peaks_sorted_by_intensity[:top_peaks]
        new_peaks += peaks_to_keep

    new_peaks = sorted(new_peaks, key=lambda peak: peak[0])
    return new_peaks


def writeMgf(inputPath, outputPath,format):
    """ Convert the mzml or mzxml input format file to sirius mgf format
        
        Parameters:
        inputPath (stirng): mzml/mzxml input path
        outputPath (string): mgf output path
        format (string ["mzml" or "mzxml"]): the input file type
        
        Returns:
        void
        
    """
    if format == "mzml":
        speclist = load_mzml_file(inputPath)
    elif format == "mzxml":
        speclist = load_mzxml_file(inputPath)
    else:
        return
    speclist.sort(key=lambda x: x.index)
    fout = open(outputPath,"w")
    featureID = 0
    for i in speclist:
        out = []
        if i.ms_level == 1:
            featureID +=1
        out.append("BEGIN IONS")
        out.append("FEATURE_ID=%d"%(featureID))
        out.append("PEPMASS=%f"%(i.mz))
        out.append("CHARGE=%d"%(i.charge))
        out.append("RTINSECONDS=%f"%(i.retention_time))
        out.append("SPECTYPE=CORRELATED MS")
        out.append("MSLEVEL=%d"%(i.ms_level))
        out.append("FILENAME=%s"%(i.filename))
        out.append("SCAN=-1")
        out.append(i.get_mgf_peak_string())
        out = "\n".join(out)
        out += "END IONS\n\n"
        fout.write(out)


