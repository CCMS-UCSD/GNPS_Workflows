import json
import os
import argparse
import glob
import sys
import shutil
import pandas as pd
import ming_proteosafe_library
import pathlib


def main():
    parser = argparse.ArgumentParser(description="Proteosafe Wrapper for Nextflow")
    parser.add_argument('workflow_params', help='workflow_params, from proteosafe')
    parser.add_argument('nextflow_script', help='nextflow_script to actually run')
    parser.add_argument('conda_activate', help='conda_activate, this is the path to the activate command in the main conda installation')
    parser.add_argument('nextflow_conda_environment', help='nextflow_conda_environment, this likely should be wherever all your dependencies and nextflow are installed, e.g. nextflow or msql2')
    parser.add_argument('--parametermapping', action='append', help='mapping of current workflow parameters to new parameters in the format: <old parameter>:<new parameter>')
    parser.add_argument('--newparameters', action='append', help='parameter key: <param name>:<parameter value>')

    parser.add_argument('--metricoutput', default=None, help='output folder for metrics')

    # Settings if we want to monitor nextflow progress in ProteoSAFe
    parser.add_argument('--updateproteosafefronteendstatus', default='NO', help='Enables outputting data to front end task directories to allow for current status, options YES and NO')

    # These settings are for the cluster run
    parser.add_argument('--runcluster', default='NO', help='Tries to run this on the cluster, values are NO and YES')
    parser.add_argument('--clusterconfig', default=None, help='Path to configuration file')
    parser.add_argument('--user', default=None, help='username running the task')
    parser.add_argument('--clusterpythonruntime', default=None, help='cluster python runtime')
    parser.add_argument('--clusterworkprefix', default=None, help='clusterworkprefix')
    parser.add_argument('--task', default=None, help='cluster python runtime')

    args = parser.parse_args()

    # Listing our system
    os.system("hostname")
    os.system("whoami")
    os.system("pwd")
    os.system("ls -l -h")

    output_stdout_file = os.path.abspath(os.path.join(args.metricoutput, "stdout.log"))
    workflow_task_directory = "."
    original_directory = os.getcwd()

    output_trace_filename = "trace.txt"

    if args.updateproteosafefronteendstatus == "YES":
        output_trace_folder = os.path.join("/data/ccms-data/tasks/", args.user, args.task, "nextflow")
        pathlib.Path(output_trace_folder).mkdir(parents=True, exist_ok=True)
        output_trace_filename = os.path.join(output_trace_folder, "trace.txt")

        output_stdout_file = os.path.join(output_trace_folder, "stdout.log")

    if args.runcluster == "YES" and args.user in ["mwang87"]:
        # Staging all files on gscratch because they might not be seen if we schedule outputs from local scratch disk
        workflow_task_directory = os.path.join("/gscratch/nextflow_staging", args.task)
        pathlib.Path(workflow_task_directory).mkdir(parents=True, exist_ok=True)

        pbs_cluster_work_dir = os.path.join(args.clusterworkprefix, args.task, "work")

        cmd = "source {} {} && cd {} && nextflow run {} -c {} \
                -work-dir {} \
                --PYTHONRUNTIME={} \
                -with-trace {} \
                -with-dag dag.html \
                -with-report report.html \
                -with-timeline timeline.html > {} 2>&1".format(args.conda_activate, args.nextflow_conda_environment,
                            workflow_task_directory, 
                            args.nextflow_script, args.clusterconfig, pbs_cluster_work_dir, args.clusterpythonruntime,
                            output_trace_filename,
                            output_stdout_file)
    else:
        cmd = "source {} {} && nextflow run {} \
                -with-trace {} \
                -with-dag dag.html \
                -with-report report.html \
                -with-timeline timeline.html > {} 2>&1".format(args.conda_activate, args.nextflow_conda_environment,
                            args.nextflow_script,
                            output_trace_filename,
                            output_stdout_file)
    for parameter in args.newparameters:
        print(parameter)
        cmd += ' --{} "{}"'.format(parameter.split(":")[0], parameter.split(":")[1].replace("\n", ""))

    params_obj = ming_proteosafe_library.parse_xml_file(open(args.workflow_params))
    for parameter in args.parametermapping:
        print(parameter)
        new_param = parameter.split(":")[1]
        old_param = parameter.split(":")[0]

        cmd += ' --{} "{}"'.format(new_param, params_obj[old_param][0].replace("\n", ""))

    print(cmd)
    return_val = os.system(cmd)
    if return_val != 0:
        print("Error in Nextflow")

    # Copying back results
    if workflow_task_directory != ".":
        try:
            cmd = "rsync -avp {}/ {}".format(workflow_task_directory, original_directory)
            print(cmd)
            os.system(cmd)
        except:
            pass

    # Copying the metric output to output folder
    if args.metricoutput is not None:
        try:
            shutil.copyfile(output_trace_filename, os.path.join(args.metricoutput, "trace.txt"))
        except:
            pass

        try:
            shutil.copyfile(output_stdout_file, os.path.join(args.metricoutput, "stdout.log"))
        except:
            pass

        try:
            os.rename("report.html", os.path.join(args.metricoutput, "report.html"))
            os.rename("timeline.html", os.path.join(args.metricoutput, "timeline.html"))
            os.rename("dag.html", os.path.join(args.metricoutput, "dag.html"))
        except:
            pass


if __name__ == "__main__":
    main()
