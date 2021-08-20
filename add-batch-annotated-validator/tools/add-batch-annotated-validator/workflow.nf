#!/usr/bin/env nextflow

params.inputspectra = ''
params.annotation_table = ''
params.workflowParameters = ''

//_spectra_ch = Channel.fromPath( params.inputspectra )
_annotation_ch = Channel.fromPath( params.annotation_table )

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