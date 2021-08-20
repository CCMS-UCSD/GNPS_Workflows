#!/usr/bin/env nextflow

params.inputspectra = ''
params.annotation_table = ''
params.workflowParameters = ''

_spectra_ch = Channel.fromPath( params.inputspectra )
_annotation_ch = Channel.fromPath( params.annotation_table )
_params_ch = Channel.fromPath( params.workflowParameters )

_annotation_ch.into{_annotation_ch1;_annotation_ch2;_annotation_ch3}
_params_ch.into{_params_ch1;_params_ch2}

TOOL_FOLDER = "$baseDir/bin"
params.publishdir = "nf_output"

process validateBatch {
    publishDir "$params.publishdir", mode: 'copy'
    
    input:
    file annotation_file from _annotation_ch3

    output:

    """
    python $TOOL_FOLDER/validate_batch.py \
        "$annotation_file"
    """
}

process createLib {
    publishDir "$params.publishdir", mode: 'copy'
    
    input:
    file annotation_file from _annotation_ch1
    file inputspectra from _spectra_ch
    file workflow_params from _params_ch1

    output:

    """
    python $TOOL_FOLDER/create_lib_wrapper.py \
        "$workflow_params" \
        "$inputspectra" \
        "$annotation_file" \
        result.tsv \
        new_results.tsv \
        new_spectra.mgf \
        $TOOL_FOLDER/main_execmodule
    """
}

process formatResult {
    publishDir "$params.publishdir", mode: 'copy'
    
    input:
    file annotation_file from _annotation_ch2
    file workflow_params from _params_ch2

    output:

    """
    python $TOOL_FOLDER/formatresults.py \
        "$annotation_file" \
        "$workflow_params" \
        formattedresult.tsv
    """

}