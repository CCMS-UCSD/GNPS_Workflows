#!/usr/bin/env nextflow

params.workflowParameters = ''

_params_ch = Channel.fromPath( params.workflowParameters )

TOOL_FOLDER = "$baseDir/bin"
params.publishdir = "nf_output"

process calculateResults {
    publishDir "$params.publishdir", mode: 'copy'

    input:
    file parameters from _params_ch

    output:
    file "specs_ms.mgf"
    file "results.tsv"

    """
    python $TOOL_FOLDER/download_usi.py \
        "$parameters" \
        "specs_ms.mgf" \
        "results.tsv"
    """
}
