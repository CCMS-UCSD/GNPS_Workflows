def validate(peak_string, min_matched_peaks):
    counter = 0

    peaks_lines = spectrum_string.split("\n")

    for peak_line in peak_lines:
        try:
            mass, inten = peak_entry.split()
        except:
            print("Error: m/z and intensity not separated properly")
            return 1

        #making sure the input is a number with no additional characters
        try:
            float(mass)
        except:
            print("Error: m/z is not numeric")
            return 1

        try:
            float(inten)
        except:
            print("Error: intensity is not numeric")
            return 1

        #making sure minimum peak criteria is met
        counter += 1

    if counter < min_matched_peaks:
        print('Error: Number of peaks in spectrum is less than the parameter "Minimum Matched Peaks"')
        return 1

    return 0


