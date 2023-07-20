import time
import os
import threading
import pygame

from src.bt_client import *
from src.bt_server import *
from src.graphics import *
from src.debug_display import *
# from src.serial_send import *

def Setup():
  import src.globals as g

  g.initGlobals()

  # Initialize Pygame
  print("PYGAME INIT")
  os.environ["DISPLAY"] = ":0"
  pygame.init()
  # g.screen = pygame.display.set_mode((480,480),pygame.FULLSCREEN)
  g.screen = pygame.display.set_mode((480,480),pygame.RESIZABLE)
  pygame.display.set_caption("Golem: Display Node")
  pygame.mouse.set_visible(False)
  g.setupPygame = True

  # Initialize BLEAK Client
  # if not g.offlineMode:
  #   setupBTAdapter()
  
  # Initialize BLESS Server
  # if not g.offlineMode:
  #   if not g.serverLessMode:
  #     loop = asyncio.get_event_loop()
  #     loop.run_until_complete(initServerAsync(loop))
  
  
# End of Setup() ========================================


def Update():
  import src.globals as g
  
  # Start Bluetooth device scanning thread (online mode)
  # if not g.offlineMode:
  #   scan_thread = threading.Thread(target=bleakLoopThread, daemon=False)
  #   # daemon is false so the thread has to be killed manualy before closing main thread
  #   scan_thread.start()
  # End of Start Bluetooth device scanning thread (online mode)

  # Update Loop
  while True:
    
    #Handle Bluetooth device scanning (offline mode)
    # if g.offlineMode:
    #    #turn state of g.isScanning each 10 seconds
    #   if g.scannCrono <= 0:
    #     if g.isScanning:
    #       g.shuffleOfflineList()
    #       g.isScanning = False
    #       g.scannCrono = 5
    #     else:
    #       g.isScanning = True
    #       g.scannCrono = 10
    # End of Bluetooth device scanning (offline mode)
       
    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Quit the application if the X button is pressed
            pygame.quit()
            g.killBleak = True
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Quit if the 'esc' key is pressed
                pygame.quit()
                g.killBleak = True
                quit()
    # End of Handle Pygame events

    # Draw graphics on the screen
    DrawLoop()
    pygame.display.update()
    # end of Draw graphics on the screen

    # Update Timers
    if g.offlineMode:
      if(g.scannCrono > 0):
        g.scannCrono -= (time.time() - g.lastLoopTime)

      g.lastLoopTime = time.time()

      
    # End of Update Timers

  # End of Update() ========================================
    

# Start the event loop
if __name__ == "__main__":
  Setup()
  Update()
