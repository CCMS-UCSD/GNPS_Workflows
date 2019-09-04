# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 18:20:42 2017

@author: Dr. Ivan Laponogov
"""
from proc.procconfig import IntraPAlign_options, NoiseFilter_options, ProfAlign_options, PeakDetection_options, TICvis_options;
from proc.utils.pipeline import ProcessingPipeLine;
import os;
import subprocess;

    
GCMS_pipeline_default_blocks = [
    ['python ./proc/preproc/intrapalign.py', IntraPAlign_options, False], #$dbfilepath --h5writepath 'sp2D'
    ['python ./proc/preproc/noisefilter.py', NoiseFilter_options, False],#"$dbfilepath" --h5readpath 'sp2D' --h5writepath 'spproc2D'
    ['python ./proc/preproc/interpalign.py', ProfAlign_options, False],#"$dbfilepath" --minsegwidth 30 --maxpeakshift 15 --h5readpath 'spproc2D' --h5writepath 'spal2D'
    ['python ./proc/preproc/peakdetect.py', PeakDetection_options, False],#"$dbfilepath" --h5readpath spal2D
    ['python ./proc/vis/vistic.py', TICvis_options, True]  # "$dbfilepath" --h5readpath '/spal2D' --method 'bokeh' 
]    

GCMS_pipeline_default_globals = ['dbfilename']
GCMS_pipeline_default_externals = ['dbfilename']
GCMS_pipeline_default_allowed_input_data = set(['GCMS_Raw']);

GCMS_pipeline_default = ProcessingPipeLine();

GCMS_pipeline_default.configure('Default GC-MS raw data processing',
                                           GCMS_pipeline_default_blocks,
                                           GCMS_pipeline_default_globals,
                                           GCMS_pipeline_default_externals,
                                           GCMS_pipeline_default_allowed_input_data);


default_pipelines = [GCMS_pipeline_default];


def import_pipelines(inpath):
    pass



def get_allowed_pipelines(available_pipelines, input_data_type):
    
    result = [];

    for pipeline in available_pipelines:
        if input_data_type in pipeline.allowed_input_data:
            result.append(pipeline);

    return result


                                           
if __name__ == '__main__':
    cml = GCMS_pipeline_default.get_command_lines();
    print(cml);
    
    html_block = GCMS_pipeline_default.get_view(True);
    
    with open('e:/WebServer/Apache24/htdocs/testhtmltree/index.html', 'w') as fout:
        fout.write(html_block);
        
        
        
    
    
    