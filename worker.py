# Worker to recieve units to process
# created by Psymons and Entarius Fusion
# (c) 2022

import math
import json
import datetime
import requests
import backoff
from os import system, name
from time import sleep

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

def backoff_hdlr(details):
  print ("Backing off {wait:0.1f} seconds after {tries} tries "
        "calling function {target} with args {args} and kwargs "
        "{kwargs}".format(**details))

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
  x = requests.post(post_url, data, timeout=3)
  
def clear():
  if name == 'nt':
    _ = system('cls')

  else:
    _ = system('clear')

def output_things(iteration, lowest, identifier):
  clear()
  print("Truckers@Home")
  print("Working on unit : {:,.0f}".format(identifier))
  print("[{}] Checkpoint {:,.0f} / 10".format(datetime.datetime.now().strftime("%H:%M:%S"), iteration / 1_000_000))
  print("Lowest Distance found so far ({:,.3f})".format(lowest))


lookup = '{"0":{"name":"van Maanen\'s Star","x":-6.3125,"y":-11.6875,"z":-4.125},"1":{"name":"Wolf 124","x":-7.25,"y":-27.1562,"z":-19.0938},"2":{"name":"Midgcut","x":-14.625,"y":10.3438,"z":13.1562},"3":{"name":"PSPF-LF 2","x":-4.40625,"y":-17.1562,"z":-15.3438},"4":{"name":"Wolf 629","x":-4.0625,"y":7.6875,"z":20.0938},"5":{"name":"LHS 3531","x":1.4375,"y":-11.1875,"z":16.7812},"6":{"name":"Stein 2051","x":-9.46875,"y":2.4375,"z":-15.375},"7":{"name":"Wolf 25","x":-11.0625,"y":-20.4688,"z":-7.125},"8":{"name":"Wolf 1481","x":5.1875,"y":13.375,"z":13.5625},"9":{"name":"Wolf 562","x":1.46875,"y":12.8438,"z":15.5625},"10":{"name":"LP 532-81","x":-1.5625,"y":-27.375,"z":-32.3125},"11":{"name":"LP 525-39","x":-19.7188,"y":-31.125,"z":-9.09375},"12":{"name":"LP 804-27","x":3.3125,"y":17.8438,"z":43.2812},"13":{"name":"Ross 671","x":-17.5312,"y":-13.8438,"z":0.625},"14":{"name":"LHS 340","x":20.4688,"y":8.25,"z":12.5},"15":{"name":"Haghole","x":-5.875,"y":0.90625,"z":23.8438},"16":{"name":"Trepin","x":26.375,"y":10.5625,"z":9.78125},"17":{"name":"Kokary","x":3.5,"y":-10.3125,"z":-11.4375},"18":{"name":"Akkadia","x":-1.75,"y":-33.9062,"z":-32.9688},"19":{"name":"Hill Pa Hsi","x":29.4688,"y":-1.6875,"z":25.375},"20":{"name":"Luyten 145-141","x":13.4375,"y":-0.8125,"z":6.65625},"21":{"name":"WISE 0855-0714","x":6.53125,"y":-2.15625,"z":2.03125},"22":{"name":"Alpha Centauri","x":3.03125,"y":-0.09375,"z":3.15625},"23":{"name":"LHS 450","x":-12.4062,"y":7.8125,"z":-1.875},"24":{"name":"LP 245-10","x":-18.9688,"y":-13.875,"z":-24.2812},"25":{"name":"Epsilon Indi","x":3.125,"y":-8.875,"z":7.125},"26":{"name":"Barnard\'s Star","x":-3.03125,"y":1.375,"z":4.9375},"27":{"name":"Epsilon Eridani","x":1.9375,"y":-7.75,"z":-6.84375},"28":{"name":"Narenses","x":-1.15625,"y":-11.0312,"z":21.875},"29":{"name":"Wolf 359","x":3.875,"y":6.46875,"z":-1.90625},"30":{"name":"LAWD 26","x":20.9062,"y":-7.5,"z":3.75},"31":{"name":"Avik","x":13.9688,"y":-4.59375,"z":-6.0},"32":{"name":"George Pantazis","x":-12.0938,"y":-16.0,"z":-14.2188}}'
lookup = json.loads(lookup)
version = "P.0.0.6"

# ip = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 22, 29, 28, 21, 31, 30, 27, 23, 24, 32, 19, 25, 26, 20, 18]

b = {}
for x in range(33):
  for y in range(33):
    if x == y: #no need to int an int, could reverse the logic so only do if not equal to each other and no else
      continue # this skips current itteration which is what i think you wanted to do
    else:
      b["{}-{}".format(x, y)] = math.sqrt(((lookup[str(x)]["x"] - lookup[str(y)]['x']) ** 2) + ((lookup[str(x)]['y'] - lookup[str(y)]['y']) ** 2) + ((lookup[str(x)]['z'] - lookup[str(y)]['z']) ** 2))



get_url = 'http://136.244.76.145:4567/work.json'
post_url = 'http://136.244.76.145:4567/result'

while True:
  lowest_total = 999999999999999999999
  lowest_perm = []
  start_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
  start = datetime.datetime.now()
  clear()
  x = get_work_unit()

  data = x.json()
  ip = data['perm']
  identifier = data['identifier']
  iteration = data['iteration']
  
  print("Truckers@Home")
  print("Working on unit : {:,.0f}".format(iteration))
  print("[{}] Checkpoint {:,.0f} / 10".format(datetime.datetime.now().strftime("%H:%M:%S"), 0))

  y = 0
  z = 0
  for x in range(1,10_000_000):
    y += 1
    if y == 1_000_000:
      output_things(x, lowest_total, iteration)
      y = 0
    
    distance = b[f"{ip[0]}-{ip[1]}"] + b[f"{ip[1]}-{ip[2]}"] + b[f"{ip[2]}-{ip[3]}"] + b[f"{ip[3]}-{ip[4]}"] + b[f"{ip[4]}-{ip[5]}"] + b[f"{ip[5]}-{ip[6]}"] + b[f"{ip[6]}-{ip[7]}"] + b[f"{ip[7]}-{ip[8]}"] + b[f"{ip[8]}-{ip[9]}"] + b[f"{ip[9]}-{ip[10]}"] + b[f"{ip[10]}-{ip[11]}"] + b[f"{ip[11]}-{ip[12]}"] + b[f"{ip[12]}-{ip[13]}"] + b[f"{ip[13]}-{ip[14]}"] + b[f"{ip[14]}-{ip[15]}"] + b[f"{ip[15]}-{ip[16]}"] + b[f"{ip[16]}-{ip[17]}"] + b[f"{ip[17]}-{ip[18]}"] + b[f"{ip[18]}-{ip[19]}"] + b[f"{ip[19]}-{ip[20]}"] + b[f"{ip[20]}-{ip[21]}"] + b[f"{ip[21]}-{ip[22]}"] + b[f"{ip[22]}-{ip[23]}"] + b[f"{ip[23]}-{ip[24]}"] + b[f"{ip[24]}-{ip[25]}"] + b[f"{ip[25]}-{ip[26]}"] + b[f"{ip[26]}-{ip[27]}"] + b[f"{ip[27]}-{ip[28]}"] + b[f"{ip[28]}-{ip[29]}"] + b[f"{ip[29]}-{ip[30]}"] + b[f"{ip[30]}-{ip[31]}"] + b[f"{ip[31]}-{ip[32]}"]   # strings are literal now
    
    if distance < lowest_total:
      lowest_total = distance
      lowest_perm = ip
      
    ip = next_lexicographic_permutation(ip)

  finish_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
  finish = datetime.datetime.now()
  # print("[{}] Finish".format(finish_date))
  diff = finish - start

  # print("Time taken => {}".format(diff))
  # print("Lowest distance => {}".format(lowest_total))
  # print("Lowest permutation => {} ".format(str(lowest_perm).replace(" ", "")))

  final = {}
  final['distance'] = lowest_total
  final['identifier'] = identifier
  final['perm'] = lowest_perm
  final['duration'] = str(diff)
  final['finished_at'] = finish_date
  final['version'] = version
  final = json.dumps(final)
  send_work_unit(final)
  # sleep(2)
