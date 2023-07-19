import time
import os
import threading
import pygame
import random

from src.bluetooth import *
from src.graphics import *
from src.debug_display import *
# from src.rail import *

# import simplepyble as ble

def Setup():
  import src.globals as g

  g.initGlobals()
  
  # Init Rail
  # try:
  #   initRail()
  # except Exception as e:
  #   print(e)
  # else:
  #   g.i2cConnected = True
     
  # rail_thread = threading.Thread(target=railControl, daemon=True)
  # rail_thread.start()
  

  # Initialize Pygame
  print("PYGAME INIT")
  os.environ["DISPLAY"] = ":0"
  pygame.init()
  
  # get os
  platform_os = os.uname()[0]
  print("OS: " + platform_os)

  if platform_os == "Darwin":
    g.screen = pygame.display.set_mode((480,480))
  else:
    g.screen = pygame.display.set_mode((480,480),pygame.FULLSCREEN)
    # ~ g.screen = pygame.display.set_mode((480,480))
  pygame.display.set_caption("Golem: Display Node")
  pygame.mouse.set_visible(False)
  g.setupPygame = True

  # Initialize BLEAK Client
  if not g.offlineMode:
    setupBTAdapter()
  
  # Initialize BLESS Server
  if not g.offlineMode:
    if not g.serverLessMode:
      loop = asyncio.get_event_loop()
      loop.run_until_complete(initServerAsync(loop))
  
  
# End of Setup() ========================================


def Update():
  import src.globals as g
  
  if not g.offlineMode:
    scan_thread = threading.Thread(target=bleakLoopThread, daemon=True)
    scan_thread.start()

  while True:
    
    #Handle Bluetooth device scanning
    if g.offlineMode:
       #turn state of g.isScanning each 10 seconds
      if g.scannCrono <= 0:
        if g.isScanning:
          g.shuffleOfflineList()
          g.isScanning = False
          g.scannCrono = 5
        else:
          g.isScanning = True
          g.scannCrono = 10
    else: #onlineMode
      if((not g.isScanning) and (g.scannCrono <= 0)):
        g.scannCrono = g.scannFrequency
        #g.scannCrono = round(random.uniform(g.scannFrequency, g.scannFrequency+5.0), 2)
        scan_thread = threading.Thread(target=scanBT, daemon=True)
        scan_thread.start()
    # End of handle Bluetooth device scanning
       
    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Quit the application if the X button is pressed
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Quit if the 'esc' key is pressed
                pygame.quit()
                quit()
    # End of Handle Pygame events

    # Handle Bluetooth connections
    # ~ if (g.isConnecting == False) and (g.connectCrono <= 0) and (g.isScanning == False):
      # ~ connect_thread = threading.Thread(target=handleBTConnections(), daemon=True)
      # ~ connect_thread.start()
      # ~ asyncio.run(handleBTConnections())
      # ~ g.connectingCrono = round(random.uniform(g.connectFreq, g.connectFreq+5.0), 2)
    # End of Handle Bluetooth connections

    # Handle Bluetooth notifications
    if not g.offlineMode:
      if not g.serverLessMode:
        handleBTData()

    # Draw graphics on the screen
    DrawLoop()
    #DrawDebugLayer()

    # Update the Pygame display
    pygame.display.update()

    # Restart USB power if time to do so
    # if g.restartUSBCrono <= 0:
    #   print("Restarting USB")
    #   #os.system("sudo systemctl restart usbmount")
    #   os.system("/sys/devices/platform/soc/20980000.usb/buspower")
    #   g.restartUSBCrono = g.restartUSBFreq


    # Update Timers
    g.restartUSBCrono -= (time.time() - g.lastLoopTime)

    if g.offlineMode:
      if(g.scannCrono > 0):
        g.scannCrono -= (time.time() - g.lastLoopTime)
      g.lastLoopTime = time.time()

    else:
      if(g.scannCrono > 0):
        if (g.isScanning == False):
          g.scannCrono -= (time.time() - g.lastLoopTime)
        # if (g.isConnecting == False):
        #   g.connectCrono -= (time.time() - g.lastLoopTime)

      g.lastLoopTime = time.time()

  # End of Update() ========================================
    

# Start the event loop
if __name__ == "__main__":
  Setup()
  Update()
