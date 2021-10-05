#!/usr/bin/env nextflow

params.input_library = ''

params.input_format = ''
params.pi = ''
params.collector = ''

_library_ch = Channel.fromPath( params.input_library )

TOOL_FOLDER = "$baseDir/bin"
params.publishdir = "nf_output"

process convertLibrary {
    publishDir "$params.publishdir", mode: 'copy'

    input:
    file library_file from _library_ch.first()

    output:
    file "output_folder"

    """
    mkdir output_folder -p
    python $TOOL_FOLDER/library_conversion.py \
        -input-library "$library_file" \
        --mgf-file output_folder/converted_library.mgf \
        --csv-file output_folder/converted_library.tsv \
        --libformat "$params.input_format" \
        --pi "$params.pi" \
        --collector "$params.collector"
    """
}
