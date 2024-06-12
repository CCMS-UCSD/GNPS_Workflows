import os
from enum import Enum

class LogType(Enum):
  SINGLE = 1
  MULTIPLE = 2

def parsefolder(path, blacklist=None, whitelist=None):
  # check that lists are either None or type lists  
  assert (blacklist is None) or (type(blacklist) is list)
  assert (whitelist is None) or (type(whitelist) is list)

  # check if dir exists
  if not os.path.exists(path):
    raise StopIteration

  # traverse dir
  for file in sorted(os.listdir(path)):
    # print("\n")
    # print("file",file)
    # print("blacklist", blacklist, all(bl not in file for bl in blacklist))
    # print("whitelist", whitelist, any(wl in file for wl in whitelist) if whitelist)
    if file[0] is not '.' and ( \
      (whitelist is None or len(whitelist) is 0 or (len(whitelist) > 0 and any(wl in file for wl in whitelist))) and \
      (blacklist is None or len(blacklist) is 0 or (len(blacklist) > 0 and all(bl not in file for bl in blacklist))) \
    ):
      yield (path+"/"+file, os.path.splitext(file)[0].split('-')[1])


def postvalidation(modulename, inpath, outpath, logtype=LogType.MULTIPLE, output_per_job=1):
  print("\n\n\n===POST VALIDATION===")

  # print("os getcwd()",os.getcwd())  
  print("output_results", os.listdir(outpath))

  exp_jobs = 1 if output_per_job < 1 else output_per_job * len(list(parsefolder(inpath, blacklist=['logfile'])))
  exp_logs = 1 if logtype == LogType.SINGLE else exp_jobs / output_per_job

  num_jobs = len(list(parsefolder(outpath, blacklist=['log'])))
  num_logs = len(list(parsefolder(outpath, whitelist=['log'])))

  if num_logs == exp_logs and num_jobs == exp_jobs:
    print("passed!")
    return True

  print("num jobs", num_jobs, exp_jobs)
  print("num logs", num_logs, exp_logs)
  print("check", num_logs == exp_logs and num_jobs == exp_jobs)

  if num_logs:
    print(modulename.upper()+": Issue with executing module")
    print("num_logs",num_logs)
    last_log = "{}/logfile-{:05d}.txt".format(outpath,num_logs-1)
    with open(last_log) as f:
      print(f.read())
  
  exit(1)