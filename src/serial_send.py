import time
import random
import serial
import serial.tools.list_ports
import asyncio

import src.globals as g

railSerial:str = ""

async def railSerialThreadAsync():
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
              try:
                if not g.offlineMode:
                  sendValueSerial(arduino, g.railDelay ) #send millis
                else:
                  randomVal = random.randint(500, 1000)
                  sendValueSerial(arduino, randomVal)
              except Exception as e:
                print(f"Serial ERROR: {e}")
                g.serialState = False
                try:
                  # arduino.__del__()
                  arduino.close()
                except Exception as e:
                  print(f"Serial ERROR: {e}")
              finally:
                  await asyncio.sleep(2)
        finally:
            await asyncio.sleep(2)

def railSerialThread():
    portFound:bool = False
    arduino:serial.Serial = None
    print("Serial Thread started")

    while not g.killRail:
      print("Serial Port Check")
      port = findSerial()
      if port is not None:
        try:
          arduino = openSerial(port.device)
        except Exception as e:
          print(f"Serial ERROR: {e}")
          
        else:
          g.serialState = True

          while g.serialState:
              if checkConnected(port):
                  if not g.offlineMode:
                      try:
                          sendValueSerial(arduino, g.railDelay ) #send millis
                      except Exception as e:
                          print(f"Serial ERROR: {e}")
                          g.serialState = False
                          try:
                              #arduino.__del__()
                              arduino.close()
                          except Exception as e:
                              print(f"Serial ERROR: {e}")
                      finally:
                          time.sleep(2)
                  else:
                      randomVal = random.randint(500, 1000)
                      sendValueSerial(arduino, randomVal)
              else:
                  g.serialState = False
                  try:
                      #arduino.__del__()
                      arduino.close()
                  except Exception as e:
                      print(f"Serial ERROR: {e}")
        finally:
            time.sleep(2)
        print("Lost Arduino connection")
      else:
        print("Arduino not found")
        time.sleep(2)
    print("Serial Thread killed")


def findSerial():
    global railSerial

    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "USB" in port.name:
            arduinoPort = port
            print(f"Serial Port: {arduinoPort}")
            return arduinoPort
    return None
    

def openSerial(port:str):
    device = serial.Serial(port, 9600)
    return device
    

def checkConnected(arduPort):
    ports = serial.tools.list_ports.comports()
    print(ports)
    if arduPort not in ports:
        print("Arduino Lost!")
        return False
    else:
        return True


def sendValueSerial(arduino:serial.Serial, value: int):
    arduino.write(f"{value}\n".encode())
