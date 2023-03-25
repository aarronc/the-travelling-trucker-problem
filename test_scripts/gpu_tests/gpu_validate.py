# Worker to recieve units to process
# created by Psymons and Entarius Fusion
# (c) 2022

# import backoff
import datetime
import json
import math
from os import system, name
# import requests
import sys
from time import sleep
import zlib

CMDR = "AnonCmdr" # Set this if you want credit to your Commander name
TEAM = "None" # If you have a team uuid, replace it inside the double quotes

# STEP_COUNT can be adjusted from 100 to 5000, 100 for short work units and 5000 for long ones
STEP_COUNT = 1000 # adjust this to make your work units longer or shorter

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

# Quick and dirty screen clearer that works with windows or linux
def clear():
  return 

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
version = "P.0.3.0"

# esp32's will request 1 to 5 depending on setup
# normal client will request 100 or more
# maximum currently is 5000
# 5000 should take a modern CPU around about 30 mins

# sorted first permutation for the int_to_perm lookup
# we are no longer importing a seed as the int_to_perm function
# now generates the seed for us from the iteration number
first_perm = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32]

# Psymons has implemented a 2d array, this is by far the fastest lookup option we have made so far
b =[0.0, 21.546875, 29.203125, 12.625, 31.09375, 22.296875, 18.328125, 10.421875, 32.75, 32.40625, 32.59375, 24.125, 56.6875, 12.375, 37.3125, 30.671875, 41.90625, 12.3125, 36.6875, 47.4375, 24.984375, 17.140625, 16.578125, 20.546875, 23.90625, 14.953125, 16.234375, 9.5390625, 26.515625, 20.9375, 28.640625, 21.5625, 12.40625], [21.546875, 0.0, 50.0, 11.0546875, 52.53125, 40.21875, 29.90625, 14.234375, 53.5, 53.625, 14.390625, 16.46875, 77.625, 25.921875, 54.96875, 51.3125, 58.1875, 21.390625, 16.375, 63.03125, 42.25, 35.5, 36.5, 39.3125, 18.453125, 33.59375, 37.53125, 24.71875, 44.4375, 39.375, 41.25, 33.625, 13.1015625], [29.203125, 50.0, 0.0, 40.90625, 12.9140625, 27.109375, 30.046875, 37.0625, 20.046875, 16.46875, 60.5, 47.34375, 35.84375, 27.390625, 35.15625, 16.734375, 41.125, 36.875, 65.1875, 47.3125, 30.890625, 26.96875, 22.8125, 15.40625, 44.8125, 26.84375, 16.8125, 31.65625, 26.734375, 24.171875, 40.84375, 37.53125, 38.0625], [12.625, 11.0546875, 40.90625, 0.0, 43.28125, 33.1875, 20.234375, 11.0859375, 43.125, 43.46875, 20.015625, 21.65625, 68.6875, 20.9375, 45.15625, 43.1875, 48.4375, 11.1640625, 24.453125, 55.1875, 32.71875, 25.421875, 26.25, 29.46875, 17.40625, 25.109375, 27.5, 14.1796875, 37.84375, 28.40625, 33.15625, 24.140625, 7.85546875], [31.09375, 52.53125, 12.9140625, 43.28125, 0.0, 19.9375, 36.25, 39.78125, 12.671875, 8.8125, 63.09375, 51.03125, 26.359375, 32.0, 25.6875, 7.95703125, 32.25, 37.09375, 67.4375, 35.21875, 23.640625, 23.140625, 19.9375, 23.5, 51.53125, 22.234375, 16.453125, 31.625, 19.03125, 23.421875, 33.5, 34.0, 42.46875], [22.296875, 40.21875, 27.109375, 33.1875, 19.9375, 0.0, 36.59375, 28.53125, 25.0625, 24.0625, 51.78125, 38.90625, 39.34375, 25.0625, 27.53125, 15.796875, 33.8125, 28.3125, 54.78125, 30.8125, 18.8125, 18.03125, 17.640625, 30.015625, 45.9375, 10.0703125, 17.828125, 23.875, 5.71875, 25.828125, 23.71875, 26.828125, 34.15625], [18.328125, 29.90625, 30.046875, 20.234375, 36.25, 36.59375, 0.0, 24.40625, 34.21875, 34.4375, 35.1875, 35.65625, 61.96875, 24.203125, 41.3125, 39.40625, 44.53125, 18.609375, 41.125, 56.5, 31.953125, 24.078125, 22.5, 14.828125, 20.875, 28.15625, 21.328125, 17.515625, 40.46875, 19.390625, 37.25, 26.203125, 18.65625], [10.421875, 14.234375, 37.0625, 11.0859375, 39.78125, 28.53125, 24.40625, 0.0, 42.875, 42.21875, 27.796875, 13.8671875, 64.9375, 12.078125, 46.9375, 38.0, 51.46875, 18.265625, 30.578125, 55.25, 34.3125, 27.0, 26.828125, 28.796875, 20.015625, 23.21875, 26.21875, 18.1875, 32.0625, 31.234375, 36.1875, 29.65625, 8.4453125], [32.75, 53.5, 20.046875, 43.125, 12.671875, 25.0625, 34.21875, 42.875, 0.0, 4.25390625, 61.71875, 55.8125, 30.109375, 37.75, 16.15625, 19.578125, 21.703125, 34.46875, 66.6875, 30.921875, 17.8125, 19.390625, 17.15625, 24.0625, 52.53125, 23.25, 16.90625, 29.546875, 26.546875, 16.984375, 27.90625, 27.96875, 43.96875], [32.40625, 53.625, 16.46875, 43.46875, 8.8125, 24.0625, 34.4375, 42.21875, 4.25390625, 0.0, 62.59375, 54.6875, 28.21875, 36.0, 19.78125, 16.28125, 25.671875, 35.625, 67.4375, 33.03125, 20.21875, 20.828125, 18.0, 22.84375, 52.15625, 23.359375, 16.265625, 30.4375, 24.828125, 18.75, 30.515625, 30.421875, 43.625], [32.59375, 14.390625, 60.5, 20.015625, 63.09375, 51.78125, 35.1875, 27.796875, 61.71875, 62.59375, 0.0, 29.71875, 88.25, 39.03125, 61.34375, 63.03125, 63.1875, 27.4375, 6.56640625, 70.375, 49.5, 43.375, 44.96875, 47.78125, 23.453125, 43.8125, 47.0625, 32.34375, 56.59375, 45.8125, 46.90625, 38.125, 23.828125], [24.125, 16.46875, 47.34375, 21.65625, 51.03125, 38.90625, 35.65625, 13.8671875, 55.8125, 54.6875, 29.71875, 0.0, 75.3125, 19.953125, 60.25, 48.0, 64.9375, 31.265625, 30.015625, 66.875, 47.59375, 40.65625, 40.375, 40.28125, 23.0, 35.78125, 39.125, 31.9375, 41.3125, 44.96875, 48.71875, 43.0, 17.703125], [56.6875, 77.625, 35.84375, 68.6875, 26.359375, 39.34375, 61.96875, 64.9375, 30.109375, 28.21875, 88.25, 75.3125, 0.0, 57.09375, 36.53125, 27.375, 41.3125, 61.53125, 92.3125, 37.21875, 42.34375, 45.96875, 43.9375, 48.84375, 77.875, 44.96875, 42.21875, 56.3125, 36.21875, 46.59375, 50.15625, 55.1875, 68.5], [12.375, 25.921875, 27.390625, 20.9375, 32.0, 25.0625, 24.203125, 12.078125, 37.75, 36.0, 39.03125, 19.953125, 57.09375, 0.0, 45.53125, 29.875, 51.0625, 24.5, 42.1875, 54.5, 34.125, 26.78125, 24.859375, 22.390625, 24.953125, 22.21875, 21.453125, 21.71875, 26.96875, 29.625, 39.09375, 33.5, 15.953125], [37.3125, 54.96875, 35.15625, 45.15625, 25.6875, 27.53125, 41.3125, 46.9375, 16.15625, 19.78125, 61.34375, 60.25, 36.53125, 45.53125, 0.0, 29.609375, 6.90234375, 34.71875, 65.875, 18.59375, 12.875, 20.296875, 21.46875, 35.875, 58.28125, 24.953125, 25.625, 31.203125, 30.453125, 22.046875, 18.015625, 23.4375, 48.59375], [30.671875, 51.3125, 16.734375, 43.1875, 7.95703125, 15.796875, 39.40625, 38.0, 19.578125, 16.28125, 63.03125, 48.0, 27.375, 29.875, 29.609375, 0.0, 36.46875, 38.1875, 66.75, 35.46875, 25.90625, 25.28125, 22.546875, 27.421875, 52.03125, 21.359375, 19.125, 32.84375, 12.984375, 28.09375, 34.53125, 36.25, 42.125], [41.90625, 58.1875, 41.125, 48.4375, 32.25, 33.8125, 44.53125, 51.46875, 21.703125, 25.671875, 63.1875, 64.9375, 41.3125, 51.0625, 6.90234375, 36.46875, 0.0, 37.53125, 67.8125, 20.0625, 17.515625, 24.8125, 26.5, 40.59375, 61.75, 30.421875, 31.1875, 34.78125, 37.03125, 25.6875, 19.8125, 25.15625, 52.5625], [12.3125, 21.390625, 36.875, 11.1640625, 37.09375, 28.3125, 18.609375, 18.265625, 34.46875, 35.625, 27.4375, 31.265625, 61.53125, 24.5, 34.71875, 38.1875, 37.53125, 0.0, 32.375, 45.875, 22.71875, 16.03125, 17.828125, 25.9375, 26.125, 18.625, 21.15625, 5.48828125, 33.65625, 19.296875, 23.265625, 13.109375, 16.828125], [36.6875, 16.375, 65.1875, 24.453125, 67.4375, 54.78125, 41.125, 30.578125, 66.6875, 67.4375, 6.56640625, 30.015625, 92.3125, 42.1875, 65.875, 66.75, 67.8125, 32.375, 0.0, 73.625, 53.8125, 47.96875, 49.71875, 53.125, 27.8125, 47.53125, 51.8125, 37.15625, 59.4375, 51.25, 50.59375, 42.8125, 27.90625], [47.4375, 63.03125, 47.3125, 55.1875, 35.21875, 30.8125, 56.5, 55.25, 30.921875, 33.03125, 70.375, 66.875, 37.21875, 54.5, 18.59375, 35.46875, 20.0625, 45.875, 73.625, 0.0, 24.65625, 32.71875, 34.5625, 50.84375, 70.4375, 32.84375, 38.5, 42.8125, 32.21875, 38.28125, 23.96875, 35.125, 59.15625], [24.984375, 42.25, 30.890625, 32.71875, 23.640625, 18.8125, 31.953125, 34.3125, 17.8125, 20.21875, 49.5, 47.59375, 42.34375, 34.125, 12.875, 25.90625, 17.515625, 22.71875, 53.8125, 24.65625, 0.0, 8.421875, 11.0, 28.546875, 46.65625, 13.1015625, 16.703125, 19.046875, 23.4375, 14.7578125, 10.4375, 13.21875, 36.3125], [17.140625, 35.5, 26.96875, 25.421875, 23.140625, 18.03125, 24.078125, 27.0, 19.390625, 20.828125, 43.375, 40.65625, 45.96875, 26.78125, 20.296875, 25.28125, 24.8125, 16.03125, 47.96875, 32.71875, 8.421875, 0.0, 4.21484375, 21.75, 38.46875, 9.09375, 10.6015625, 11.453125, 23.0625, 9.84375, 15.4296875, 11.2109375, 28.328125], [16.578125, 36.5, 22.8125, 26.25, 19.9375, 17.640625, 22.5, 26.828125, 17.15625, 18.0, 44.96875, 40.375, 43.9375, 24.859375, 21.46875, 22.546875, 26.5, 17.828125, 49.71875, 34.5625, 11.0, 4.21484375, 0.0, 18.0625, 37.78125, 9.640625, 6.48828125, 12.640625, 22.078125, 8.328125, 19.359375, 14.9609375, 28.0], [20.546875, 39.3125, 15.40625, 29.46875, 23.5, 30.015625, 14.828125, 28.796875, 24.0625, 22.84375, 47.78125, 40.28125, 48.84375, 22.390625, 35.875, 27.421875, 40.59375, 25.9375, 53.125, 50.84375, 28.546875, 21.75, 18.0625, 0.0, 31.859375, 24.515625, 13.2578125, 21.734375, 32.34375, 16.34375, 37.09375, 29.4375, 26.828125], [23.90625, 18.453125, 44.8125, 17.40625, 51.53125, 45.9375, 20.875, 20.015625, 52.53125, 52.15625, 23.453125, 23.0, 77.875, 24.953125, 58.28125, 52.03125, 61.75, 26.125, 27.8125, 70.4375, 46.65625, 38.46875, 37.78125, 31.859375, 0.0, 38.71875, 36.625, 27.90625, 49.5625, 37.90625, 49.15625, 38.8125, 12.3671875], [14.953125, 33.59375, 26.84375, 25.109375, 22.234375, 10.0703125, 28.15625, 23.21875, 23.25, 23.359375, 43.8125, 35.78125, 44.96875, 22.21875, 24.953125, 21.359375, 30.421875, 18.625, 47.53125, 32.84375, 13.1015625, 9.09375, 9.640625, 24.515625, 38.71875, 0.0, 12.15625, 14.0625, 15.5078125, 17.8125, 18.15625, 17.5625, 27.171875], [16.234375, 37.53125, 16.8125, 27.5, 16.453125, 17.828125, 21.328125, 26.21875, 16.90625, 16.265625, 47.0625, 39.125, 42.21875, 21.453125, 25.625, 19.125, 31.1875, 21.15625, 51.8125, 38.5, 16.703125, 10.6015625, 6.48828125, 13.2578125, 36.625, 12.15625, 0.0, 15.7109375, 21.078125, 10.9765625, 25.5625, 21.078125, 27.40625], [9.5390625, 24.71875, 31.65625, 14.1796875, 31.625, 23.875, 17.515625, 18.1875, 29.546875, 30.4375, 32.34375, 31.9375, 56.3125, 21.71875, 31.203125, 32.84375, 34.78125, 5.48828125, 37.15625, 42.8125, 19.046875, 11.453125, 12.640625, 21.734375, 27.90625, 14.0625, 15.7109375, 0.0, 29.078125, 15.1796875, 21.734375, 12.46875, 17.875], [26.515625, 44.4375, 26.734375, 37.84375, 19.03125, 5.71875, 40.46875, 32.0625, 26.546875, 24.828125, 56.59375, 41.3125, 36.21875, 26.96875, 30.453125, 12.984375, 37.03125, 33.65625, 59.4375, 32.21875, 23.4375, 23.0625, 22.078125, 32.34375, 49.5625, 15.5078125, 21.078125, 29.078125, 0.0, 29.953125, 28.765625, 32.375, 38.03125], [20.9375, 39.375, 24.171875, 28.40625, 23.421875, 25.828125, 19.390625, 31.234375, 16.984375, 18.75, 45.8125, 44.96875, 46.59375, 29.625, 22.046875, 28.09375, 25.6875, 19.296875, 51.25, 38.28125, 14.7578125, 9.84375, 8.328125, 16.34375, 37.90625, 17.8125, 10.9765625, 15.1796875, 29.953125, 0.0, 22.734375, 15.5234375, 30.1875], [28.640625, 41.25, 40.84375, 33.15625, 33.5, 23.71875, 37.25, 36.1875, 27.90625, 30.515625, 46.90625, 48.71875, 50.15625, 39.09375, 18.015625, 34.53125, 19.8125, 23.265625, 50.59375, 23.96875, 10.4375, 15.4296875, 19.359375, 37.09375, 49.15625, 18.15625, 25.5625, 21.734375, 28.765625, 22.734375, 0.0, 12.3125, 38.53125], [21.5625, 33.625, 37.53125, 24.140625, 34.0, 26.828125, 26.203125, 29.65625, 27.96875, 30.421875, 38.125, 43.0, 55.1875, 33.5, 23.4375, 36.25, 25.15625, 13.109375, 42.8125, 35.125, 13.21875, 11.2109375, 14.9609375, 29.4375, 38.8125, 17.5625, 21.078125, 12.46875, 32.375, 15.5234375, 12.3125, 0.0, 29.609375], [12.40625, 13.1015625, 38.0625, 7.85546875, 42.46875, 34.15625, 18.65625, 8.4453125, 43.96875, 43.625, 23.828125, 17.703125, 68.5, 15.953125, 48.59375, 42.125, 52.5625, 16.828125, 27.90625, 59.15625, 36.3125, 28.328125, 28.0, 26.828125, 12.3671875, 27.171875, 27.40625, 17.875, 38.03125, 30.1875, 38.53125, 29.609375, 0.0]

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
  # x = get_work_unit()

  # data = x.json()
  identifier = 0
  iteration = 0
  work_unit_step_count = 0
  steps = 1_000_000_000
  
  # sys.stdout.write("\r" + f"[{start_date}] ITR: {iteration:,} STARTED")
  # sys.stdout.flush()
  
  # the function that generated the initial seed that the main work loop uses
  ip = int_to_perm(int(iteration),first_perm[:])
  
  # The main work loop 
  # we are now doing 100M iterations (up from 10M as the run time was too fast)
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
     
    if distance < lowest_total:
      lowest_total = distance
      lowest_perm = ip[:]
      lowest_perm_int = perm_to_int(lowest_perm)
      
      
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
  final['cmdr'] = CMDR
  final['team'] = TEAM
  final['identifier'] = identifier
  final['distance'] = lowest_total
  final['duration'] = str(diff)
  final['finished_at'] = finish_date
  final['version'] = version
  final['truckers_at_home'] = 1
  final['lowest_perm_int'] = lowest_perm_int
  final['step_count'] = work_unit_step_count
  final = json.dumps(final)
  sys.stdout.write("\r[{}] ITR: {:,.0f} FINISH: {} LOWEST: {}".format(finish_date, iteration, diff, lowest_total))
  sys.stdout.flush()
  # Send the final list to the server
  # send_work_unit(final)
  print(final)
  break