import time
import random
import serial
import serial.tools.list_ports

import src.globals as g

railSerial:str = ""


def railSerialThread():
    portFound:bool = False
    arduino:serial.Serial = None

    while not g.killRail:
      port = findSerial()
      if port is not None:
        try:
          arduino = openSerial(port)
        except Exception as e:
          print(f"Serial ERROR: {e}")
          
        else:
          g.serialState = True

          while g.serialState:
              if not g.offlineMode:
                  try:
                    sendValueSerial(arduino, g.railDelay ) #send millis
                  except Exception as e:
                    print(f"Serial ERROR: {e}")
                    g.serialState = False
                    try:
                      arduino.__del__()
                    except Exception as e:
                      print(f"Serial ERROR: {e}")
                  finally:
                      time.sleep(2)
              else:
                  randomVal = random.randint(500, 1000)
                  sendValueSerial(arduino, randomVal)
        finally:
            time.sleep(2)


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
    arduino.write(str(value).encode('utf-8'))
