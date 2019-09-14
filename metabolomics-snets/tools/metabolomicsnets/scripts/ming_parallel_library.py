#!/usr/bin/python

from joblib import Parallel, delayed  
import multiprocessing
import os

def run_shell_command(script_to_run):
	os.system(script_to_run)
	return "DONE"

#Wraps running in parallel a set of shell scripts
def run_parallel_shellcommands(input_shell_commands, parallelism_level):
	return run_parallel_job(run_shell_command, input_shell_commands, parallelism_level)

#Wraps the parallel job running, simplifying code
def run_parallel_job(input_function, input_parameters_list, parallelism_level):
	results = Parallel(n_jobs = parallelism_level)(delayed(input_function)(input_object) for input_object in input_parameters_list)
	return results

#Wraps calling a parallel map and a subsequent reduce function
def map_reduce_parallel_job(map_function, reduce_function, input_parameters_list, parallelism_level):
	map_results = run_parallel_job(map_function, input_parameters_list, parallelism_level)
	reduce_results = reduce_function(map_results)
	return reduce_results
