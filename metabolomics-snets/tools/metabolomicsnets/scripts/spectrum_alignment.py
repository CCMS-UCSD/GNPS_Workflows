import math
import bisect
from collections import namedtuple


Match = namedtuple('Match', ['peak1', 'peak2', 'score'])
Peak = namedtuple('Peak',['mz','intensity'])
Alignment = namedtuple('Alignment', ['peak1', 'peak2'])

def convert_to_peaks(peak_tuples):
    #using the splat we can handle both size 2 lists and tuples
    return [Peak(*p) for p in peak_tuples]

def sqrt_normalize_spectrum(spectrum):
    output_spectrum = []
    intermediate_output_spectrum = []
    acc_norm = 0.0
    for s in spectrum:
        sqrt_intensity = math.sqrt(s.intensity)
        intermediate_output_spectrum.append(Peak(s.mz,sqrt_intensity))
        acc_norm += s.intensity
    normed_value = math.sqrt(acc_norm)
    for s in intermediate_output_spectrum:
        output_spectrum.append(Peak(s.mz,s.intensity/normed_value))
    return output_spectrum

#reimplementation of find_match_peaks, but much more efficient
# Assumes that shift is equal to spec1 - spec2
def find_match_peaks_efficient(spec1, spec2, shift, tolerance):
    adj_tolerance =  tolerance + 0.000001
    spec2_mass_list = []

    for i,peak in enumerate(spec2):
        spec2_mass_list.append(peak.mz)

    alignment_mapping = []

    for i, peak in enumerate(spec1):
        left_mz_bound = peak.mz - shift - adj_tolerance
        right_mz_bound = peak.mz - shift + adj_tolerance

        left_bound_index = bisect.bisect_left(spec2_mass_list, left_mz_bound)
        right_bound_index = bisect.bisect_right(spec2_mass_list, right_mz_bound)

        for j in range(left_bound_index,right_bound_index):
            alignment_mapping.append(Alignment(i,j))
    return alignment_mapping



# Assumes that shift is equal to spec1 - spec2
def find_match_peaks(spec1,spec2,shift,tolerance):
    adj_tolerance =  tolerance + 0.000001
    low = 0
    high = 0
    alignment_mapping = []
    for i,s1 in enumerate(spec1):
        low = len(spec2)-1
        while low > 0 and (s1.mz - adj_tolerance) < (spec2[low].mz + shift):
            low = low - 1
        while low < len(spec2) and (s1.mz - adj_tolerance) > (spec2[low].mz + shift):
            low = low + 1
        while high < len(spec2) and (s1.mz + adj_tolerance) >= (spec2[high].mz + shift):
            high = high + 1
        for j in range(low,high):
            alignment_mapping.append(Alignment(i,j))
    return alignment_mapping

def alignment_to_match(spec1_n,spec2_n,alignment):
    s1_peak = spec1_n[alignment.peak1].intensity
    s2_peak = spec2_n[alignment.peak2].intensity
    match_score = s1_peak * s2_peak
    return Match(
            peak1 = alignment.peak1,
            peak2 = alignment.peak2,
            score = match_score
    )

###
# This score alignment code will take two spectra
# then it will align the two spectrum given their parent masses
# These spectra are expected to be a list of lists (size two mass, intensity) or a list of tuples
###
def score_alignment(spec1,spec2,pm1,pm2,tolerance):
    if len(spec1) == 0 or len(spec2) == 0:
        return 0.0, []

    spec1_n = sqrt_normalize_spectrum(convert_to_peaks(spec1))
    spec2_n = sqrt_normalize_spectrum(convert_to_peaks(spec2))
    shift = abs(pm1 - pm2)

    #zero_shift_alignments = find_match_peaks(spec1_n,spec2_n,0,tolerance)
    #real_shift_alignments = find_match_peaks(spec1_n,spec2_n,shift,tolerance)

    zero_shift_alignments = find_match_peaks_efficient(spec1_n,spec2_n,0,tolerance)
    real_shift_alignments = []
    if shift > tolerance:
        real_shift_alignments = find_match_peaks_efficient(spec1_n,spec2_n,shift,tolerance)

    zero_shift_match = [alignment_to_match(spec1_n,spec2_n,alignment) for alignment in zero_shift_alignments]
    real_shift_match = [alignment_to_match(spec1_n,spec2_n,alignment) for alignment in real_shift_alignments]

    all_possible_match_scores = zero_shift_match + real_shift_match
    all_possible_match_scores.sort(key=lambda x: x.score, reverse=True)

    reported_alignments = []

    spec1_peak_used = set()
    spec2_peak_used = set()

    total_score = 0.0

    for match in all_possible_match_scores:
        if not match.peak1 in spec1_peak_used and not match.peak2 in spec2_peak_used:
            spec1_peak_used.add(match.peak1)
            spec2_peak_used.add(match.peak2)
            reported_alignments.append(Alignment(match.peak1,match.peak2))
            total_score += match.score

    return total_score, reported_alignments
