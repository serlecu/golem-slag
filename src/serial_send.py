import time
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
        if g.railDelay > 0:
            sendValueSerial( int(g.railDelay * 1000) ) #send millis
        else:
            sendValueSerial(2000)
        time.sleep(1)

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
    
    


def sendValueSerial(value: int):
    
    arduino.write(b'9')
