#!/usr/bin/env nextflow

params.inputspectra = ''
params.annotation_table = ''
params.workflowParameters = ''

_spectra_ch = Channel.fromPath( params.inputspectra )
_annotation_ch = Channel.fromPath( params.annotation_table )
_params_ch = Channel.fromPath( params.workflowParameters )

TOOL_FOLDER = "$baseDir/bin"
params.publishdir = "nf_output"

process validateBatch {
    publishDir "$params.publishdir", mode: 'copy'
    
    input:
    file annotation_file from _annotation_ch

    output:

    """
    python $TOOL_FOLDER/validate_batch.py \
        "$annotation_file"
    """
}

process createLib {
    publishDir "$params.publishdir", mode: 'copy'
    
    input:
    file annotation_file from _annotation_ch
    file inputspectra from _spectra_ch
    file workflow_params from _params_ch

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
    file annotation_file from _annotation_ch
    file inputspectra from _spectra_ch
    file workflow_params from _params_ch

    output:

    """
    python $TOOL_FOLDER/formatresults.py \
        "$annotation_file" \ 
        "$workflow_params" \ 
        formattedresult.tsv
    """

}