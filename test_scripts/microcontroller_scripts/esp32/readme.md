When flashing the ESP32 you need to install the micropython bin file if you have not used the esp32 before you need to pip install the flash tool:

  python -m pip install esptool
 
You need to run the following command to erase the esp32 :

  python -m esptool –-chip esp32 erase_flash

and the following command to write micropython to the device :

  python esptool write_flash -z 0x1000 esp32-20220618-v1.19.1.bin