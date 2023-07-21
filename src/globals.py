# import simplepyble as ble
import pygame
import uuid
import time
import random


nodeID: str
lastLoopTime: float = 0.0


# Pygame
setupPygame: bool = False
screen: pygame.Surface


# Rail
i2cConnected = False
killRail: bool = False
lastEndSwitch: bool = False
railDirection: bool = True
railSpeed: int = 60
railDelay: float = 1.0
endSwitchCounter = 0
syncState = False
restartUSBFreq = 10.0
restartUSBCrono: float = 10.0


# Bluetooth BLEAK Client
setupBleak: bool = False
killBleak: bool = False
deviceInfo: str
isScanning: bool
scannCrono: float = 3.0
scannFrequency: float = 20.0
writeDevices = False
foundDevicesBleak: list#[BLEDevice]
# ~ matchedClients: list#[BleakClient]

isConnecting:bool = False
connectCrono: float = 0.0
connectFreq: float = 5.0
failedNotifications: list


# Bluetooth BLESS Server
serverLessMode: bool = False
setupBless: bool = False
runningBLEserver: bool = False


# Offline Mode
offlineMode: bool = False
offlineListLen: int
offlineMacList: list = [
    "SLAG_4e:dc:27 -> e4:5f:1:4e:dc:27",
    "SLAG_4e:09:7e -> e4:5f:1:4e:09:7e",
    "SLAG_4e:7c:71 -> e4:5f:1:4e:7c:71",
    "85:f5:75:ce:4a:e3",
    "7e:4b:74:3f:1b:7d",
    "a2:fd:1c:3f:97:9f",
    "ed:ac:0d:81:05:be",
    "9b:a5:2f:a2:9a:f9",
    "b4:12:78:ea:01:d7",
    "db:da:84:c9:95:66",
    "b2:88:a1:4a:58:bc",
    "b3:89:a7:94:39:5c",
    "d5:17:69:c1:3c:15",
    "b3:e3:15:e5:a7:65",
    "eb:67:71:68:d8:a2",
    "bf:a5:fb:0c:b0:47" ]#,
    # "d3:44:01:6b:48:a5",
    # "cf:d6:b4:d6:06:dd",
    # "33:c9:74:00:c1:9d" ]


def initGlobals():
  global lastLoopTime, scannCrono, scannFrequency, isScanning, foundDevices
  global deviceInfo, nodeID, foundDevicesBleak, offlineMode, offlineListLen
  
  lastLoopTime = time.time()
  nodeID = str(uuid.uuid1()).split("-")[1]

  scannCrono = 5
  # ~ scannFrequency = 10
  isScanning = False
  foundDevices = []
  foundDevicesBleak = []
  # ~ matchedClients = []
  deviceInfo = ""

  if offlineMode:
    offlineListLen = random.randint(10, 16)
    print(f"Offline Mode: {offlineListLen} devices")
  
  print(f"Initialize Golem Node #{nodeID}")


def shuffleOfflineList():
  global offlineMacList, offlineListLen

  offlineListLen = random.randint(10, 16)
  random.shuffle(offlineMacList)

  
