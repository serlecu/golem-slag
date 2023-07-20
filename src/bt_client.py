import time
import threading
import asyncio

# import logging
from typing import Any

from bleak import BleakScanner, BleakClient

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
TARGET_SERVICE:str = 'A07498CA-AD5B-474E-940D-16F1FBE7E8CD'


# BLEAK (BLE client) manages deviceDiscovery, connections and subscription



def setupBTAdapter():
    global scanner
    print("Initializing Bluetooth...")
    
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
    # global scanner
    g.killBleak = False
    devices: Sequence[BLEDevice]
    
    while not g.killBleak:
        
      print("BLEAK: start scanning")
      g.isScanning = True
      # 1. Scann
      try:
        devices = await BleakScanner.discover(timeout=5)
      except Exception as e:
        print(f"BLEAK 73: {e}")
        g.isScanning = False 
      else:
        print("BLEAK: end scanning")
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
  
                
def filterDevice(device, targetService):
    global matchedDevices, matchedClients, serverName
    
    # ~ print(f"BLESS: filter {device.name}")
    if ("SLAG_" in device.name) and (device.name is not serverName):
        # ~ client = BleakClient(device)
        if (device in matchedDevices):
            print(f"BLEAK alert: Device [{device.name}] already stored.")
        elif (device in connectedDevices):
            print(f"BLEAK alert: Device [{device.name}] already connected.")
        else:
            print(f"BLEAK: Match [{device.name}].")
            # device.disconnected_callback = (lambda d=device: onDisconnectedDeviceBleak(d))
            matchedDevices.append(device)
            # ~ matchedClients.append(client)


# ========= HANDLE CONNECTIONS ===========
                    
# BLEAK
def handleBTConnections():
    global devicesChecked, matchedDevices, matchedClients, connectingClients 
    g.isConnecting = True
    print("Handling connections")
    
    if (not g.isScanning) and (not devicesChecked):
        if len(matchedDevices) > 0:  
            checkMatched = []
            for device in matchedDevices:
                # Check and correct duplicates
                if device in checkMatched:
                    matchedClients.remove(device)
                    continue
                
                client = BleakClient(device)
                # Filter connected and connecting    
                if client.is_connected:
                    print(f"BLEAK alert: Device [{client.address}] already connected.")
                else:
                    if client in connectingClients:
                        print(f"BLEAK alert: Device [{client.address}] already connecting.")
                    else:
                        # ~ try:
                            # ~ await connectBleak(device)
                        # ~ except Exception as e:
                            # ~ print(f"BLEAK ERROR: 137 - {e}")
                        connectingClients.append(client)
                        connect_thread = threading.Thread(target=lambda d=device: handleClientBleak(d), daemon=True)
                        connect_thread.start()
                            
                #flag for duplicates        
                checkMatched.append(device)
                
    time.sleep(10)
    g.isConnecting = False
    
    
# BLEAK - dirty async inside thread    
def handleClientBleak(device):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(connectBleak(device))
    

# BLEAK
async def connectBleak(device):
    global connectingClients
    
    async with BleakClient(device) as client:
        print(f"BLEAK: Connecting to {client.address} ...")
        counter = 3
        while counter > 0:
            try:
                await client.connect()
            except Exception as e:
                print(f"BLEAK ERROR: Failed to connect to {client.address}. {e}")
                if client in connectingClients:
                    connectingClients.remove(client)
                    counter -= 1
                    await asyncio.sleep(3)
            else:
                await onConnectedDeviceBleak(client)
                break
    

# BLEAK
async def onConnectedDeviceBleak(client):
    print(f"BLEAK: Connection success {client.address}")
    
    counter = 3
    while counter > 0:
        try:
            # subscribe to the one characteristic notifications
            await client.start_notify(char_specifier=CHARACTERISTIC_UUID, callback=onCharacNotified )
        except Exception as e:
            print(f"BLEAK ERROR: on notify. {e}")
            counter -= 1
            await asyncio.sleep(3)
        else:
            print(f"BLEAK: success subribing to {CHARACTERISTIC_UUID} of {client.address}")
            break
    connectingClients.remove(client)
    
    
# BLEAK
def onCharacNotified(char, byteArray):
    data = byteArray.decode()
    clientName: str = "SLAG_"+data[:3]
    print(f"BLEAK: Recieved msg from {clientName}: {data}")
    if data[-2:] == "01":
        g.syncState = True
    else:
        g.syncState = False


# BLEAK
def onDisconnectedDeviceBleak(device):
    global connectingClients
    print(f"BLEAK alert: Device[{device.address}] disconnected")
    if device in g.matchedDevices:
        g.matchedDevices.remove(device)