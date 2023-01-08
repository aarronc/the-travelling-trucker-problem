# Commander Program
# Recieves request for work from the node sender ESP32's
# Work units.
# There are Several Json Action types.
# empty - This is normally sent from a ESP32 upon boot and it needs a Work Unit
# completed - This is sent with the attached completed work unit

import network
import time
import espnow
import requests #this has been saved manually to the ESP32
import json

STEP_COUNT = 1

NETWORK_SSID = 'Factor_Farm'
NETWORK_PASSWORD = 'FactorFarm#1#'

get_url = 'http://hot.forthemug.com:4567/work.json/{}'.format(STEP_COUNT)
post_url = 'http://hot.forthemug.com:4567/result'


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
    work_unit = json.loads((requests.get(get_url).text))
    work_unit['action'] = "work"
    json_work_unit = json.dumps(work_unit)
    send_over_esp_now(mac_address, json_work_unit)
    print("Sent: {}".format(json_work_unit))

def send_work_unit_to_server(mac_address, work_unit):
    work_unit['truckers_at_home'] = 1
    work_unit['step_count'] = 1
    json_work_unit = json.dumps(work_unit)
    print("Completed : {}".format(json_work_unit))
    req = requests.post(post_url, headers = {'content-type': 'application/json', 'esp32' : 'yes'}, data = json_work_unit)
    give_work_unit(mac_address)
    
def send_over_esp_now(mac_address, msg):
    e.add_peer(mac_address)
    e.send(mac_address, msg)
    e.del_peer(mac_address)
    

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
        mac_address = host
        msg = json.loads(msg)
        print("From: {}, Message: {}".format(mac_address, msg))
        if msg['action'] == "empty":
            give_work_unit(mac_address)
            
        if msg['action'] == "completed":
            send_work_unit_to_server(mac_address, msg)