# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 18:20:42 2017

@author: Dr. Ivan Laponogov
"""
import os;
import subprocess;
from proc.utils.cmdline import OptionsHolder, Option;
import json;
import numpy as np;


class MS_Data_Encoder(json.JSONEncoder):
    def default(self, obj):
       #print(type(obj));
       
       if isinstance(obj, np.ndarray):    
           return obj.tolist();
           
       elif isinstance(obj, np.float32):    
           return float(obj);
           
       elif isinstance(obj, np.uint16):    
           return int(obj);

       elif isinstance(obj, np.uint8):    
           return int(obj);
           
       return json.JSONEncoder.default(self, obj)


header_html = ''.join([
'<!DOCTYPE html>    \n',
'<html lang="en">    \n',
'<head>    \n',
'    <meta charset="utf-8">    \n',
'    <meta http-equiv="X-UA-Compatible" content="IE=edge">    \n',
'    <meta name="viewport" content="width=device-width, initial-scale=1">    \n',
'    \n',
'    <title>testTree</title>    \n',
'    \n',
'    \n',
'    <link href="css/bootstrap.min.css" rel="stylesheet">    \n',
'    <link href="css/style.css" rel="stylesheet">    \n',
'    \n',
'</head>    \n',
'\n',
'<script src="js/jquery.min.js"></script>    \n',
'<script src="js/bootstrap.min.js"></script>    \n',
'<script src="js/scripts.js"></script>       \n',
'\n',

'<body>    \n',
'\n',
'<h1 id="javascript_warning">Please enable javascript! It is required for proper display of this webpage!</h3>\n',
'<script>document.getElementById("javascript_warning").style.display = "none";</script>\n', 
'<div class="container-fluid">    \n',
]);

tail_html = '\
</div>  \n\
</body> \n\
</html>\
';

#def spectra_to_json(fname, spectral_list):
#    dirname, filename=os.path.split(fname);
#    if not os.path.exists(dirname):
#            os.makedirs(dirname);
#    with open(fname,'w') as fout:
#        json.dump(spectral_list, fout, cls=MS_Data_Encoder, sort_keys=True, indent=4, separators=(',', ': '))
        



class ProcessingPipeLine(object):

    def __init__(self):
        self.title = 'None';
        self.blocks = [];
        self.globals = [];
        self.externals = [];
        self.allowed_input_data = set();
        self.modified = False;
        
    def __to_hdf5_dictionary__(self):
        return {
                'title':self.title, 
                'blocks':self.blocks,
                'globals':self.globals,
                'externals':self.externals,
                'allowed_input_data':self.allowed_input_data
                };
    
    def __from_hdf5_dictionary__(self, hdf5_dictionary):
        self.configure(hdf5_dictionary['title'], 
                       hdf5_dictionary['blocks'], 
                       hdf5_dictionary['globals'], 
                       hdf5_dictionary['externals'], 
                       hdf5_dictionary['allowed_input_data']);

    def configure(self, title, pipeline_blocks, pipeline_globals, pipeline_externals, pipeline_allowed_input_data):
        self.title = title;
        self.globals = OptionsHolder('Globals', pipeline_globals);
        self.externals = pipeline_externals;
        self.allowed_input_data = pipeline_allowed_input_data;
        self.options_holders = [];
        index = -1;
        for block in pipeline_blocks:
            index += 1;
            options_holder = OptionsHolder('', block[1]);
            options_holder.optional = block[3];
            options_holder.selected = block[4];
            options_holder.command_line = block[0];
            options_holder.title = block[2];
            options_holder.index = index;
            
            self.options_holders.append(options_holder);
            


    def add_options_to_treeview(self, options_holder, read_only, externals, pre_tab = ''):

        #if read_only:        
        #    read_only_status = 'readonly';
        #else:
        #    read_only_status = '';
            
        if options_holder.optional == False or options_holder.selected:
            s1 = 'checked';
        else:
            s1 = '';

        if options_holder.optional == False or read_only:
            s2 = 'disabled';
        else:
            s2 = '';

        index = options_holder.index;
        
        #Options expander

        result = '%s%s'%(pre_tab, pre_tab.join([
        '\n',        
        '<script> \n',
        '\n',
        'var options_block_%s_expanded = true;\n'%index,
        '\n',
        'function setBlock_%s_Expanded(newValue){\n'%index,
        '    options_block_%s_expanded = newValue;\n'%index,
        '    if (options_block_%s_expanded) {\n'%index,
        '          document.getElementById("optionsexpander_%s").innerHTML = "<span class=\'glyphicon glyphicon-triangle-bottom\' aria-hidden=\'true\'></span>"\n'%index,
        '          document.getElementById("options_of_block_%s").style.display = "inline";'%index,
        '      }\n',
        '    else {\n',
        '          document.getElementById("optionsexpander_%s").innerHTML = "<span class=\'glyphicon glyphicon-triangle-right\' aria-hidden=\'true\'></span>"\n'%index,
        '          document.getElementById("options_of_block_%s").style.display = "none";'%index,
        '      }\n',
        '};\n',
        '\n',
        'function toggleExpandedOptions_%s(){\n'%index,
        '    setBlock_%s_Expanded(!options_block_%s_expanded);\n'%(index, index),
        '}\n',
        '</script> \n',
        '\n',
        '<li class="list-group-item">\n',
        '     <h3>\n',
        '          <button type="button" class="btn btn-default" aria-label="Expand/Collapse" id="optionsexpander_%s" onclick="toggleExpandedOptions_%s()">\n'%(index, index),
        '          </button>\n',
        '          <span class="label label-default">%s</span>'%options_holder.title,
        '          <input type="checkbox" aria-label="..." %s %s>\n'%(s1, s2),
        '     </h3>',
        '\n',        
        '     <ul class="list-group" id="options_of_block_%s"> \n'%index,
        options_holder.get_html_view(read_only, externals, pre_tab = '            '),
        '     </ul>',
        '\n',        
        '     <script> \n',
        '     setBlock_%s_Expanded(true);\n'%index,
        '     </script> \n',
        '</li>\n',
        ]));
        
        return result;

    def get_view(self, full_html = False, read_only = False, externals = set(), options_level = 0):

        if self.modified:
            modified_status = 'true';
        else:
            modified_status = 'false';
        
        if read_only:        
            read_only_status = 'readonly';
        else:
            read_only_status = '';
            
            

        #Pipeline Title handling
        result = ''.join([
        '<div class="row">\n',
        '    <div class="col-md-12"> \n',
#        '        <div class="page-header">\n',
        '             <h1>Pipeline:</h1>\n',
#       '        </div>\n',
        '    </div> \n',
        '</div> \n',
        '<div class="row">\n',
        '    <div class="col-md-10"> \n',
        '             <div class="input-group">\n',
        '                 <input type="text" class="form-control" aria-describedby="title_extra_basic-addon2" id="pipeline_title" %s value="%s">\n'%(read_only_status, self.title),
        '                 <span class="input-group-addon" id="readonly_status"></span>\n',
        '                 <span class="input-group-addon" id="title_modified_status"></span>\n',
        '                 <span class="input-group-addon" id="title_extra_basic-addon2"></span>\n',
        '             </div>\n',
  
        '    </div> \n',
        '    <div class="col-md-2"> \n',
        '                 <button type="button" class="btn btn-default">Save as...</button>\n',
        '                 <button type="button" class="btn btn-default">Run</button>\n',        
        '    </div> \n',
        '</div> \n',
        '<div class="row">\n',
        '    <div class="col-md-12"> \n',
        '    <hr>\n',        
        '    <ul class="nav nav-tabs" id="ModeTabSettings">\n',
        '       <li role="presentation"><a href="#" onclick="setBasicLevel();return false;">Basic</a></li>\n',
        '       <li role="presentation" class="active"><a href="#" onclick="setAdvancedLevel();return false;">Advanced</a></li>\n',
        '    </ul>\n',

        '    <hr>\n',
        '    </div> \n',
        '</div> \n',

        #Modification status handling
        '<script> \n',
        'var modified = false; \n',
        'var global_form_read_only = %s; \n'%(str(read_only).lower()),        
        '\n',
        'function update_modified_status(newValue) {\n',
        '     modified = newValue;\n',
        '     if (modified) {\n',
        '         document.getElementById("title_modified_status").innerHTML = "Modified";\n',
        '     }\n',
        '     else {\n',
        '         document.getElementById("title_modified_status").innerHTML = "Original";\n',
        '     }\n',
        '}\n',
        '\n',        
        ' if (global_form_read_only) {\n',
        '       document.getElementById("readonly_status").innerHTML = "ReadOnly";\n',
        '    }\n',
        'else {\n',
        '       document.getElementById("readonly_status").innerHTML = "Editable";\n',
        '};\n',
        '\n',
        'update_modified_status(%s);\n'%(modified_status),

        #Current time stamp handling
        '\n',
        'function display_current_time_and_date(elementID) {\n',
        '     var today = new Date();\n',
        '     document.getElementById(elementID).innerHTML = today;\n',
        '};\n',
        '\n',
        'display_current_time_and_date("title_extra_basic-addon2")\n',
        'setInterval(function(){display_current_time_and_date("title_extra_basic-addon2")}, 1000);\n',

        #setOptionValue
        '\n',
        'function setOptionValue(value, optionid) {\n',
        '     document.getElementById(optionid).value = value;\n',
        '};\n',
        '\n',
        
        'function setOptionValueAndToggleVisibility(value, input_field, value_dict) {\n',
        '\n',
        '    element = document.getElementById(input_field);\n',
        '    element.innerHTML = value;\n',
        '    element.value = value;\n',
        '\n',
        '    for (key in value_dict) {\n',
        '        if (key == value) {\n',
        '                document.getElementById(value_dict[key]).style.display = "inline";\n',
        '            }\n',
        '        else {\n',
        '                document.getElementById(value_dict[key]).style.display = "none";\n',
        '            }\n',
        '    }\n',
        '}\n',


        #Define the list of inputs to be run through setOptionValueAndToggleVisibility at the end of loading the page
        'var inputs_list_to_be_called = [];\n',

        #Define which inputs are displayed in advanced mode only
        'var inputs_list_to_be_of_advanced_level = [];\n',
        '\n',
        'function setBasicLevel() {\n',
        '\n',
 #       'console.log("Basic");\n',
        '    element = document.getElementById("ModeTabSettings");\n',
        '    \n',
        '    element.innerHTML = \'       <li role="presentation" class="active"><a href="#" onclick="setBasicLevel(); return false;">Basic</a></li>\'+\n',
        '    \'<li role="presentation"><a href="#" onclick="setAdvancedLevel(); return false;">Advanced</a></li>\';\n',
        ' \n',
        
        '    item_count = inputs_list_to_be_of_advanced_level.length;    \n',        
        '    for (i = 0; i < item_count; i++) {\n',
        '        item = inputs_list_to_be_of_advanced_level[i];\n',
        '        document.getElementById(item).style.display = "none";\n',
        '    }\n',
        
        '\n',
        '\n',
        '\n',
        '}\n',
        '\n',
        'function setAdvancedLevel() {\n',
        '\n',
#        'console.log("Advanced");\n',
        '    element = document.getElementById("ModeTabSettings");\n',
        '    \n',
        '    element.innerHTML = \'       <li role="presentation"><a href="#" onclick="setBasicLevel(); return false;">Basic</a></li>\'+\n',
        '    \'<li role="presentation" class="active"><a href="#" onclick="setAdvancedLevel(); return false;">Advanced</a></li>\';\n',
        '\n',
        '    item_count = inputs_list_to_be_of_advanced_level.length;    \n',        
        '    for (i = 0; i < item_count; i++) {\n',
        '        item = inputs_list_to_be_of_advanced_level[i];\n',
        '        document.getElementById(item).style.display = "block";\n',
        '    }\n',
        
        '}\n',
        '\n',



        #Head scripting end        
        '\n',
        '</script>\n',
        '\n',


        #List of pipeline blocks handling
        '<div class="row"><div class="col-md-12">\n',

#        '   <div style="position:relative;width:100%;height:100%;">\n',
#        '    <div class="scroll-area">\n',
        
        
        '     <ul class="list-group">\n']);
                    
        for options_holder in self.options_holders:
            result += self.add_options_to_treeview(options_holder, read_only, externals, pre_tab = '         ');
            
        result += ''.join([
        '     </ul>\n',
        
        
#        '   </div>\n',
#        '  </div>\n',        
        
#        '  <div class="bottom" >\n',
#        '<div class="panel panel-primary" style = "width:99%; height:99%">\n',
#        '<div class="alert alert-success" role="alert">\n',
#        'Bottom Panel  </div>\n',        
#        '</div>\n',
#        '  </div>\n',
            
        '</div>\n</div>\n']);
        
        result += ''.join([
        '<script>\n',
        'function processToggleList(inputs_list) {\n',
        '\n',
        '    item_count = inputs_list.length;    \n',        
        '    for (i = 0; i < item_count; i++) {\n',
        '        item = inputs_list[i];\n',
        '        setOptionValueAndToggleVisibility(item[1], item[0], item[2]);\n',
        '    }\n',
        '}\n',
        '\n',
        'processToggleList(inputs_list_to_be_called);\n',
        '</script>\n',
        '\n',
        ]);
        
        if options_level == 0:
            result += ''.join([
            '<script>\n',
            'setBasicLevel();\n',
            '</script>\n',    
            ]);

        else:
            result += ''.join([
            '<script>\n',
            'setAdvancedLevel();\n',
            '</script>\n',    
            ]);

            

        #Ending of HTML
        if full_html:
            result = '%s\n%s\n%s'%(header_html, result, tail_html);
            
        return result


    def restore_from_json(self):
        pass


    
    def store_to_json(self):
        source_json = {
                'title':self.title, 
                'options_holders':self.options_holders,
                'globals':self.globals,
                'externals':self.externals,
                'allowed_input_data':self.allowed_input_data
                };
                
        return json.dumps(source_json, cls=MS_Data_Encoder, indent=4, separators=(',', ': '));
    
    
    def store_to_file(self, fname):
        with open(fname, 'w') as fout:
            fout.write(self.store_to_json());

    def restore_from_file(self, fname):
        with open(fname, 'r') as finp:
            self.restore_from_json(finp.read());
    
    def store_parameters_to_json(self):
        pass
    
    def restore_parameters_from_json(self):
        pass
    
    
    def get_command_lines(self):
        result = [];
        for options_holder in self.options_holders:
            if options_holder.optional == False or options_holder.selected:
                result.append(options_holder.generate_command_line(self.globals))
        return result;
    
    def execute_pipeline(self, working_folder = os.getcwd()):
        curpath = os.getcwd();
        
        os.chdir(working_folder);
        commands = self.get_command_lines();
        
        for command in commands:
            subprocess.run([command]);
        
        os.chdir(curpath);
            
        
                                           
if __name__ == '__main__':
    print('Pipeline module');
    from proc.procconfig import IntraPAlign_options, NoiseFilter_options, ProfAlign_options, PeakDetection_options, TICvis_options;

    GCMS_pipeline_default_blocks = [
        ['python ./proc/preproc/intrapalign.py', IntraPAlign_options+[Option('--verbose', help = 'Use verbose level', values=None, type=bool, targets=['/params'], level = 0)], 'Internal peak alignment', False, True], #$dbfilepath --h5writepath 'sp2D'
        ['python ./proc/preproc/noisefilter.py', NoiseFilter_options, 'Noise filtering', False, True],#"$dbfilepath" --h5readpath 'sp2D' --h5writepath 'spproc2D'
        ['python ./proc/preproc/interpalign.py', ProfAlign_options, 'Intersample peak alignment', False, True],#"$dbfilepath" --minsegwidth 30 --maxpeakshift 15 --h5readpath 'spproc2D' --h5writepath 'spal2D'
        ['python ./proc/preproc/peakdetect.py', PeakDetection_options, 'Peak extraction', False, True],#"$dbfilepath" --h5readpath spal2D
        ['python ./proc/vis/vistic.py', TICvis_options, 'Results visualization', True, True]  # "$dbfilepath" --h5readpath '/spal2D' --method 'bokeh' 
    ]    
    
    GCMS_pipeline_default_globals = [Option('dbfilename', help = 'Output HDF5 file name.', values=['', None], type=str, level = 0)]
    GCMS_pipeline_default_externals = set(['dbfilename']);
    GCMS_pipeline_default_allowed_input_data = set(['GCMS_Raw']);
    
    GCMS_pipeline_default = ProcessingPipeLine();
    
    GCMS_pipeline_default.configure('Default GC-MS raw data processing',
                                           GCMS_pipeline_default_blocks,
                                           GCMS_pipeline_default_globals,
                                           GCMS_pipeline_default_externals,
                                           GCMS_pipeline_default_allowed_input_data);
    
    cml = GCMS_pipeline_default.get_command_lines();
    for cmdl in cml:
        print(cmdl);
    
    html_block = GCMS_pipeline_default.get_view(full_html = True, read_only = False, externals = GCMS_pipeline_default_externals, options_level = 1);
    
    with open('e:/WebServer/Apache24/htdocs/testhtmltree/index.html', 'w') as fout:
        fout.write(html_block);
