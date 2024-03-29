# Working GPU with TAH code. Edit steps variable if the script fails
# 1 Billion iterations uses about 12GB of memory to construct the array
# if you have less than 12GB then lower it to 500_000_000 or so
# 100_000_000 ses about 2GB

import backoff
import cupy as cp
import datetime
import json
import math
from numba import cuda
from numba.core.errors import NumbaPerformanceWarning
import numpy as np
from os import sys, system, name
import requests
import time
import warnings
import zlib

warnings.simplefilter('ignore', category=NumbaPerformanceWarning)

CMDR = "AnonCmdr" # Set this if you want credit to your Commander name
TEAM = "None" # If you have a team uuid, replace it inside the double quotes

# STEP_COUNT can be adjusted from 100 to 5000, 100 for short work units and 5000 for long ones
# GPU step count should be 5000 to avoid excessive server calls
STEP_COUNT = 50_000 # adjust this to make your work units longer or shorter 

# GPU steps are the amount of numbers the gpu will fill a matrix with and process to get a result.
# if your work unit has a step size of 1000, the total numbers that need to be processed is 1 billion
# so the client will break the work unit up into 10 100_000_000 steps to process the entire result
# a gpu_steps size of 100 million usually uses aroung 3GB of GPU memory
# Adjusting this higher can SLIGHTLY increase GPU performance and lower overall work unit time
# unless you have a lot of GPU memory its advised not to go over 250 Million gpu_steps
gpu_steps = 100_000_000

# This dedicates GPU cores to blocks of work (the GPU sorts of the work allocation behind the scenes)
# 32 seems to give the best result for processing this type of work
threadsperblock = 32
blockspergrid = (gpu_steps + threadsperblock - 1) // threadsperblock

# Client Version
version = "GPU.0.2"

COMPRESSED_OCTET_STREAM = {'content-type': 'application/octet-stream', 'content-encoding': 'zlib'}

@cuda.jit(device=True)
def gpu_factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

@cuda.jit(device=True)
def gpu_int_to_perm(n, elems, output):
    length = len(elems)
    factoradic = cuda.local.array(33, dtype=cp.uint64)
    elems_copy = cuda.local.array(33, dtype=cp.int64)

    # Compute the factoradic representation of n
    for i in range(length):
        factoradic[i] = n % (i + 1)
        n //= i + 1

    # Copy elems to elems_copy
    for i in range(length):
        elems_copy[i] = elems[i]

    # Generate the permutation based on the factoradic representation
    for i in range(length - 1, -1, -1):
        output[length - 1 - i] = elems_copy[factoradic[i]]

        # Shift elements from index factoradic[i] to the end to the left
        for j in range(factoradic[i], i):
            elems_copy[j] = elems_copy[j + 1]



@cuda.jit
def int_to_perm_kernel(integer_matrix, elems, b, min_result, min_n_value):
    i = cuda.grid(1)
    if i < len(integer_matrix):
        n = integer_matrix[i]
        elems_copy = cuda.local.array(33, dtype=cp.int64)
        for j in range(len(elems)):
            elems_copy[j] = elems[j]

        ip = cuda.local.array(33, dtype=cp.int64)
        gpu_int_to_perm(n, elems_copy, ip)
        # Calculate the sum of consecutive pairs using the lookup table (borrowed from CPU code)
        distance = b[ip[0]][ip[1]] + b[ip[1]][ip[2]] + b[ip[2]][ip[3]] +\
            b[ip[3]][ip[4]] + b[ip[4]][ip[5]] + b[ip[5]][ip[6]] +\
            b[ip[6]][ip[7]] + b[ip[7]][ip[8]] + b[ip[8]][ip[9]] +\
            b[ip[9]][ip[10]] + b[ip[10]][ip[11]] + b[ip[11]][ip[12]] +\
            b[ip[12]][ip[13]] + b[ip[13]][ip[14]] + b[ip[14]][ip[15]] +\
            b[ip[15]][ip[16]] + b[ip[16]][ip[17]] + b[ip[17]][ip[18]] +\
            b[ip[18]][ip[19]] + b[ip[19]][ip[20]] + b[ip[20]][ip[21]] +\
            b[ip[21]][ip[22]] + b[ip[22]][ip[23]] + b[ip[23]][ip[24]] +\
            b[ip[24]][ip[25]] + b[ip[25]][ip[26]] + b[ip[26]][ip[27]] +\
            b[ip[27]][ip[28]] + b[ip[28]][ip[29]] + b[ip[29]][ip[30]] +\
            b[ip[30]][ip[31]] + b[ip[31]][ip[32]]

        cuda.atomic.min(min_result, 0, distance)
        if min_result[0] == distance:
            min_n_value[0] = n
            
# Gives some details if we are forced to back off during a connect or send event
def backoff_hdlr(details):
  print ("Backing off {wait:0.1f} seconds after {tries} tries "
        "calling function {target} with args {args} and kwargs "
        "{kwargs}".format(**details))
            
# Added the backoff decorators to retry without hammering the server if it unreachable or offline for any reason

@backoff.on_exception(backoff.expo,
                      (requests.exceptions.Timeout,
                       requests.exceptions.ConnectionError,
                       requests.exceptions.RequestException,
                       requests.exceptions.RetryError),on_backoff=backoff_hdlr)
def get_work_unit():
  x = requests.get(get_url, timeout=3)
  return x

@backoff.on_exception(backoff.expo,
                      (requests.exceptions.Timeout,
                       requests.exceptions.ConnectionError,
                       requests.exceptions.RequestException,
                       requests.exceptions.RetryError),on_backoff=backoff_hdlr)
def send_work_unit(data):
  compressed_data = zlib.compress(data.encode('utf-8'))
  x = requests.post(post_url, compressed_data, timeout=3, headers=COMPRESSED_OCTET_STREAM)
  
# Quick and dirty screen clearer that works with windows or linux
def clear():
  if name == 'nt':
    _ = system('cls')

  else:
    _ = system('clear')

# used for updating against checkpoints. not currently in use
def output_things(iteration, lowest, identifier):
  clear()
  print("Truckers@Home GPU client")
  print("Working on unit : {:,.0f}".format(identifier))
  print("[{}] Checkpoint {:,.0f} / 10".format(datetime.datetime.now().strftime("%H:%M:%S"), iteration / 1_000_000))
  print("Lowest Distance found so far ({:,.3f})".format(lowest))
  
get_url = 'http://hot.forthemug.com:4567/work.json/{}/G'.format(STEP_COUNT)
post_url = 'http://hot.forthemug.com:4567/result'
  
lookup = '{"0":{"name":"van Maanen\'s Star","x":-6.3125,"y":-11.6875,"z":-4.125},\
  "1":{"name":"Wolf 124","x":-7.25,"y":-27.1562,"z":-19.0938},\
  "2":{"name":"Midgcut","x":-14.625,"y":10.3438,"z":13.1562},\
  "3":{"name":"PSPF-LF 2","x":-4.40625,"y":-17.1562,"z":-15.3438},\
  "4":{"name":"Wolf 629","x":-4.0625,"y":7.6875,"z":20.0938},\
  "5":{"name":"LHS 3531","x":1.4375,"y":-11.1875,"z":16.7812},\
  "6":{"name":"Stein 2051","x":-9.46875,"y":2.4375,"z":-15.375},\
  "7":{"name":"Wolf 25","x":-11.0625,"y":-20.4688,"z":-7.125},\
  "8":{"name":"Wolf 1481","x":5.1875,"y":13.375,"z":13.5625},\
  "9":{"name":"Wolf 562","x":1.46875,"y":12.8438,"z":15.5625},\
  "10":{"name":"LP 532-81","x":-1.5625,"y":-27.375,"z":-32.3125},\
  "11":{"name":"LP 525-39","x":-19.7188,"y":-31.125,"z":-9.09375},\
  "12":{"name":"LP 804-27","x":3.3125,"y":17.8438,"z":43.2812},\
  "13":{"name":"Ross 671","x":-17.5312,"y":-13.8438,"z":0.625},\
  "14":{"name":"LHS 340","x":20.4688,"y":8.25,"z":12.5},\
  "15":{"name":"Haghole","x":-5.875,"y":0.90625,"z":23.8438},\
  "16":{"name":"Trepin","x":26.375,"y":10.5625,"z":9.78125},\
  "17":{"name":"Kokary","x":3.5,"y":-10.3125,"z":-11.4375},\
  "18":{"name":"Akkadia","x":-1.75,"y":-33.9062,"z":-32.9688},\
  "19":{"name":"Hill Pa Hsi","x":29.4688,"y":-1.6875,"z":25.375},\
  "20":{"name":"Luyten 145-141","x":13.4375,"y":-0.8125,"z":6.65625},\
  "21":{"name":"WISE 0855-0714","x":6.53125,"y":-2.15625,"z":2.03125},\
  "22":{"name":"Alpha Centauri","x":3.03125,"y":-0.09375,"z":3.15625},\
  "23":{"name":"LHS 450","x":-12.4062,"y":7.8125,"z":-1.875},\
  "24":{"name":"LP 245-10","x":-18.9688,"y":-13.875,"z":-24.2812},\
  "25":{"name":"Epsilon Indi","x":3.125,"y":-8.875,"z":7.125},\
  "26":{"name":"Barnard\'s Star","x":-3.03125,"y":1.375,"z":4.9375},\
  "27":{"name":"Epsilon Eridani","x":1.9375,"y":-7.75,"z":-6.84375},\
  "28":{"name":"Narenses","x":-1.15625,"y":-11.0312,"z":21.875},\
  "29":{"name":"Wolf 359","x":3.875,"y":6.46875,"z":-1.90625},\
  "30":{"name":"LAWD 26","x":20.9062,"y":-7.5,"z":3.75},\
  "31":{"name":"Avik","x":13.9688,"y":-4.59375,"z":-6.0},\
  "32":{"name":"George Pantazis","x":-12.0938,"y":-16.0,"z":-14.2188}}'
lookup = json.loads(lookup)

# First permutation of our array
elems = cp.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32], dtype=cp.int64)

# float32 version of the lookup array calulated in the normal way insted of previous hard coded table
b = cp.zeros((33,33), dtype=cp.float32)
for x in range(33):
  for y in range(33):
    if x == y: 
      b[x][y] = 0.0
    else:
      b[x][y] = math.sqrt(((lookup[str(x)]["x"] - lookup[str(y)]['x']) ** 2) + ((lookup[str(x)]['y'] - lookup[str(y)]['y']) ** 2) + ((lookup[str(x)]['z'] - lookup[str(y)]['z']) ** 2))


clear()
print("Truckers@Home GPU client")
print("Getting work block size of {:,} Million Iterations each".format(STEP_COUNT))
print("Beginning Work on First unit...")
print("")


while True:
    # gets the work unit from the server
    x = get_work_unit()

    data = x.json()
    identifier = data['identifier']
    iteration = data['iteration']
    start_number = iteration
    work_unit_step_count = int(data['step'])
    steps = work_unit_step_count * 1_000_000

    # GPU processing is borken up into runs gpu_steps long so we need to work how many runs we need to do to to get
    # all of our runs to cover all steps
    gpu_processing_runs = math.ceil(steps / gpu_steps)

    # declare the variables passed in to hold our minimum values for sending off when this becomes a full worker client
    min_result = cp.array([cp.finfo(cp.float32).max], dtype=cp.float32)
    min_n_value = cp.array([0], dtype=cp.uint64)

    start_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    start = datetime.datetime.now()

    for i in range(gpu_processing_runs):
        # stop number is how many iterations you want from the start
        stop_number = (start_number + gpu_steps)

        # creates a 1d array of consecutive numbers from start to stop number
        integer_matrix = cp.arange(start_number,stop_number,1, dtype=cp.uint64)
                
        # Main event is wrapped in timing vars
        int_to_perm_kernel[blockspergrid, threadsperblock](integer_matrix, elems, b, min_result, min_n_value)
        
        # Create new start number for the next loop
        start_number = stop_number
        
    finish = datetime.datetime.now()
    finish_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    diff = finish - start
    final = {}
    final['cmdr'] = CMDR
    final['team'] = TEAM
    final['identifier'] = identifier
    final['distance'] = str(min_result[0].tolist())
    final['duration'] = str(diff)
    final['finished_at'] = finish_date
    final['version'] = version
    final['truckers_at_home'] = 1
    final['lowest_perm_int'] = int(min_n_value[0].tolist())
    final['step_count'] = work_unit_step_count
    final = json.dumps(final)
    sys.stdout.write("\r[{}] ITR: {:,.0f} FINISH: {} LOWEST: {}".format(finish_date, iteration, diff, min_result[0]))
    sys.stdout.flush()

    # Send the final list to the server
    send_work_unit(final)