#!/usr/bin/env nextflow

params.inputspectra = ''
params.workflowParameters = ''

params.type = ''

_spectra_ch = Channel.fromPath( params.inputspectra )
_params_ch = Channel.fromPath( params.workflowParameters )

_params_ch.into{_params_ch1;_params_ch2}

TOOL_FOLDER = "$baseDir/bin"
params.publishdir = "nf_output"

process calculateResults {
    publishDir "$params.publishdir", mode: 'copy'

    input:
    file spectra_folder from _spectra_ch

    output:
    file "result_file.tsv"

    """
    python $TOOL_FOLDER/template_script.py \
        "$spectra_folder" \
        "result_file.tsv"
    """
}
