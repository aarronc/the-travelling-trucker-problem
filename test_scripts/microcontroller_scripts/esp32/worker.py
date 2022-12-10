import math
import json
import time
import gc
import network
import urequests as requests

gc.enable()

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
    
def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('<your SSID>', '<Your Password>')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())   

print("Pre dict creation memory amount : {} bytes".format(gc.mem_free()))

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

get_url = 'http://136.244.76.145:4567/tiny.json'
post_url = 'http://136.244.76.145:4567/tiny'

do_connect() # Connect to network

gc.collect()
b = {}
for x in range(33):
  gc.collect()
  for y in range(33):
    if x == y: 
      continue 
    else:
      b["{}-{}".format(x, y)] = math.sqrt(((lookup[str(x)]["x"] - lookup[str(y)]['x']) ** 2) + ((lookup[str(x)]['y'] - lookup[str(y)]['y']) ** 2) + ((lookup[str(x)]['z'] - lookup[str(y)]['z']) ** 2))

while True:
    data = json.loads(requests.get(get_url).text)
    STEPS = 100_000
    lowest_distance = 9999
    # ip = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32]
    ip = data['perm']
    orig_uuid = data['orig_identifier']
    tiny_uuid = data['tiny_identifier']
    iteration = data['iteration']
    work_unit = data['work_unit_number']
    start = time.time()
    y = 0
    print("Tiny Unit : {}".format(tiny_uuid))
    for x in range(STEPS):
        distance = b[f"{ip[0]}-{ip[1]}"] + b[f"{ip[1]}-{ip[2]}"] + b[f"{ip[2]}-{ip[3]}"] +\
        b[f"{ip[3]}-{ip[4]}"] + b[f"{ip[4]}-{ip[5]}"] + b[f"{ip[5]}-{ip[6]}"] +\
        b[f"{ip[6]}-{ip[7]}"] + b[f"{ip[7]}-{ip[8]}"] + b[f"{ip[8]}-{ip[9]}"] +\
        b[f"{ip[9]}-{ip[10]}"] + b[f"{ip[10]}-{ip[11]}"] + b[f"{ip[11]}-{ip[12]}"] +\
        b[f"{ip[12]}-{ip[13]}"] + b[f"{ip[13]}-{ip[14]}"] + b[f"{ip[14]}-{ip[15]}"] +\
        b[f"{ip[15]}-{ip[16]}"] + b[f"{ip[16]}-{ip[17]}"] + b[f"{ip[17]}-{ip[18]}"] +\
        b[f"{ip[18]}-{ip[19]}"] + b[f"{ip[19]}-{ip[20]}"] + b[f"{ip[20]}-{ip[21]}"] +\
        b[f"{ip[21]}-{ip[22]}"] + b[f"{ip[22]}-{ip[23]}"] + b[f"{ip[23]}-{ip[24]}"] +\
        b[f"{ip[24]}-{ip[25]}"] + b[f"{ip[25]}-{ip[26]}"] + b[f"{ip[26]}-{ip[27]}"] +\
        b[f"{ip[27]}-{ip[28]}"] + b[f"{ip[28]}-{ip[29]}"] + b[f"{ip[29]}-{ip[30]}"] +\
        b[f"{ip[30]}-{ip[31]}"] + b[f"{ip[31]}-{ip[32]}"]
    
        if distance < lowest_distance:
            lowest_distance = distance
            print("[{:,}] New lowest distance found... it's {:,.2f} ly".format(x, lowest_distance))
    
    
        if y == 500:
            print ("Checkpoint {:,} / {:,}".format(x, STEPS))
            # print("Memory Check : {} bytes".format(gc.mem_free()))
            # gc.collect()
            y = 0
        
        y += 1           
        ip = next_lexicographic_permutation(ip)
    
    # print("Post run memory amount : {} bytes".format(gc.mem_free()))
    finish = time.time()
    diff = finish - start
    print("Time Taken for a run of {:,.0f} iterations : {} seconds".format(STEPS, diff))
    print("lowest distance in run : {}".format(lowest_distance))

    final = {}
    final['orig_identifier'] = orig_uuid
    final['tiny_identifier'] = tiny_uuid
    final['distance'] = lowest_distance
    final['work_unit_numbmer'] = work_unit
    final['iteration'] = iteration
    final = json.dumps(final)
    req = requests.post(post_url, headers = {'content-type': 'application/json'}, data = final)





