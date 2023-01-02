# Worker to recieve units to process
# created by Psymons and Entarius Fusion
# (c) 2022

import backoff
import datetime
import json
import math
from os import system, name
import requests
import sys
from time import sleep
import zlib

COMPRESSED_OCTET_STREAM = {'content-type': 'application/octet-stream', 'content-encoding': 'zlib'}

# The original lookup algorithm
def next_lexicographic_permutation(x):
  
  i = len(x) - 2

  while i >= 0:
    if x[i] < x[i+1]:
      break
    else:
      i -= 1  
    if i < 0:
      return False
  
  j = len(x) - 1

  while j > i:
    if x[j] > x[i]:
      break
    else:
      j-= 1
  
  x[i], x[j] = x[j], x[i]
  reverse(x, i + 1)
  return x

def reverse(arr, i):
  if i > len(arr) - 1:
    return

  j = len(arr) - 1

  while i < j:
    arr[i], arr[j] = arr[j], arr[i]
    i += 1
    j -= 1
    
# New algorithm for calculating the Permutation based on a given integer
def int_to_perm(n,elems): # with n from 0
    output = []
    while len(elems) > 0:
        if(len(elems) == 1):
           output.append(elems[0])
           elems.remove(elems[0])
           continue
        sizeGroup = math.factorial(len(elems)-1)
        q,r = divmod(n,sizeGroup)
        v = elems[q]
        elems.remove(v)
        output.append(v)
        n = r
    return output
  
def perm_to_int(numbers): # takes the permutation list and converts it to an integer thanks ChatGPT :)
    base = len(numbers)
    lehmer = 0
    for i, num in enumerate(numbers):
        smaller = sum(1 for j in numbers[i + 1:] if j < num)
        lehmer += smaller * math.factorial(base - i - 1)
    return lehmer

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
  print("Truckers@Home")
  print("Working on unit : {:,.0f}".format(identifier))
  print("[{}] Checkpoint {:,.0f} / 10".format(datetime.datetime.now().strftime("%H:%M:%S"), iteration / 1_000_000))
  print("Lowest Distance found so far ({:,.3f})".format(lowest))

# The list of systems we are testing the shortest distances for
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
version = "P.0.2.0"

CMDR = "EntariusFusion"
STEP_COUNT = 500 # adjust this to make your work units longer or shorter
# esp32's will request 1 to 5 depending on setup
# normal client will request 100 or more
# maximum currently is 5000
# 5000 should take a modern CPU around about 30 mins

# sorted first permutation for the int_to_perm lookup
# we are no longer importing a seed as the int_to_perm function
# now generates the seed for us from the iteration number
first_perm = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32]

# Psymons has implemented a 2d array, this is by far the fastest lookup option we have made so far
b = [[0 for i in range(33)] for j in range(33)]
for x in range(33):
  for y in range(33):
    if x == y: 
      continue 
    else:
      b[x][y] = math.sqrt(((lookup[str(x)]["x"] - lookup[str(y)]['x']) ** 2) + ((lookup[str(x)]['y'] - lookup[str(y)]['y']) ** 2) + ((lookup[str(x)]['z'] - lookup[str(y)]['z']) ** 2))


# Changed the URL to a small work server from the old hosted one
get_url = 'http://hot.forthemug.com:4567/work.json/{}'.format(STEP_COUNT)
post_url = 'http://hot.forthemug.com:4567/result'
clear()
print("Truckers@Home")
print("Getting work block size of {:,} Million Iterations each".format(STEP_COUNT))
print("Beginning Work on First unit...")
print("")

while True:
  # starts at a high amount to force the first iteration to populate the variable
  lowest_total = 9999
  lowest_perm = []
  lowest_perm_int = 0
  start_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
  start = datetime.datetime.now()
  # gets the work unit from the server
  x = get_work_unit()

  data = x.json()
  identifier = data['identifier']
  iteration = data['iteration']
  steps = int(data['step'])
  steps = steps * 1_000_000
  
  # sys.stdout.write("\r" + f"[{start_date}] ITR: {iteration:,} STARTED")
  # sys.stdout.flush()
  
  # the function that generated the initial seed that the main work loop uses
  ip = int_to_perm(int(iteration),first_perm[:])
  
  # The main work loop 
  # we are now doing 100M iterations (up from 10M as the run time was too fast)
  for x in range(1,steps):   
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
    
    if distance < lowest_total:
      lowest_total = distance
      lowest_perm = ip
      
      
    ip = next_lexicographic_permutation(ip)

  finish = datetime.datetime.now()
  finish_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
  
  diff = finish - start
  # used for debugging
  # print("Time taken => {}".format(diff))
  # print("Lowest distance => {}".format(lowest_total))
  # print("Lowest permutation => {} ".format(str(lowest_perm).replace(" ", "")))
  
  # The final list is generated before being sent to the server for processing
  final = {}
  final['identifier'] = identifier
  final['distance'] = lowest_total
  final['duration'] = str(diff)
  final['finished_at'] = finish_date
  final['version'] = version
  final['truckers_at_home'] = 1
  # Generates the lehmer integer based on the lowest found permutation
  # in this work block
  final['lowest_perm_int'] = perm_to_int(lowest_perm)
  final = json.dumps(final)
  sys.stdout.write("\r[{}] ITR: {:,.0f} FINISH: {} LOWEST: {}".format(finish_date, iteration, diff, lowest_total))
  sys.stdout.flush()
  # Send the final list to the server
  send_work_unit(final)