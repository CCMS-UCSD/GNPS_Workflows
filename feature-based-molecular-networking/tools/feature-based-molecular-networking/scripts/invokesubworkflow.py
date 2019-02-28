#!/usr/bin/python

import sys
import getopt
import os
import json
import argparse
#from ccmsproteosafepythonapi import proteosafe
import ming_proteosafe_library

def main():
    parser = argparse.ArgumentParser(description='Invoking new workflow with parameters of given workflow')
    parser.add_argument('workflowparamters', help='workflowparamters')
    parser.add_argument('credentials', help='credentials.json')
    parser.add_argument('outputhtml', default='output.html', help='output html with a url')
    parser.add_argument('--serverurl', default='proteomics2.ucsd.edu', help='Server URL, default is proteomics2.ucsd.edu, other options are massive.ucsd.edu and gnps.ucsd.edu')
    parser.add_argument('--parametermapping', action='append', help='mapping of current workflow parameters to new parameters in the format: <old parameter>:<new parameter>')
    parser.add_argument('--newparameters', action='append', help='parameter key: <param name>:<parameter value>')
    parser.add_argument('--runparameter', default='NONE', help='Workflow xml parameter to check if this parameter is equal to "1" to actually invoke the workflow')
    args = parser.parse_args()

    credentials = json.loads(open(args.credentials).read())

    workflow_parameters_map = ming_proteosafe_library.parse_xml_file(args.workflowparamters)

    if args.runparameter != "NONE":
        if workflow_parameters_map[args.runparameter][0] == "0":
            output_html_file = open(args.outputhtml, "w")
            output_html_file.write("User chose not to run tool\n")
            output_html_file.close()
            exit(0)

    new_parameters = {}

    new_parameters["desc"] = "Analysis subroutine from ProteoSAFe job %s" % (workflow_parameters_map["task"][0])

    if args.newparameters != None:
        for parameter_string in args.newparameters:
            parameter_key = parameter_string.split(":")[0]
            parameter_value = parameter_string.split(":")[1]

            new_parameters[parameter_key] = parameter_value

    if args.parametermapping != None:
        for parameter_string in args.parametermapping:
            parameter_old_key = parameter_string.split(":")[0]
            parameter_new_key = parameter_string.split(":")[1]

            new_parameters[parameter_new_key] = workflow_parameters_map[parameter_old_key][0]

    task_id = ming_proteosafe_library.invoke_workflow(args.serverurl, new_parameters, credentials["username"], credentials["password"])
    if task_id == None:
        exit(1)
    ming_proteosafe_library.wait_for_workflow_finish(args.serverurl, task_id)

    """Writing HTML output"""
    output_html_file = open(args.outputhtml, "w")
    output_html_file.write("<script>\n")
    output_html_file.write('window.open("https://%s/ProteoSAFe/status.jsp?task=%s", "_blank")\n' % (args.serverurl, task_id))
    output_html_file.write("</script>\n")
    output_html_file.close()


if __name__ == "__main__":
    main()
