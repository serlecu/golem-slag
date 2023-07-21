import pygame
from pygame import gfxdraw
import math
import os
import random

import src.globals as g # global variables

clock = pygame.time.Clock()
deltaTime = 0.0
radarAngle = 0.0

def setupPygame():
    print("PYGAME INIT")
    os.environ["DISPLAY"] = ":0"
    pygame.init()

    g.screen = pygame.display.set_mode((480,480),pygame.FULLSCREEN)
    pygame.display.set_caption("Golem: Display Node")
    pygame.mouse.set_visible(False)
    g.setupPygame = True

def draw_background(screen, color):
    screen.fill(color)

# testing animation
def test_ellipse(screen, color, radius, angle):
    centerX = (int)(screen.get_width()/2)
    centerY = (int)(screen.get_height()/2)
    gfxdraw.aaellipse(screen, centerX, centerY, radius, radius, color)
    gfxdraw.line(screen, centerX, centerY, centerX+(int)(radius*math.cos(angle)), centerY+(int)(radius*math.sin(angle)), (200,200,200))

# testing text
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

        if type(device) is str:
          textColor = (255, 255, 255)
          text = device
          test_text(screen, text, (screen.get_width()/2, 100+ypos), textColor, size =16)
        else:
          if "SLAG_" in device.name:
            textColor = (255, 255, 255)

          text = f"{device.name} -> {device.address}"
          test_text(screen, text, (screen.get_width()/2, 100+ypos), textColor, size =16)
        ypos += 20

    if len(devices) > 15:
      textColor = (100, 100, 100)
      text = "..."
      test_text(screen, text, (screen.get_width()/2, 100+ypos), textColor, size =16)

def debugScannedDevicesOffline(deviceList:list, screen):
    ypos = 0
    countSLAG = 0
    countAll = 0
    for device in deviceList:
        textColor = (100, 100, 100)
        text = ''

        if "SLAG_" in device:
          textColor = (255, 255, 255)
          text = device
          countSLAG += 1
          countAll += 1
        else:
          text = f"{device} -> {device}"
          countAll += 1

        test_text(screen, text, (screen.get_width()/2, 100+ypos), textColor, size =16)
        ypos += 20
        if countSLAG > 2 and countAll >= g.offlineListLen:
            break

def DrawLoop():
    global deltaTime
    global radarAngle

    radarAngle += deltaTime % 360
    draw_background(g.screen, (0, 0, 0))
    test_ellipse(g.screen, (200, 200, 200, 100), 200, radarAngle)

    test_text(g.screen, (f"IsScanning: {g.isScanning}"), (g.screen.get_width()/2, 40), (255, 255, 255))

    if not g.offlineMode:
      if not g.writeDevices:
        if(len(g.foundDevicesBleak) > 0):
            debugScannedDevicesColor(g.foundDevicesBleak, g.screen)
        else:
            test_text(g.screen, "No devices found", (g.screen.get_width()/2, 100), (255, 255, 255))
    else:
        debugScannedDevicesOffline(g.offlineMacList, g.screen)


def DisplayUpdate():
    global deltaTime
    
    pygame.display.update()
    deltaTime = clock.tick(60) / 1000.0