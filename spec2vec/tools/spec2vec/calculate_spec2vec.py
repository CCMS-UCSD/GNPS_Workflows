import os
import sys
import gensim
import numpy as np
import pandas as pd

from matchms.filtering import normalize_intensities
from matchms.filtering import require_minimum_number_of_peaks
from matchms.filtering import select_by_mz
from matchms.filtering import select_by_relative_intensity
from matchms.filtering import reduce_to_number_of_peaks
from matchms.filtering import add_losses
from matchms.importing import load_from_mgf
from matchms import calculate_scores_parallel


from spec2vec import Spec2VecParallel
from spec2vec import SpectrumDocument

import argparse

def post_process(s):
    s = normalize_intensities(s)
    s = select_by_mz(s, mz_from=0, mz_to=1000)
    s = require_minimum_number_of_peaks(s, n_required=10)
    s = reduce_to_number_of_peaks(s, n_required=10, ratio_desired=0.5)
    if s is None:
        return None
    s_remove_low_peaks = select_by_relative_intensity(s, intensity_from=0.001)
    if len(s_remove_low_peaks.peaks) >= 10:
        s = s_remove_low_peaks
        
    s = add_losses(s, loss_mz_from=5.0, loss_mz_to=200.0)
    return s

def main():
    parser = argparse.ArgumentParser(description='Creating Spec2Vec Pairs')
    parser.add_argument('input_mgf', help='input_mgf')
    parser.add_argument('output_pairs', help='output_pairs')
    parser.add_argument('model_file', help='model_file')
    args = parser.parse_args()

    spectra = load_from_mgf(args.input_mgf)

    filtered_spectra = [post_process(s) for s in spectra]

    # Omit spectrums that didn't qualify for analysis
    filtered_spectra = [s for s in filtered_spectra if s is not None]

    # Create spectrum documents
    query_documents = [SpectrumDocument(s, n_decimals=2) for s in filtered_spectra]

    #DEBUG
    #query_documents = query_documents[:100]

    # Loading the model
    model = gensim.models.Word2Vec.load(args.model_file)

    # Define similarity_function
    spec2vec = Spec2VecParallel(model=model, intensity_weighting_power=0.5,
                            allowed_missing_percentage=80.0)


    print("total documents", len(query_documents))
    scores = calculate_scores_parallel(query_documents, query_documents, spec2vec).scores

    number_of_spectra = len(query_documents)

    output_scores_list = []
    for i in range(number_of_spectra):
        for j in range(number_of_spectra):
            if i <= j:
                continue

            i_spectrum = filtered_spectra[i]
            j_spectrum = filtered_spectra[j]

            sim = scores[i][j]

            if sim < 0.8:
                continue

            score_dict = {}
            score_dict["filename"] = args.input_mgf
            score_dict["CLUSTERID1"] = i_spectrum.metadata["scans"]
            score_dict["CLUSTERID2"] = j_spectrum.metadata["scans"]
            score_dict["Cosine"] = sim
            score_dict["mz1"] = i_spectrum.metadata["pepmass"][0]
            score_dict["mz2"] = j_spectrum.metadata["pepmass"][0]
            score_dict["DeltaMZ"] = score_dict["mz2"] - score_dict["mz1"]
            score_dict["EdgeAnnotation"] = "Spec2Vec"
            

            output_scores_list.append(score_dict)

    # Saving Data Out
    pd.DataFrame(output_scores_list).to_csv(args.output_pairs, sep="\t", index=False)


if __name__ == "__main__":
    main()
