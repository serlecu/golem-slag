import time
import threading
import asyncio

# import logging
from typing import Any

from bleak import BleakScanner, BLEDevice

from typing import Sequence

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

    # asyncio.set_event_loop_policy(asyncio.ThreadedEventLoopPolicy())
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(scann())
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

          # 3. Send values to rail
          # ~ g.railSpeed = 50 + ( len(devices) * 5 )
          # ~ g.railDelay = 1.0 - ( len(devices) * 0.07 )
          # if len(devices) > 0:
          #     g.railDelay = 1.0 / len(devices)
          # else:
          #     g.railDelay = 1.0
            
        await asyncio.sleep(10)