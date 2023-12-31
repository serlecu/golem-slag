import time
import threading
import pygame

from src.bt_client import *
from src.bt_server import *
from src.graphics import *
from src.debug_display import *
from src.serial_send import *

def Setup():
  import src.globals as g

  g.initGlobals()

  # Initialize Pygame
  setupPygame()

  # Initialize BLEAK Client
  if not g.offlineMode:
    setupBTAdapter()
  
  # Initialize BLESS Server
  if not g.offlineMode:
    if not g.serverLessMode:
      loop = asyncio.get_event_loop()
      loop.run_until_complete(initServerAsync(loop))

  # Initialize Serial
  # loop = asyncio.get_event_loop()
  # loop.run_until_complete(railSerialThreadAsync())
  serialThread = threading.Thread(target=railSerialThread, daemon=False)
  serialThread.start()

  
  
# End of Setup() ========================================


def Update():
  import src.globals as g
  count = 0
  
  # Start Bluetooth device scanning thread (online mode)
  if not g.offlineMode:
    # # not thread but async ver
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(bleakLoopAsync(loop))
    # #

    scan_thread = threading.Thread(target=bleakLoopThread, daemon=False)
    # daemon is false so the thread has to be killed manualy before closing main thread
    scan_thread.start()
  # End of Start Bluetooth device scanning thread (online mode)

  # Update Loop
  while True:
    
    #Handle Bluetooth device scanning (offline mode)
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
    # End of Bluetooth device scanning (offline mode)
       
    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Quit the application if the X button is pressed
            pygame.quit()
            g.killBleak = True
            g.runningBLEserver = False
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Quit if the 'esc' key is pressed
                pygame.quit()
                g.killBleak = True
                g.runningBLEserver = False
                quit()
    # End of Handle Pygame events

    # Draw graphics on the screen
    DrawLoop()
    UpdateDisplay()
    # end of Draw graphics on the screen

    # Update Timers
    if g.offlineMode:
      if(g.scannCrono > 0):
        g.scannCrono -= (time.time() - g.lastLoopTime)

      g.lastLoopTime = time.time()
    # End of Update Timers

    # Debug Memory
    if count == 0:
      print (".", end="\r")
      count += 1
    elif count == 1:
      print ("..", end="\r")
      count += 1
    elif count == 2:
      print ("...", end="\r")
      count = 0
    # End of Debug Memory

  # End of Update() ========================================
    

# Start the event loop
if __name__ == "__main__":
  # Print starting timecode
  print(f"Golem Slag started at {time.strftime('%H:%M:%S', time.localtime())}")
  Setup()
  Update()
  print("Golem Slag closed")
