import math

#Returns a new list that has a euclidean norm as given
def euclidean_norm(input_list, desired_norm = 1.0):
    new_list = []
    norm = sum([x**2 for x in input_list])
    if norm == 0.0:
        return input_list
    new_list = [math.sqrt((x**2)/norm) for x in input_list]
    return new_list

def dot_product(list_one, list_two):
    return sum([a*b for a,b in zip(list_one,list_two)])

def calculate_noise_level_in_peaks(peaks):
    #Take bottom 25% of peaks
    sorted_peaks = sorted(peaks, key=lambda peak: peak[1])

    number_of_peaks = len(sorted_peaks)
    number_of_peaks_bottom = int(number_of_peaks/4)

    if number_of_peaks_bottom == 0:
        return -1.0

    sum_intensity = 0.0
    for i in range(number_of_peaks_bottom):
        intensity = sorted_peaks[i][1]
        sum_intensity += intensity
    average_noise_intensity = sum_intensity/float(number_of_peaks_bottom)

    return average_noise_intensity

#Determines the number of signal peaks in a set of peaks
def calculate_signal_peaks_in_peaklist(peaks, SNR_Threshold):
    average_noise_intensity = calculate_noise_level_in_peaks(peaks)
    if average_noise_intensity < 0.00001:
        return 0.0

    total_signal_peaks = 0
    for peak in peaks:
        snr_of_peak = peak[1]/average_noise_intensity
        if snr_of_peak > SNR_Threshold:
            total_signal_peaks += 1

    return total_signal_peaks

#Norms it too
def vectorize_peaks(peaks, max_mass, bin_size, sqrt_peaks=True):
    number_of_bins = int(max_mass / bin_size)
    peak_vector = [0.0] * number_of_bins

    for peak in peaks:
        mass = peak[0]
        bin_index = int(mass/bin_size)
        if bin_index > number_of_bins - 1:
            continue
        peak_vector[bin_index] += peak[1]

    acc_norm = 0.0
    if sqrt_peaks == True:
        for bin_index in range(len(peak_vector)):
            sqrt_intensity = math.sqrt(peak_vector[bin_index])
            acc_norm += peak_vector[bin_index]
            peak_vector[bin_index] = sqrt_intensity

        normed_value = math.sqrt(acc_norm)
        for bin_index in range(len(peak_vector)):
            peak_vector[bin_index] = peak_vector[bin_index]/normed_value
    else:
        for bin_index in range(len(peak_vector)):
            acc_norm += peak_vector[bin_index] * peak_vector[bin_index]

        normed_value = math.sqrt(acc_norm)
        for bin_index in range(len(peak_vector)):
            peak_vector[bin_index] = peak_vector[bin_index]/normed_value

    return peak_vector

def unvectorize_peaks(peaks, bin_size):
    output_peaks = []

    for bin_index in range(len(peaks)):
        mass = (float(bin_index)) * bin_size + bin_size/2.0
        intensity = peaks[bin_index]
        output_peaks.append([mass, intensity])

    return output_peaks
