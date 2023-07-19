import pygame
from bleak import BleakClient

import src.globals as g

def test_text(screen, text, pos, color, size = 12):
    font = pygame.font.Font(None, size)
    text = font.render(text, True, color)
    textpos = text.get_rect()
    textpos.centerx = pos[0]
    textpos.centery = pos[1]
    screen.blit(text, textpos)

def debugScannedDevicesColor(devices, screen):
  ypos = 0
  for i, device in enumerate(devices):
      textColor = (100, 100, 100)
      
      if "SLAG_" in device.name:
        textColor = (255, 255, 255)

      text = f"{device.name} -> {device.address}"
      test_text(screen, text, (screen.get_width()/2, 100+ypos), textColor, size =16)
      ypos += 20


def DrawDebugLayer():
    test_text(g.screen, (f"[ {g.deviceInfo} ]"), (g.screen.get_width()/2, 20), (255, 255, 255))
    test_text(g.screen, (f"IsScanning: {not g.isScanning}"), (g.screen.get_width()/2, 40), (255, 255, 255))
    # test_text(g.screen, (f"ScanCrono: {g.scannCrono}"), (g.screen.get_width()/2, 60), (255, 255, 255))
  
    # ~ if(len(g.foundDevices) > 0):
        # ~ debugScannedDevices(g.foundDevices, g.screen)
    # ~ else:
        # ~ test_text(g.screen, "No devices found", (g.screen.get_width()/2, 100), (255, 255, 255))
        
    if(len(g.foundDevicesBleak) > 0):
        debugScannedDevicesColor(g.foundDevicesBleak, g.screen)
    else:
        test_text(g.screen, "No devices found", (g.screen.get_width()/2, 100), (255, 255, 255))
