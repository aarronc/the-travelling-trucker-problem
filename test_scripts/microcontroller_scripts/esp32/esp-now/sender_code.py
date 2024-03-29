# Note: ESP32 has a lack of compression for zlib or uzlib
# modules, setting the esp32 : 'yes' in the header information
# when sending the result prompts the server not to try and
# uncompress the data when its sent, going to have to use this
# workaround until they implement something in the stdlib for Micorpython

import espnow
import gc
import json
import machine
import math
import network
import time

# Commander and team attribution are handled by the Control ESP32, all of these nodes server the Control ESP32

STEP_COUNT = 1 # adjust this to make your work units longer or shorter. Esp32's will request 1, normal client will request 100 to 5000

# Remember to set your networks username and password
NETWORK_SSID = 'Factor_Farm'
NETWORK_PASSWORD = 'FactorFarm#1#'

SSID_CHANNEL_NUMBER = 6 # Set this to the SSID channel number your control ESP32 Wifi uses

led = machine.Pin(2, machine.Pin.OUT) # Set the LED for ESP32's that have them

# Set the ESP32 clock speed to maximum supported
machine.freq(240000000)

# Enable Garbage collection, this is to mainly help
# with the creation of the large 2D array
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
    
def int_to_perm(n,elems):#with n from 0
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

def flash_blue_led(wait_time,num_of_flashes):
    for x in range(num_of_flashes):
        led.value(1)
        time.sleep(wait_time)
        led.value(0)
        time.sleep(wait_time)
    
def wifi_reset():   # Reset wifi to AP_IF off, STA_IF on and disconnected
  sta = network.WLAN(network.STA_IF); sta.active(False)
  ap = network.WLAN(network.AP_IF); ap.active(False)
  sta.active(True)
  while not sta.active():
      time.sleep(0.1)
  sta.disconnect()   # For ESP8266
  while sta.isconnected():
      time.sleep(0.1)
  return sta, ap

def send_over_esp_now(mac_address, message):
    e.send(mac_address, message)

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

version = "ESP32 0.3.0"
flash_blue_led(1,1)


get_url = 'http://hot.forthemug.com:4567/work.json/{}'.format(STEP_COUNT)
post_url = 'http://hot.forthemug.com:4567/result'

# Reset of the WiFi chip to a known state
sta, ap = wifi_reset()

# Connect to ESP-NOW network

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.config(channel= SSID_CHANNEL_NUMBER)
sta.disconnect()   # For ESP8266

e = espnow.ESPNow()
e.active(True)
peer = b'\x08\xb6\x1f)\xff\xc0'   # MAC address of control ESP32
e.add_peer(peer)

# Perform a garbage collection before the creation of the 2D array, sometimes
# the json parsing of the above list would cause the 2D array to fail with 
# not enough memory errors
gc.collect()

# construct a JSON string to send to tell the Control ESP32 we are alive and awaiting work units
init_json_string = {}
init_json_string['action'] = 'empty'
init_json_string = json.dumps(init_json_string)

# Creation of the 2D array
b = {}
b = [[0 for i in range(33)] for j in range(33)]
for x in range(33):
  gc.collect() # called as the array needs memory freeing after every couple of x iterations or it will run out and crash
  for y in range(33):
    if x == y: 
      continue 
    else:
      b[x][y] = math.sqrt(((lookup[str(x)]["x"] - lookup[str(y)]['x']) ** 2) + ((lookup[str(x)]['y'] - lookup[str(y)]['y']) ** 2) + ((lookup[str(x)]['z'] - lookup[str(y)]['z']) ** 2))


print("Telling the Control ESP32 we are alive ") # This Signals our need for a work unit
e.send(peer, init_json_string)
while True:
  
    if not sta.isconnected():
        sta.active(True)
    
    print("Waiting for Message...")
    host, msg = e.recv(5000) # Wait for a message from the control ESP32 for 5 seconds
    
    if msg == None:
        print("No msg Found. Telling the Control Server we are empty")
        a = e.send(peer, init_json_string, True)
        print (a)
        continue
    
      
    # Parse the data from the server
    data = json.loads(msg)
    
    if data['action'] == "sleep":
        print("We have been told to sleep, see you in 5 seconds....")
        sleep(5)
        continue
    
    if data['action'] == "Confirm":
        print("Recieved a rouge confirm message, this shouldnt be here")
        sleep(5)
        continue
    
    print("Beginning Work ...")
    # Split out the data we need
    uuid = data['identifier']
    iteration = data['iteration']
    work_unit_step_count = int(data['step'])
    steps = work_unit_step_count * 1_000_000 # Normally Set to 1_000_000
    
    lowest_distance = 9999
    lowest_perm = []
    lowest_perm_int = 0
    
    first_perm = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32]
    
    
    ip = int_to_perm(iteration, first_perm[:])
    start = time.time()
    y = 0
    print("Unit : {:,} ({:,} iterations)".format(iteration, steps))
    
    # Main work loop
    for x in range(steps):
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
          
        if distance < lowest_distance:
            lowest_distance = distance
            lowest_perm = ip[:]
            lowest_perm_int = perm_to_int(lowest_perm)
    
        if y == 10_000: # Normally set to 10_000 to report the progress in 10_000 step chunks
            print ("Checkpoint {:,} / {:,}".format(x, steps))
            y = 0
        
        y += 1           
        ip = next_lexicographic_permutation(ip)
    
    finish = time.time()
    diff = finish - start
    print("Time Taken for a run of {:,.0f} iterations : {} seconds".format(steps, diff))
    print("lowest distance in run : {}".format(lowest_distance))

    final = {}
    final['action'] = "completed"
    # final['cmdr'] = CMDR
    # final['team'] = TEAM
    final['identifier'] = uuid
    final['distance'] = lowest_distance
    final['duration'] = str(diff)
    final['version'] = version
    final['lowest_perm_int'] = lowest_perm_int
    # final['step_count'] = work_unit_step_count
    # final['truckers_at_home'] = 1
    final = json.dumps(final)
    
    print(final)
    
    # check if we are still connected
    if not sta.isconnected():
      sta.active(True)
          
    # post the data back to the server
    send_over_esp_now(host, final)
    
    while True:
        host, msg = e.recv(5000)
        if msg == None:
            print("No Confirm... resending result")
            final = json.loads(final)
            final['resend'] = 1
            final = json.dumps(final)
            send_over_esp_now(host, final)
        else:
            msg = json.loads(msg)
            if msg['action'] == "confirm":
                print("Result has been confirmed")
                break
    
    # Flash LED's to indicate we are done with a unit
    flash_blue_led(0.5,2)
