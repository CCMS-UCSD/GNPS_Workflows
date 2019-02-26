#!/usr/bin/python

"""

PSM Utilities to read psms

"""

import ming_fileio_library
import math
import re
import random

try:
    from pyteomics import mass
    known_modification_masses = mass.std_aa_comp
except:
    print("no pyteomics")

class PSM:
    def __init__(self, filename, scan, annotation, score, decoy, protein, charge, frag_method="NO_FRAG"):
        self.filename = filename
        self.scan = scan
        self.annotation = annotation
        self.score = score
        self.decoy = decoy
        self.protein = protein
        self.charge = charge
        self.fdr = -1.0
        self.ppm_error = -1.0
        self.frag_method = frag_method
        self.collision_energy = 0.0
        self.extra_metadata = {}


    @staticmethod
    def output_header():
        return_headers = "sequence\tscore\tdecoy\tFDR\tfilename\tscan\tcharge\tppm_error\tFragMethod\tcollision_energy"
        return return_headers

    def __str__(self):
        try:
            return "%s\t%s\t%s\t%s\t%s\t%s\t%d\t%f\t%s\t%f" % (self.annotation, str(self.score), str(self.decoy), str(self.fdr), self.filename, str(self.scan), self.charge, self.ppm_error, self.frag_method, self.collision_energy)
        except KeyboardInterrupt:
            raise
        except:
            return "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (self.annotation, str(self.score), str(self.decoy), str(self.fdr), self.filename, str(self.scan), str(self.charge), str(self.ppm_error), self.frag_method, str(self.collision_energy))

    def __repr__(self):
        return str(self)

    def get_extra_metadata_headers(self):
        return "\t".join(self.extra_metadata.keys())

    #def get_extra_metadata_values(self):
    #    return "\t".join(self.extra_metadata.values())

    def is_decoy(self):
        return self.decoy

    def sorting_value(self):
        return self.score

    def get_stripped_sequence(self):
        sequence = self.annotation
        p = re.compile('\W|\d')
        sequence = p.sub("", sequence)
        return sequence

    def get_annotation_without_charge(self):
        return remove_charges_from_annotation(self.annotation)

    def calculate_theoretical_mz(self):
        return calculate_theoretical_peptide_mass(self.get_annotation_without_charge(), self.charge)


class PSMset:
    def __init__(self, name):
        self.name = name
        self.psms = []

    def __len__(self):
        return len(self.psms)



    #Loading a TSV File from MSGFDB
    def load_MSGF_tsvfile(self, filename):
        self.psms += parse_MSGF_tsvfile(filename)

    def load_MSGF_Plus_tsvfile(self, filename):
        self.psms += parse_MSGFPlus_tsvfile(filename)

    def remove_duplicated_rows(self):
        seen_psm_keys = set()
        new_psm_list = []
        for psm in self.psms:
            psm_key = psm.filename + "." + str(psm.scan) + "." + psm.annotation
            if psm_key in seen_psm_keys:
                continue
            seen_psm_keys.add(psm_key)
            new_psm_list.append(psm)
        self.psms = new_psm_list


    def load_PSM_tsvfile(self, filename, load_extra_metadata=False):
        self.psms = parse_psm_file(filename, load_extra_metadata)

    def remove_redundant_psms(self):
        new_psm_list = []
        observed_psms = set()
        for psm in self.psms:
            spectrum_key = psm.filename + "." + str(psm.scan) + "." + str(psm.annotation)
            if spectrum_key in observed_psms:
                continue
            observed_psms.add(spectrum_key)
            new_psm_list.append(psm)
        print("Filtered redundant PSMs from ", len(self.psms), "to", len(new_psm_list))
        self.psms = new_psm_list


    #Filter PSMs to given FDR
    def filter_to_fdr(self, fdr):
        filtered_psms = filter_psm_fdr(self.psms, fdr)
        print("Filtered " + str(len(self.psms)) + " to " + str(len(filtered_psms)))
        self.psms = filtered_psms

    def filter_to_fdr_by_length(self, fdr):
        output_psms = []
        peptide_length_map = {}
        for psm in self.psms:
            peptide_length = len(psm.get_stripped_sequence())
            if not peptide_length in peptide_length_map:
                peptide_length_map[peptide_length] = []
            peptide_length_map[peptide_length].append(psm)

        for peptide_length in peptide_length_map:
            filtered_psms = filter_psm_fdr(peptide_length_map[peptide_length], fdr)
            print("Filtered Length " + str(peptide_length) + " " + str(len(peptide_length_map[peptide_length])) + " to " + str(len(filtered_psms)))
            output_psms += filtered_psms
        self.psms = output_psms

    def filter_synthetic_psms_by_length(self, target_filename_list, decoy_filename_list, fdr=0.0000000001):
        output_psms = []
        peptide_length_map = {}
        for psm in self.psms:
            peptide_length = len(psm.get_stripped_sequence())
            if not peptide_length in peptide_length_map:
                peptide_length_map[peptide_length] = []
            peptide_length_map[peptide_length].append(psm)

        for peptide_length in peptide_length_map:
            filtered_psms = filter_synthetic_psms(peptide_length_map[peptide_length], target_filename_list, decoy_filename_list, fdr=fdr)
            print("Filtered Length " + str(peptide_length) + " " + str(len(peptide_length_map[peptide_length])) + " to " + str(len(filtered_psms)))
            output_psms += filtered_psms
        self.psms = output_psms

    def synthetic_psms_by_length_decoy_set(self, target_filename_list, decoy_filename_list):
        decoy_psms = []
        peptide_length_map = {}
        for psm in self.psms:
            peptide_length = len(psm.get_stripped_sequence())
            if not peptide_length in peptide_length_map:
                peptide_length_map[peptide_length] = []
            peptide_length_map[peptide_length].append(psm)

        for peptide_length in peptide_length_map:
            filtered_psms = get_synthetic_decoy_psms(peptide_length_map[peptide_length], target_filename_list, decoy_filename_list)
            decoy_psms += filtered_psms
        return decoy_psms






    #Calculate FDR of PSM Set
    def calculate_fdr(self):
        running_target_count = 0
        running_decoy_count = 0
        for psm in self.psms:
            if psm.is_decoy() == 0:
                running_target_count += 1
            else:
                running_decoy_count += 1

        current_fdr = float(running_decoy_count) / float(running_target_count)
        return current_fdr

    def write_output(self, output_file, write_extra_metadata=False):
        if write_extra_metadata:
            if len(self.psms) > 0:
                metadata_headers_list = self.psms[0].extra_metadata.keys()
                output_headers = ""
                if len(metadata_headers_list) > 0:
                    metadata_header_string = ""
                    for header in metadata_headers_list:
                        metadata_header_string += header + "\t"
                    output_headers = PSM.output_header() + "\t" + metadata_header_string.rstrip() + "\n"
                else:
                    output_headers = PSM.output_header() + "\n"
                output_file.write(output_headers)

                #print(metadata_headers_list)
                #print(metadata_header_string)
                for psm in self.psms:
                    values_list = []
                    for header in metadata_headers_list:
                        if header in psm.extra_metadata:
                            values_list.append(psm.extra_metadata[header].rstrip())
                        else:
                            values_list.append("0")

                    if len(values_list) > 0:
                        output_file.write(str(psm) + "\t" + "\t".join(values_list) + "\n")
                    else:
                        output_file.write(str(psm) + "\n")

            else:
                output_file.write(PSM.output_header() + "\n")
        else:
            output_file.write(PSM.output_header() + "\n")
            for psm in self.psms:
                output_file.write(str(psm) + "\n")


class PeptideVariant:
    def __init__(self, variant_sequence):
        self.variant_sequence = variant_sequence
        self.psms = []
        self.fdr = -1
        self.local_fdr = -1

    @staticmethod
    def output_header():
        return "variant_sequence\tscore\tdecoy\tFDR\tfilename\tscan\tcharge\tppm_error\tfragmentation_method\tcollision_energy\tnumberpsms\tstrippedsequence\tpeptidefdr\tlocalpeptidefdr\tlength"

    def __str__(self):
        max_psm = self.get_best_psm()
        return "%s\t%d\t%s\t%s\t%s\t%s" %  (str(max_psm), len(self.psms), self.get_stripped_sequence(), str(self.fdr), str(self.local_fdr), str(len(self.get_stripped_sequence())))

    def add_psm(self, psm_object):
        self.psms.append(psm_object)

    def is_decoy(self):
        return self.psms[0].is_decoy()

    def get_charge(self):
        return self.psms[0].charge

    def sorting_value(self):
        max_score = -10.0
        for psm in self.psms:
            max_score = max(psm.sorting_value(), max_score)
        return max_score

    def get_best_psm(self):
        max_score = -100
        max_psm = None
        for psm in self.psms:
            if psm.sorting_value() > max_score:
                max_score = psm.sorting_value()
                max_psm = psm
        return max_psm

    def get_spectrum_count(self):
        return len(self.psms)

    def get_stripped_sequence(self):
        sequence = self.variant_sequence
        p = re.compile('\W|\d')
        sequence = p.sub("", sequence)
        return sequence

    def sequence_length(self):
        return len(self.get_stripped_sequence())

    #Research-y Portion

###
 # Class to hold a set of library peptides
###
class PeptideVariantSet:
    def __init__(self, name):
        self.name = name
        self.peptide_list = []
        self.peptide_map = {}

    def __len__(self):
        return len(self.peptide_list)

    def get_total_spectra_count(self):
        return sum(self.get_spectra_count_list())
        total_ms_ms_count = 0
        for variant in self.peptide_list:
            total_ms_ms_count += len(variant.psms)
        return total_ms_ms_count

    #Get total peptides regardless of modifications
    def get_total_unique_sequence_count(self):
        return len(self.get_unique_sequences())

    def get_unique_sequences_spectrum_count_map(self):
        sequence_map = {}
        for variant in self.peptide_list:
            sequence = variant.variant_sequence
            p = re.compile('\W|\d')
            sequence = p.sub("", sequence)
            if not sequence in sequence_map:
                sequence_map[sequence] = 0
            sequence_map[sequence] += variant.get_spectrum_count()

        return sequence_map

    def get_unique_sequences(self):
        sequence_map = {}
        for variant in self.peptide_list:
            sequence = variant.variant_sequence
            p = re.compile('\W|\d')
            sequence = p.sub("", sequence)
            sequence_map[sequence] = 1

        return sequence_map.keys()

    #Returns a list of spectral counts for each variant
    def get_spectra_count_list(self):
        ms_ms_count_list = []
        for variant in self.peptide_list:
            ms_ms_count_list.append(len(variant.psms))
        return ms_ms_count_list

    def add_psms_set(self, psm_set):
        self.add_psms_list(psm_set.psms)

    def add_psms_list(self, psm_list):
        for psm in psm_list:
            if not(psm.annotation in self.peptide_map):
                peptide_variant = PeptideVariant(psm.annotation)
                self.peptide_list.append(peptide_variant)
                self.peptide_map[psm.annotation] = peptide_variant
            self.peptide_map[psm.annotation].add_psm(psm)

    #Appending a variant set
    def add_variant_set(self, variant_set):
        for variant in variant_set.peptide_list:
            if not(variant.variant_sequence in self.peptide_map):
                self.peptide_list.append(variant)
                self.peptide_map[variant.variant_sequence] = variant
            else:
                self.add_psms_list(variant.psms)

    def add_variant(self, variant_obj):
        if not(variant_obj.variant_sequence in self.peptide_map):
            self.peptide_list.append(variant_obj)
            self.peptide_map[variant_obj.variant_sequence] = variant_obj
        else:
            self.add_psms_list(variant_obj.psms)

    def remove_variant(self, variant_obj):
        self.peptide_list.remove(variant_obj)
        del self.peptide_map[variant_obj.variant_sequence]

    def filter_to_fdr(self, fdr):
        filtered_peptides = filter_psm_fdr(self.peptide_list, fdr)
        print("Filtered " + str(len(self.peptide_list)) + " to " + str(len(filtered_peptides)))
        self.peptide_list = filtered_peptides
        self.peptide_map = {}
        for variant in self.peptide_list:
            self.peptide_map[variant.variant_sequence] = variant

    def filter_to_fdr_by_length(self, fdr):
        output_peptides = []
        peptide_length_map = {}
        for peptide_obj in self.peptide_list:
            peptide_length = len(peptide_obj.get_stripped_sequence())
            if not peptide_length in peptide_length_map:
                peptide_length_map[peptide_length] = []
            peptide_length_map[peptide_length].append(peptide_obj)

        for peptide_length in peptide_length_map:
            filtered_peptides = filter_psm_fdr(peptide_length_map[peptide_length], fdr)
            print("Filtered Length " + str(peptide_length) + " " + str(len(peptide_length_map[peptide_length])) + " to " + str(len(filtered_peptides)))
            output_peptides += filtered_peptides
        self.peptide_list = output_peptides
        self.peptide_map = {}
        for variant in self.peptide_list:
            self.peptide_map[variant.variant_sequence] = variant

    def filter_to_local_fdr_by_length(self, fdr):
        output_peptides = []
        peptide_length_map = {}
        for peptide_obj in self.peptide_list:
            peptide_length = len(peptide_obj.get_stripped_sequence())
            if not peptide_length in peptide_length_map:
                peptide_length_map[peptide_length] = []
            peptide_length_map[peptide_length].append(peptide_obj)

        for peptide_length in peptide_length_map:
            filtered_peptides = filter_psm_local_fdr(peptide_length_map[peptide_length], fdr)
            print("Filtered Length " + str(peptide_length) + " " + str(len(peptide_length_map[peptide_length])) + " to " + str(len(filtered_peptides)))
            output_peptides += filtered_peptides
        self.peptide_list = output_peptides
        self.peptide_map = {}
        for variant in self.peptide_list:
            self.peptide_map[variant.variant_sequence] = variant

    def calculate_fdr(self):
        running_target_count = 0
        running_decoy_count = 0
        for psm in self.peptide_list:
            if psm.is_decoy() == 0:
                running_target_count += 1
            else:
                running_decoy_count += 1

        current_fdr = float(running_decoy_count) / float(running_target_count)
        return current_fdr

    def write_output(self, output_file):
        output_file.write(PeptideVariant.output_header() + "\n")
        for variant in self.peptide_list:
            output_file.write(str(variant) + "\n")


###
 # Class to hold a set of Sequence Peptides
###
class PeptideSequenceSet:
    def __init__(self, name):
        self.name = name
        self.peptide_list = []
        self.peptide_map = {}

    def __len__(self):
        return len(self.peptide_list)

    def add_psms_list(self, psm_list):
        for psm in psm_list:
            sequence = psm.get_stripped_sequence()
            if not(sequence in self.peptide_map):
                peptide_sequence = PeptideVariant(sequence)
                self.peptide_list.append(peptide_sequence)
                self.peptide_map[sequence] = peptide_sequence
            self.peptide_map[sequence].add_psm(psm)

    def calculate_fdr(self):
        running_target_count = 0
        running_decoy_count = 0
        for psm in self.peptide_list:
            if psm.is_decoy() == 0:
                running_target_count += 1
            else:
                running_decoy_count += 1

        current_fdr = float(running_decoy_count) / float(running_target_count)
        return current_fdr


###
 # Parsing peptide string into a list of literals including mods in the string
###
def get_peptide_modification_list_inspect_format(peptide):
    return re.findall('[^A-Z]*[A-Z][^A-Z]*', peptide)



def create_theoretical_peak_map(peptide, ion_type_list, charge_set=[1]):
    amino_acid_list = get_peptide_modification_list_inspect_format(peptide)
    #print(amino_acid_list)

    only_letters_list = [letter for letter in peptide if letter.isalpha()]

    only_mods_mass_add_list = []
    for amino_acid in amino_acid_list:
        mod_mass_to_add = 0.0
        mod_strings_tokenized = re.findall('[+-][0-9]*.[0-9]*', re.sub("[A-Z]", "", amino_acid))
        for mod_tokenized in mod_strings_tokenized:
            mod_mass_to_add += float(mod_tokenized)
        only_mods_mass_add_list.append(mod_mass_to_add)

    ion_to_mass_mapping = {}
    #print(peptide)
    #print(only_mods_mass_add_list)
    for charge in charge_set:
        for ion_type in ion_type_list:
            #print(ion_type)
            iso_topic_added_mass = 0.0
            real_ion_type = ion_type
            if ion_type[-4:] == "-iso":
                iso_topic_added_mass = 1.007276 / float(charge)
                real_ion_type = ion_type[:-4]

            for i in range(len(amino_acid_list)):
                peak_mass = 0.0
                if real_ion_type[0] in "abc":
                    peak_annotation = ion_type + ":" + str(i+1) + ":" + str(charge)
                    peak_mass = mass.fast_mass("".join(only_letters_list[:i+1]), ion_type=real_ion_type, charge=charge) + sum(only_mods_mass_add_list[:i+1])/(float(charge)) + iso_topic_added_mass
                    #print(ion_type, i, charge, peak_mass, real_ion_type)
                else:
                    peak_annotation = ion_type + ":" + str(len(amino_acid_list) - i) + ":" + str(charge)
                    peak_mass = mass.fast_mass("".join(only_letters_list[i:]), ion_type=real_ion_type, charge=charge) + sum(only_mods_mass_add_list[i:])/(float(charge)) + iso_topic_added_mass
                    #print(ion_type, i, charge, peak_mass)
                ion_to_mass_mapping[peak_annotation] = peak_mass

    return ion_to_mass_mapping

def calculate_theoretical_peptide_mass(peptide_sequence, charge):
    amino_acid_list = get_peptide_modification_list_inspect_format(peptide_sequence)
    only_letters_list = [letter for letter in peptide_sequence if letter.isalpha()]

    only_mods_mass_add_list = []

    for amino_acid in amino_acid_list:
        mod_mass_to_add = 0.0
        mod_strings_tokenized = re.findall('[+-][0-9]*.[0-9]*', re.sub("[A-Z]", "", amino_acid))
        for mod_tokenized in mod_strings_tokenized:
            mod_mass_to_add += float(mod_tokenized)
        only_mods_mass_add_list.append(mod_mass_to_add)

    total_peptide_mass = (mass.fast_mass("".join(only_letters_list), charge=charge) + sum(only_mods_mass_add_list)/(float(charge)))

    return total_peptide_mass



#Returns both annotated and unannotated peaks
def extract_annotated_peaks(ion_peak_mapping, peak_list, tolerance):
    extracted_peaks = []
    unannotated_peaks = []
    for peak in peak_list:
        mass = peak[0]
        isAnnotated = False
        for ion_peak in ion_peak_mapping:
            if abs(mass - ion_peak_mapping[ion_peak]) < tolerance:
                #extracted_peaks.append(peak)
                isAnnotated = True
                break
        if isAnnotated:
            extracted_peaks.append(peak)
        else:
            unannotated_peaks.append(peak)
    return extracted_peaks, unannotated_peaks

def calculated_explained_intensity(peaks, max_charge, peptide, tolerance):
    if len(peaks) == 0:
        return 0.0

    charge_set = range(1, max_charge + 1)
    theoretical_peaks = create_theoretical_peak_map(peptide, ["b",  "b-iso", "y", "y-iso", "b-H2O", "b-NH3", "y-H2O", "y-NH3", "a"], charge_set=charge_set)
    annotated_peaks, unannotated_peaks = extract_annotated_peaks(theoretical_peaks, peaks, tolerance)

    sum_annotated_peaks = sum(x[1] for x in annotated_peaks)
    sum_unannotated_peaks = sum(x[1] for x in unannotated_peaks)

    return sum_annotated_peaks / (sum_annotated_peaks + sum_unannotated_peaks)

def calculated_number_annotated_peaks(peaks, max_charge, peptide, tolerance):
    charge_set = range(1, max_charge + 1)
    theoretical_peaks = create_theoretical_peak_map(peptide, ["b",  "b-iso", "y", "y-iso", "b-H2O", "b-NH3", "y-H2O", "y-NH3", "a"], charge_set=charge_set)
    annotated_peaks, unannotated_peaks = extract_annotated_peaks(theoretical_peaks, peaks, tolerance)

    max_peak_intensity = 0.0
    for peak in peaks:
        max_peak_intensity = max(max_peak_intensity, peak[1])

    total_peaks_annotated = 0
    for annotated_peak in annotated_peaks:
        peak_intensity = annotated_peak[1]
        fraction_of_max = peak_intensity/max_peak_intensity
        if fraction_of_max > 0.05:
            total_peaks_annotated += 1

    return total_peaks_annotated



###
 # Takes as input a filename
 # Returns a list of PSM
###
def parse_MSGF_tsvfile(filename):
    rows, table_data = ming_fileio_library.parse_table_with_headers(filename)

    scan_header = "Scan#"
    peptide_header = "Peptide"
    protein_header = "Protein"
    score_header = "P-value"
    filename_header = "#SpecFile"
    charge_header = "Charge"
    ppm_error_header = "PMError(ppm)"
    da_pm_error_header = "PMError(Da)"
    precursor_header = "Precursor"
    fragmethod_header = "FragMethod"

    parse_da_error = False
    if not ppm_error_header in table_data:
        parse_da_error = True


    decoy_indicator = "REV_"

    psm_list = []

    for i in range(rows):
        scan = table_data[scan_header][i]
        peptide = table_data[peptide_header][i]
        protein = table_data[protein_header][i]
        score = -math.log10(float(table_data[score_header][i]))
        #print table_data[score_header][i] + "\t" + str(score)
        filename = table_data[filename_header][i]
        charge = int(table_data[charge_header][i])
        frag_method = table_data[fragmethod_header][i]
        if parse_da_error:
            ppm_error = float(table_data[da_pm_error_header][i])/float(table_data[precursor_header][i]) * 1000000
        else:
            ppm_error = float(table_data[ppm_error_header][i])
        decoy = 0

        #Stripping peptide dots
        if peptide[1] == "." and peptide[-2] == ".":
            peptide = peptide[2:-2]


        if protein.find(decoy_indicator) != -1:
            decoy = 1

        #Adding charge state to peptide name
        peptide += "." + str(charge)

        new_psm = PSM(filename, scan, peptide, score, decoy, protein, charge, frag_method=frag_method)
        new_psm.ppm_error = ppm_error
        psm_list.append(new_psm)

    return psm_list

def parse_MSGFPlus_tsvfile(filename):
    rows, table_data = ming_fileio_library.parse_table_with_headers(filename)

    scan_header = "ScanNum"
    peptide_header = "Peptide"
    protein_header = "Protein"
    score_header = "EValue"
    filename_header = "#SpecFile"
    charge_header = "Charge"
    ppm_error_header = "PrecursorError(ppm)"
    da_pm_error_header = "PrecursorError(Da)"
    precursor_header = "Precursor"
    frag_method_header = "FragMethod"

    parse_da_error = False
    if not ppm_error_header in table_data:
        parse_da_error = True


    decoy_indicator = "XXX_"

    psm_list = []

    for i in range(rows):
        scan = table_data[scan_header][i]
        peptide = table_data[peptide_header][i]
        protein = table_data[protein_header][i]
        score = -math.log10(float(table_data[score_header][i]))
        #print table_data[score_header][i] + "\t" + str(score)
        filename = table_data[filename_header][i]
        charge = int(table_data[charge_header][i])
        frag_method = table_data[frag_method_header][i]
        if parse_da_error:
            ppm_error = float(table_data[da_pm_error_header][i])/float(table_data[precursor_header][i]) * 1000000
        else:
            ppm_error = float(table_data[ppm_error_header][i])
        decoy = 0

        #Stripping peptide dots
        if peptide[1] == "." and peptide[-2] == ".":
            peptide = peptide[2:-2]


        if protein.find(decoy_indicator) != -1:
            decoy = 1

        #Adding charge state to peptide name
        peptide += "." + str(charge)

        new_psm = PSM(filename, scan, peptide, score, decoy, protein, charge)
        new_psm.ppm_error = ppm_error
        new_psm.frag_method = frag_method
        psm_list.append(new_psm)

    return psm_list

###
 # Takes as input a filename for a variant file output by this code
###
def parse_variant_file(filename):
    rows, table_data = ming_fileio_library.parse_table_with_headers(filename)

    psm_list = []
    for i in range(rows):
        filename = table_data["filename"][i]
        scan = int(table_data["scan"][i])
        score = float(table_data["score"][i])
        decoy = int(table_data["decoy"][i])
        variant_sequence = table_data["variant_sequence"][i]
        charge = 0
        if "charge" in table_data:
            charge = int(table_data["charge"][i])
        else:
            charge = int(variant_sequence.split(".")[-1])
        protein = "NONE"

        if "unmangled_name" in table_data:
            filename = table_data["unmangled_name"][i]

        new_psm = PSM(filename, scan, variant_sequence, score, decoy, protein, charge)
        psm_list.append(new_psm)

    return psm_list

###
 # Takes as input a filename for a variant file output by this code
###
def parse_psm_file(filename, load_extra_metadata=False):
    rows, table_data = ming_fileio_library.parse_table_with_headers(filename)

    known_headers = ["filename", "scan", "score", "decoy", "sequence", "charge", "ppm_error", "unmangled_name", "FDR", "collision_energy", "FragMethod"]
    extra_metadata_headers = set(table_data.keys()).difference(set(known_headers))

    psm_list = []
    for i in range(rows):
        filename = table_data["filename"][i]
        scan = int(table_data["scan"][i])
        score = float(table_data["score"][i])
        decoy = int(table_data["decoy"][i])
        variant_sequence = table_data["sequence"][i]
        charge = int(table_data["charge"][i])
        ppm_error = float(table_data["ppm_error"][i])
        fdr = float(table_data["FDR"][i])
        fragmentation_method = "N/A"
        if "FragMethod" in table_data:
            fragmentation_method = table_data["FragMethod"][i]
        collision_energy = 0.0
        if "collision_energy" in table_data:
            collision_energy = float(table_data["collision_energy"][i])
        protein = "NONE"

        if "unmangled_name" in table_data:
            filename = table_data["unmangled_name"][i]

        new_psm = PSM(filename, scan, variant_sequence, score, decoy, protein, charge)
        new_psm.ppm_error = ppm_error
        new_psm.fdr = fdr
        new_psm.frag_method = fragmentation_method
        new_psm.collision_energy = collision_energy

        if load_extra_metadata:
            extra_metadata = {}
            for header in extra_metadata_headers:
                extra_metadata[header] = table_data[header][i]
            new_psm.extra_metadata = extra_metadata

        psm_list.append(new_psm)

    return psm_list

###
 # Takes as input a filename for a variant file output by this code
###
def parse_msplit_file(filename, load_extra_metadata=False):
    rows, table_data = ming_fileio_library.parse_table_with_headers(filename)

    known_headers = ["filename", "scan", "score", "decoy", "sequence", "charge", "ppm_error", "unmangled_name", "FDR", "collision_energy", "FragMethod"]
    extra_metadata_headers = set(table_data.keys()).difference(set(known_headers))

    psm_list = []
    for i in range(rows):
        filename = table_data["internalFilename"][i]
        scan = int(table_data["Scan#"][i])
        score = table_data["cosine(M,A)"][i]
        decoy = 0
        variant_sequence = table_data["Annotation"][i]
        charge = table_data["Charge"][i]
        protein = "NONE"

        new_psm = PSM(filename, scan, variant_sequence, score, decoy, protein, charge)
        psm_list.append(new_psm)
    return psm_list

def calculate_fdr_by_length(input_psms):
    peptide_length_map = {}
    for psm in input_psms:
        peptide_length = len(psm.get_stripped_sequence())
        if not peptide_length in peptide_length_map:
            peptide_length_map[peptide_length] = []
        peptide_length_map[peptide_length].append(psm)

    for peptide_length in peptide_length_map:
        calculate_psm_fdr(peptide_length_map[peptide_length])
    return input_psms

def calculate_psm_fdr(input_psms):
    input_psms = sorted(input_psms, key=lambda psm: psm.sorting_value(), reverse=True)

    running_target_count = 1
    running_decoy_count = 0

    output_psms = []

    for psm in input_psms:
        if psm.is_decoy() == 0:
            running_target_count += 1
        else:
            running_decoy_count += 1

        current_fdr = float(running_decoy_count) / float(running_target_count)

        psm.fdr = current_fdr

    #Properly finding the min q value for PSM
    min_fdr = 1
    input_psms.reverse()
    for psm in input_psms:
        min_fdr = min(min_fdr, psm.fdr)
        psm.fdr = min_fdr

    return input_psms

###
 # Filtering PSM results so that the returned set is at the
 # prescribed FDR
###
def filter_psm_fdr(input_psms, fdr_percentage):
    #TODO Add Sorting
    #Sorting
    #print "Sorting shit to " + str(fdr_percentage*100) + "%"
    #input_psms = sorted(input_psms, key=PSM.sorting_value)
    input_psms = sorted(input_psms, key=lambda psm: psm.sorting_value(), reverse=True)

    running_target_count = 1
    running_decoy_count = 0

    output_psms = []

    for psm in input_psms:
        if psm.is_decoy() == 0:
            running_target_count += 1
        else:
            running_decoy_count += 1

        current_fdr = float(running_decoy_count) / float(running_target_count)

        psm.fdr = current_fdr

    #Properly finding the min q value for PSM
    min_fdr = 1
    input_psms.reverse()
    for psm in input_psms:
        min_fdr = min(min_fdr, psm.fdr)
        psm.fdr = min_fdr

    input_psms.reverse()
    #for i in range(len(input_psms)):
    #    index_to_check = len(input_psms) - i - 1
    #    min_fdr = min(min_fdr, input_psms[index_to_check].fdr)
    #    input_psms[index_to_check].fdr = min_fdr

    for psm in input_psms:
        if psm.fdr < fdr_percentage:
            output_psms.append(psm)

    return output_psms

def filter_synthetic_psms(input_psms, target_filename_list, decoy_filename_list, fdr=0.00000000001):
    target_filelist_psm_list = []
    decoy_filelist_psm_list = []

    for psm in input_psms:
        filename = psm.filename
        if filename in target_filename_list:
            target_filelist_psm_list.append(psm)
        else:
            psm.decoy = 1
            decoy_filelist_psm_list.append(psm)

    print(len(target_filelist_psm_list), len(decoy_filelist_psm_list))

    #Now lets select the appropriate number of decoys
    random.seed(0)
    random.shuffle(decoy_filelist_psm_list)
    total_number_of_targets = len(target_filelist_psm_list)
    decoy_filelist_psm_list = decoy_filelist_psm_list[:total_number_of_targets]
    print(len(target_filelist_psm_list), len(decoy_filelist_psm_list))

    merged_psm_list = target_filelist_psm_list + decoy_filelist_psm_list

    return filter_psm_fdr(merged_psm_list, fdr)

    #
    #
    # merged_psm_list = sorted(merged_psm_list, key=lambda psm: psm.sorting_value(), reverse=True)
    #
    # output_psms = []
    #
    # for psm in merged_psm_list:
    #     if psm.is_decoy() == 1:
    #         break
    #     else:
    #         output_psms.append(psm)
    #
    # return output_psms

def get_synthetic_decoy_psms(input_psms, target_filename_list, decoy_filename_list):
    target_filelist_psm_list = []
    decoy_filelist_psm_list = []

    for psm in input_psms:
        filename = psm.filename
        if filename in target_filename_list:
            target_filelist_psm_list.append(psm)
        else:
            psm.decoy = 1
            decoy_filelist_psm_list.append(psm)

    print(len(target_filelist_psm_list), len(decoy_filelist_psm_list))

    #Now lets select the appropriate number of decoys
    random.seed(0)
    random.shuffle(decoy_filelist_psm_list)
    total_number_of_targets = len(target_filelist_psm_list)
    decoy_filelist_psm_list = decoy_filelist_psm_list[:total_number_of_targets]

    print(len(decoy_filelist_psm_list))

    return decoy_filelist_psm_list


###
 # Filtering PSM results so that the returned set is at the
 # prescribed local FDR
###
def filter_psm_local_fdr(input_psms, fdr_percentage):
    local_window_size = 500

    input_psms = sorted(input_psms, key=lambda psm: psm.sorting_value(), reverse=True)

    running_target_count = 1
    running_decoy_count = 0

    recent_target_numbers = []
    recent_decoy_numbers = []

    output_psms = []

    for psm in input_psms:
        if psm.is_decoy() == 0:
            recent_target_numbers.append(1)
            recent_decoy_numbers.append(0)
            running_target_count += 1
        else:
            recent_decoy_numbers.append(1)
            recent_target_numbers.append(0)
            running_decoy_count += 1

        recent_target_numbers = recent_target_numbers[-local_window_size:]
        recent_decoy_numbers = recent_decoy_numbers[-local_window_size:]

        local_fdr = float(sum(recent_decoy_numbers)) / float(sum(recent_target_numbers))
        current_fdr = float(running_decoy_count) / float(running_target_count)
        #print(local_fdr, current_fdr)

        psm.local_fdr = local_fdr
        psm.fdr = current_fdr

    #Properly finding the min q value for PSM
    min_fdr = 1
    input_psms.reverse()
    for psm in input_psms:
        min_fdr = min(min_fdr, psm.local_fdr)
        psm.local_fdr = min_fdr

    input_psms.reverse()
    #for i in range(len(input_psms)):
    #    index_to_check = len(input_psms) - i - 1
    #    min_fdr = min(min_fdr, input_psms[index_to_check].fdr)
    #    input_psms[index_to_check].fdr = min_fdr

    for psm in input_psms:
        if psm.local_fdr < fdr_percentage:
            output_psms.append(psm)

    return output_psms

def strip_sequence(input_sequence):
    p = re.compile('\W|\d')
    sequence = p.sub("", input_sequence)
    return sequence

def remove_charges_from_annotation(annotation):
    if annotation[-2] == ".":
        return annotation[:-2]
    return annotation
