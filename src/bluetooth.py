import time
import threading
import asyncio
import random

# import bluetooth as bt
# import simplepyble as ble

import bless
from bless import (
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions
    )

import logging
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

# BLESS server vars
serverName: str
server: BlessServer
trigger: threading.Event = threading.Event()
notifyChar: BlessGATTCharacteristic

SERVICE_UUID:str = 'A07498CA-AD5B-474E-940D-16F1FBE7E8CD'
CHARACTERISTIC_UUID:str = '51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B'


# BLEAK (BLE client) manages deviceDiscovery, connections and subscription
# BLESS (BLE server) manages advertising and notification of characteristics



def setupBTAdapter():
    global scanner
    print("Initializing Bluetooth...")
    
    scanner = BleakScanner()
    
    g.setupBleak = True
    

def bleakLoopThread():
    asyncio.run(bleakLoopAsync())

    
async def bleakLoopAsync():
    # global scanner
    g.killBleak = False
    devices: Sequence[BLEDevice]
    
    while not g.killBleak:
        
      print("BLEAK: start scanning")
      g.isScanning = True
      # async with BleakScanner() as scanner:
      # 1. Scann
      try:
        await updateScanResoults(scanner)
      except Exception as e:
        print(e)
        try:
          await scanner.stop()
        except Exception as e:
          print(e)
        g.isScanning = False
        await asyncio.sleep(2)
      else:
        g.isScanning = False
        # ~ if len(connectingClients) < 1:
            # ~ try:
                # ~ await asyncio.sleep(5)
                # ~ devices = scanner.discovered_devices
            # ~ except Exception as e:
                # ~ print(f"BLEAK 73: {e}")
                # ~ await asyncio.sleep(5)
            # ~ else:
                # ~ g.foundDevicesBleak = list(devices)
                # ~ # g.railSpeed = 50 + ( len(devices) * 5 )
                # ~ g.railDelay = 1.0 - ( len(devices) * 0.07 )
        # ~ await asyncio.sleep(2)
        
        
        # 2. Pick & Filter 
        print("BLEAK: Filtering Found Devices...")
        for device in g.foundDevicesBleak :
            filterDevice(device, TARGET_SERVICE)
        print("BLEAK: ...end filtering Found Devices.")
                
        # 3. Connect
        # print("BLEAK: start connecting")
        # for d in matchedDevices:
        #     if device in connectedDevices:
        #         continue
        #     else:
        #         async with BleakClient(d) as client:
        #             print(f"BLEAK: Start Client {client.address}")
        #             print(f"{client.address} is connected {client.is_connected}")
        #             connectedDevices.append(d)
                    
        #             # 4. Subscribe to notify
        #             try:
        #                 await client.start_notify(
        #                                 char_specifier=CHARACTERISTIC_UUID, 
        #                                 callback=onCharacNotified 
        #                                 )
        #             except Exception as e:
        #                 print(f"BLEAK ERROR: on notify. {e}")
        #                 await asyncio.sleep(3)
        #             else:
        #                 print(f"BLEAK: success subribing to {CHARACTERISTIC_UUID} of {client.address}")
        #                 keepConnected = True
        #                 while keepConnected:
        #                     await asyncio.sleep(10)
        #                     await updateScanResoults(scanner)
                            
        #             finally:
        #                 try:
        #                     await client.unpair()
        #                 except Exception as e:
        #                     print(f"BLEAK ERROR: {e}")
        #                 finally:
        #                     connectedDevices.remove(d)
        #                     print(f"BLEAK: End Client {client.address}")   
        #await scanner.stop()
      # g.isScanning = False      
      await asyncio.sleep(10)


async def updateScanResoults(scanner):
  await asyncio.sleep(5)
  try:
      # devices = await BleakScanner.discover(timeout=5.0)
      await scanner.start()
      await asyncio.sleep(5)
      await scanner.stop()
      devices = scanner.discovered_devices
  except Exception as e:
      print(f"BLEAK 73: {e}")

  else:
      if len(devices) > 16:
        devices = devices[:16]
      g.writeDevices = True
      g.foundDevicesBleak = list(devices)
      g.writeDevices = False
      # ~ g.railSpeed = 50 + ( len(devices) * 5 )
      # ~ g.railDelay = 1.0 - ( len(devices) * 0.07 )
      # if len(devices) > 0:
      #     g.railDelay = 1.0 / len(devices)
      # else:
      #     g.railDelay = 1.0
      
  # await asyncio.sleep(2)
  print("BLEAK: end scanning")
  
                
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
        
        
# ======= BLESS server ======= #

# BLESS Server
async def initServerAsync(loop):
    global trigger, server, serverName
    
    print("BLESS: Setting up BLE Server...")
    
    gatt:Dict = {
        SERVICE_UUID: {
            CHARACTERISTIC_UUID:{
                "Properties": GATTCharacteristicProperties.notify,
                "Permissions": GATTAttributePermissions.readable,
                "Value": str(g.nodeID+"00").encode()
            },
        }
    }
    
    # ~ trigger.clear()
    
    serverName = "SLAG_" + g.nodeID
    print(serverName)
    
    server = BlessServer(name=serverName, name_overwrite=True, loop=loop)
    
    
    # --- without gatt ---
    try:
        await server.add_new_service(SERVICE_UUID)
    except Exception as e:
        print(f"BLESS: Error adding Service: {e}")
    else:
        print(f"BLESS: service added {SERVICE_UUID}")
        
    try:
        await server.add_new_characteristic( SERVICE_UUID,
                                   CHARACTERISTIC_UUID,
                                   ( GATTCharacteristicProperties.read |
                                     GATTCharacteristicProperties.write |
                                     GATTCharacteristicProperties.notify ),
                                    str(g.nodeID+"00").encode(),
                                   ( GATTAttributePermissions.readable |
                                     GATTAttributePermissions.writeable ) )
    except Exception as e:
        print(f"BLESS: Error adding characteristic: {e}")
    else:
        print(f"BLESS: characteristic added {CHARACTERISTIC_UUID}")
        
        notifyChar = server.get_characteristic(CHARACTERISTIC_UUID)
        print(notifyChar)
        
    # ~ print("BLESS: Starting BLE server...")
    # ~ try:
        # ~ g.runningBLEserver = await server.start()
    # ~ except:
        # ~ print("BLESS: Error on advertising services")
        # ~ return False
    # ~ else:
        # ~ g.runningBLEserver = True
        # ~ print("BLESS: Advertising.")
        
        # ~ bless_thread = threading.Thread(target=runBlessListener(), daemon=True)
        # ~ bless_thread.start()
    # ~ print("BLESS: async done")
    await server.start()
    
    # --- With gatt ---
    # ~ await server.add_gatt(gatt)
    # ~ await server.start()
    
    if await server.is_advertising():
        print("BLESS: server up and running!")
        g.setupBless = True
    else:
        print("BLESS ERROR: server not advertising")


# BLESS        
def runBlessListener():
    global trigger, server
    
    while g.runningBLEserver:
        try:
            print("BLESS: waiting requests.")
            trigger.wait()
            trigger.clear()
            print("BLESS: back to listen.")
        except Exception as e:
            print(f"BLESS listener Error: {e}.")
        
    print("BLESS: end server")
    loop.close()
    server.stop()
    

# BLESS - server
def handleBTData():
    global server

    if g.endSwitchCounter > 1:
        print("BLESS: notify endSwitch")
        try:
            notify(server, g.nodeID+"01" )
        except Exception as e:
            print(f"BLESS ERROR: couldn't get characteristic. {e}")
        else:
            g.endSwitchCounter = 0

            
def notify(server, value:str):
    server.get_characteristic(CHARACTERISTIC_UUID,).value = value.encode() 
    server.update_value(SERVICE_UUID, CHARACTERISTIC_UUID)
        
        
# BLESS
def onReadRequest_Other(conn_handle: int, attr_handle: int, value: bytes):
    print(f"BLESS: received {value}")

def onReadRequest( char: BlessGATTCharacteristic,
                   **kwargs
                   ) -> bytearray:
    global logger
    
    logger.debug(f"BLESS: Reading {characteristic.value}")
    return char.value

def onWriteRequest( char: BlessGATTCharacteristic,
                    value: Any,
                   **kwargs ):
    global logger, trigger
    
    print(f"BLESS: Write request - {char} -> {value}")
    
    
    char.value = value
    logger.debug(f"Char value set to { char.value}")
    if char.value == b'\x0f':
        logger.debug("NICE")
        trigger.set()
