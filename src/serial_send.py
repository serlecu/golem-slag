import time
import random
import serial
import serial.tools.list_ports

import src.globals as g

railSerial:str = ""


def railSerialThread():
    portFound:bool = False
    arduino:serial.Serial = None

    while not portFound:
      port = findSerial()
      if port is not None:
        arduino = openSerial(port)
        portFound = True
      time.sleep(1)

    while not g.killRailSerial:
        if not g.offlineMode:
            sendValueSerial(arduino, g.railDelay ) #send millis
        else:
            randomVal = random.randint(500, 1000)
            sendValueSerial(arduino, randomVal)
        time.sleep(2)

    if arduino is not None:
      arduino.close()

def findSerial():
    global railSerial

    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "USB" in port.name:
            railSerial = port.device
            print(f"Serial Port: {railSerial}")
            return railSerial
    return None
    

def openSerial(port:str):
    device = serial.Serial(port, 9600)
    return device
    
    


def sendValueSerial(arduino:serial.Serial, value: int):
    # Translate value int to bytes
    byteValue = value.to_bytes(2, byteorder='big')
    arduino.write(byteValue)
