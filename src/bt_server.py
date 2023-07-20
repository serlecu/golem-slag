import time
import threading
import asyncio

# import logging
from bless import (
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions
    )
from typing import Any
from typing import Sequence

import src.globals as g

# BLESS server vars
serverName: str
server: BlessServer
trigger: threading.Event = threading.Event()
notifyChar: BlessGATTCharacteristic

SERVICE_UUID:str = 'A07498CA-AD5B-474E-940D-16F1FBE7E8CD'
CHARACTERISTIC_UUID:str = '51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B'


# ======= BLESS server ======= #
# BLESS (BLE server) manages advertising and notification of characteristics

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
