import time
import threading
import asyncio
from typing import Any
from typing import Sequence
from bleak import BleakScanner, BLEDevice

# from memory_profiler import profile
# import logging


import src.globals as g

# General BLE flags and arrays
devicesChecked: bool = False
matchedDevices = []
connectedDevices = []
connectingClients = []
matchedClients = []

# BLEAK scanner vars
scanner: BleakScanner


def setupBTAdapter():
    global scanner
    # print("Initializing Bluetooth...")
    
    scanner = BleakScanner()
    
    g.setupBleak = True
    

def bleakLoopThread():
    asyncio.run(bleakLoopAsync())

    asyncio.set_event_loop_policy(asyncio.ThreadedEventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bleakLoopAsync())
    # loop.close()

    
async def bleakLoopAsync():
    g.killBleak = False
    devices: Sequence[BLEDevice]
    
    while not g.killBleak:
        
        # print("BLEAK: start scanning")
        g.isScanning = True
        # 1. Scann
        try:
          devices = await BleakScanner.discover(timeout=5)
        except Exception as e:
          print(f"BLEAK 73: {e}")
          g.isScanning = False 
        else:
          # print("BLEAK: end scanning")
          g.isScanning = False 

          # 2. Write resoults
          if len(devices) > 16:
            devices = devices[:16]
          g.writeDevices = True
          g.foundDevicesBleak = list(devices)
          g.writeDevices = False

          # 3. Update rail values
          if len(devices) == 0:
              g.railDelay = 2000
          elif len(devices) < 25:
              g.railDelay = int(1500 / (len(devices)+1))
          else:
              g.railDelay = 1500
            
        await asyncio.sleep(10)