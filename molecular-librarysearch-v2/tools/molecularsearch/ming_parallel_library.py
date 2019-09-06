#!/usr/bin/python

from joblib import Parallel, delayed
import multiprocessing
import subprocess
import os

def run_shell_command(script_to_run):
    try:
        os.system(script_to_run)
    except KeyboardInterrupt:
        raise
    except:
        return "FAILURE"
    return "DONE"

def run_shell_command_timeout(parameter_dict):
    p = None
    try:
        print(parameter_dict["command"])
        p = subprocess.Popen(parameter_dict["command"])
        p.wait(parameter_dict["timeout"])
    except subprocess.TimeoutExpired:
        p.kill()
        return "FAILURE"
    except KeyboardInterrupt:
        raise
    except:
        return "FAILURE"
    return "DONE"

#Wraps running in parallel a set of shell scripts
def run_parallel_shellcommands(input_shell_commands, parallelism_level, timeout=None):
    if timeout != None:
        parameters_list = []
        for command in input_shell_commands:
            parameter_object = {}
            parameter_object["command"] = command
            parameter_object["timeout"] = timeout
            parameters_list.append(parameter_object)
        return run_parallel_job(run_shell_command_timeout, parameters_list, parallelism_level)
    else:
        return run_parallel_job(run_shell_command, input_shell_commands, parallelism_level)

#Wraps the parallel job running, simplifying code
def run_parallel_job(input_function, input_parameters_list, parallelism_level):
    if parallelism_level == 1:
        output_results_list = []
        for input_param in input_parameters_list:
            result_object = input_function(input_param)
            output_results_list.append(result_object)
        return output_results_list
    else:
        results = Parallel(n_jobs = parallelism_level)(delayed(input_function)(input_object) for input_object in input_parameters_list)
        return results

#Wraps calling a parallel map and a subsequent reduce function
def map_reduce_parallel_job(map_function, reduce_function, input_parameters_list, parallelism_level):
    map_results = run_parallel_job(map_function, input_parameters_list, parallelism_level)
    reduce_results = reduce_function(map_results)
    return reduce_results
