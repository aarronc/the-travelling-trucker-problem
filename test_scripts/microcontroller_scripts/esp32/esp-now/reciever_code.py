# Control Program
# Recieves request for work from the Node programs and distributes
# Work units.
# There are Several Json Action types.
# empty - This is normally sent from a ESP32 upon boot and it needs a Work Unit
# completed - This is sent with the attached completed work unit
# confirm - Used after receiving completed result. sent back to sender to confirm
# that result has been processed

# requests need to be closed to stop memory leaks or malfunctions of the requests.

import network
import time
import espnow
import machine
import requests #this has been saved manually to the ESP32
import json

STEP_COUNT = 1

NETWORK_SSID = 'Factor_Farm'
NETWORK_PASSWORD = 'FactorFarm#1#'

get_url = 'http://hot.forthemug.com:4567/work.json/{}'.format(STEP_COUNT)
post_url = 'http://hot.forthemug.com:4567/result'

led = machine.Pin(2, machine.Pin.OUT)


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

def do_connect():
    # A WLAN interface must be active to send()/recv()
    if not sta.isconnected():
        print('connecting to network...')
        sta.active(True)
        sta.connect(NETWORK_SSID, NETWORK_PASSWORD)
        while not sta.isconnected():
            pass
    print('network config:', sta.ifconfig())
    ap.active(True)
    sta.config(ps_mode=network.WIFI_PS_NONE) # Turning off power saving
    print("We are running on channel:", sta.config("channel"))
    
def give_work_unit(mac_address):
    req = requests.get(get_url)
    req_txt = req.text
    work_unit = json.loads((req_txt))
    work_unit['action'] = "work"
    json_work_unit = json.dumps(work_unit)
    send_over_esp_now(mac_address, json_work_unit)
    # print("Sent to Node : {}".format(json_work_unit))
    req.close()

def send_work_unit_to_server(mac_address, work_unit):
    confirm_receipt_of_message(mac_address)
    work_unit['truckers_at_home'] = 1
    work_unit['step_count'] = 1
    json_work_unit = json.dumps(work_unit)
    print("Comp: {} -> {}".format(mac_address, json_work_unit))
    req = requests.post(post_url, headers = {'content-type': 'application/json', 'esp32' : 'yes'}, data = json_work_unit)
    req.close()
    # give_work_unit(mac_address)
    
def send_over_esp_now(mac_address, msg):
    e.add_peer(mac_address)
    e.send(mac_address, msg)
    print("Sent: {} -> {}".format(mac_address, msg))
    e.del_peer(mac_address)
    
def confirm_receipt_of_message(mac_address):
    msg = {}
    msg['action'] = "confirm"
    msg = json.dumps(msg)
    send_over_esp_now(mac_address, msg)
    
def flash_blue_led(wait_time,num_of_flashes):
    for x in range(num_of_flashes):
        led.value(1)
        time.sleep(wait_time)
        led.value(0)
        time.sleep(wait_time)

sta, ap = wifi_reset()

do_connect()

e = espnow.ESPNow()
e.active(True)

while True:
    host, msg = e.recv()
    if msg == None:
        print("Nothing received this time...")
        continue
    else:
        print("Recv: {} M: {}".format(host, msg))
        mac_address = host
        msg = json.loads(msg)
        
        if msg['action'] == "empty":
            give_work_unit(mac_address)
            
        if msg['action'] == "completed":
            send_work_unit_to_server(mac_address, msg)
