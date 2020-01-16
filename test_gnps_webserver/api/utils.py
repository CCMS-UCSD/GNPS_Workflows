#!/usr/bin/python

import sys
import getopt
import os
import requests
import json
import time

def load_time_of_request(url):
    current_milli_time = int(round(time.time() * 1000))
    requests.get(url)
    done_milli_time = int(round(time.time() * 1000))

    delta = done_milli_time - current_milli_time

    return delta

def test_load_time(url, threshold):
    load_time = load_time_of_request(url)

    if load_time > threshold:
        print(url, " took too long to load", load_time, "milliseconds")
        
        raise Exception