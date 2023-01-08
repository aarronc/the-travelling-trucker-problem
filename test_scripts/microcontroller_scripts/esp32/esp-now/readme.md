ESP-NOW is used here to make a collection of ESP32's communicate with only 1 ESP32 that is connected to Wifi and the others processing the work units without the use of a Wifi connection (This saves on IP addresses assigned to the ESP32's using the standard worker.py code in the main folder)

The ESP-NOW library is not available in the main MicroPython code base and has been included in custom Binaries from the link below :
    https://github.com/glenn20/micropython-espnow-images

This code has been tested using the firmware-esp32-GENERIC_C3.bin
I have included it in the folder but you can download a copy from the link below
    https://github.com/glenn20/micropython-espnow-images/blob/main/20220709_espnow-g20-v1.19.1-espnow-6-g44f65965b/firmware-esp32-GENERIC_C3.bin

Documentation for the MicroPython port of ESP-NOW can be found here:
    https://micropython-glenn20.readthedocs.io/en/latest/library/espnow.html

You Will need to flash your ESP32's with the custom firmware-esp32-GENERIC_C3.bin before you will be able to use the espnow library.

When flashing the ESP32 you need to install the micropython firmware-esp32-GENERIC_C3.bin. If you have not used the esp32 before you need to pip install the flash tool:

  python -m pip install esptool
 
You need to run the following command to erase the esp32 :

  python -m esptool –-chip esp32 erase_flash

and the following command to write micropython to the device :

  python -m esptool write_flash -z 0x1000 firmware-esp32-GENERIC_C3.bin



The control ESP32 uses the reciever_code.py
  Only 1 of the ESP32's need to run this script.
  When running the code the output will include the line
    'We are running on channel <x>'
  Channel x is the number of the channel your Wifi network is on. It is important that you change the SSID_CHANNEL_NUMBER variable on line 23 of the sender_code.py to your Wifi channel number so that the ESP32's that are running the sender_code.py know what channel to send their information on.
  It is also a good idea if possible to disable the Wifi from automatically changing this value as some routers do this and can lead to loss of communication to the ESP32 Nodes.

  Copy the requests.py file onto your ESP32 as the custome firmware does not include this in it's library.

  a find_mac_address.py has been included, run this on your control ESP32 and it will give you the bytes string of your control ESP32's mac address, you'll need this as you need to alter the peer varible on line 168 to the your mac address

The node ESP32's use the sender_code.py
  Once you have the control ESP32 set up using the above code, remember to change the following:
    1. SSID_CHANNEL_NUMBER on line 23 to the correct number given to you on the control ESP32 code output window.
    2. the peer variable on line 168 to your control ESP32's mac address by running find_mac_address.py on your control ESP32
  
  After that, all you need to do is run this code on your ESP32 and it will ask for, work on, send and confirm the send of work units as they are issued.

There Should be no limit to the number of ESP32's you can add to this cluster, i have only tested with 7 ESP32's but as long as every ESP32 has a unique mac address then every node in the cluster should be able to get work and process it.
