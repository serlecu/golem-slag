import grove
from grove.i2c import Bus
from grove.motor import I2CStepperMotor

import RPi.GPIO as GPIO
import time

import src.globals as g


driver : I2CStepperMotor
loadArgs = {
    'var-ratio' : 200,
    'stride-angle': 1.8,
    'rpm-max': 10,
    'sequences': []
        #CW
        #[0b0001, 0b0101, 0b0100, 0b0110, 0b0010, 0b1010, 0b1000, 0b1001]
        #CCW
        #[0b1001, 0b1000, 0b1100, 0b0100, 0b0110, 0b0010, 0b0011, 0b0001]
        }
stepCount: int = 0


def initRail():
    global driver
    print("RAIL: Init")
    
    # Setup End-Switches
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(26, GPIO.IN)
    
    # Setup i2C-driver
    driver = I2CStepperMotor(loadArgs)
    driver.set_speed(0,0)
    driver._rotate(0)
    stepRun(0,0,1)
    driver.enable(True)
    
    #Move Rail to left
    #moveToOrigin()
    
    print("RAIL: init end.")
    time.sleep(1)
    
    
def railTest():
    # ~ stepsTotal = 0
    lastEndSwitch = False
    direction = True
    
    while (1):
        # Handle EndSwitches -> direction
        if readEndSwitch() and not lastEndSwitch:
            direction = not direction
            lastEndSwitch = True
            print("END SWITCH !!")
        elif not readEndSwitch() and lastEndSwitch:
            lastEndSwitch = False
            print("released endSwitch")
        
        print(f"Direction: {direction}")
        # Perform Step
        stepRun(60, direction, 0.5)
        

def railControl():
    
    # Wait for al setups to start running
    while (not g.setupBleak) or (not g.setupBless) or (not g.setupPygame):
        time.sleep(0.2) 
        
    while not g.i2cConnected:
        try:
            initRail()
        except Exception as e:
            print(e)
            time.sleep(2)
        else:
            g.i2cConnected = True
            
    while not g.killRail:
        if g.i2cConnected:
            try:
                if (g.syncState): #! Warning -> endSwitches
                    moveToOrigin()
                    syncState = False
                    continue
                # Handle EndSwitches -> direction
                handleEndSwitch()
                # Perform Step
                stepRun(g.railSpeed, g.railDirection, g.railDelay)
            except Exception as e:
                print(e)
                g.i2cConnected = False
        else:
            try:
                # Setup End-Switches
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(26, GPIO.IN)
                
                # Setup i2C-driver
                driver = I2CStepperMotor(loadArgs)
                driver.set_speed(0,0)
                driver._rotate(0)
                stepRun(0,0,1)
                driver.enable(True)
            except Exception as e:
                print(e)
                time.sleep(2)
            else:
                g.i2cConnected = True
                
                
def moveToOrigin():
    onOrigin = False
    
    while not onOrigin:
        if readEndSwitch():
            onOrigin = True
        else:
         stepRun(50, False, 0.01)
    steps = 10
    while steps > 0:
        stepRun(50, True, 0.01)
        steps -= 1
         
    print("RAIL: position set to origin.")
    
    

def handleEndSwitch():
    
    if readEndSwitch() and not g.lastEndSwitch:
        g.railDirection = not g.railDirection
        g.endSwitchCounter += 1
        g.lastEndSwitch = True
        print("RAIL: change direction !!")
    elif not readEndSwitch() and g.lastEndSwitch:
        g.lastEndSwitch = False
     
        
def readEndSwitch():
    input_state: bool = GPIO.input(26)
    return input_state
    
    
def stepRun(speed, direction, sleep) :
    # speed int [50-255]
    # direction in [0-1]
    # sleep float seconds
    
    global stepCount
    
    # Set motor force
    driver.set_speed(speed, speed)
    
    # Activate correct motor conmbination for step
    if stepCount == 0:
        driver.set_dir(True, True)
    elif stepCount == 1:
        driver.set_dir(True, False)
    elif stepCount == 2:
        driver.set_dir(False,False)
    elif stepCount == 3:
        driver.set_dir(False,True)
    else:
        print("Error on dir counter")
    
    # Deactivate motor (reduce heat)
    driver.set_speed(0, 0)
    
    # Increas/Decrease counter
    if direction == True: #CW
        stepCount += 1
    else:  #CCW
        stepCount -= 1
        
    # Manage bounds
    if stepCount > 3:
        stepCount = 0
    elif stepCount < 0:
        stepCount = 3
    
    # Delay as speed controll
    time.sleep(sleep)
    
# ~ initRail()
# ~ railControl()
