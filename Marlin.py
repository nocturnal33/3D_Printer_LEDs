#!/usr/bin/python3
#######################
### Library imports ###
#######################
import requests
import time
import board
import neopixel
import signal
import sys
from setproctitle import setproctitle
setproctitle("neopixel_script")

#####################
### Printer Temps ###
#####################
temp_low = 11.0
temp_on = 100.0
temp_too_high = 295.0
target_temp = None
tempState = None
printerOn = None

######################
### Filament Temps ###
######################
temp_PLA_LOW = 140.0
temp_PLA_HIGH = 215.0
temp_PETG_LOW = 215.1
temp_PETG_HIGH = 240.0
temp_ABS_LOW = 245.0
temp_ABS_HIGH = 290.0

##########################
### NeoPixel Variables ###
##########################
pixel_pin = board.D21
ORDER = neopixel.GRB
pixels_strip1 = 16
pixels_strip2 = 2

##############
### Colors ###
##############
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255,165,0)
OFF = (0, 0, 0)
WHITE = (255, 255, 255)

##############################
### Define NeoPixel Strips ###
##############################
neo_strip1 = neopixel.NeoPixel(
pixel_pin, 
pixels_strip1, 
brightness=0.5,
auto_write=False,
pixel_order=ORDER
)

neo_strip2 = neopixel.NeoPixel(
pixel_pin,
pixels_strip2,
brightness=0.5, 
auto_write=False,
pixel_order=ORDER
)

#################
### Functions ###
#################

# turn off pixels
def turn_off_pixel_strip1():
    neo_strip1.fill(OFF)
    neo_strip1.show()

def turn_off_pixel_strip2():
    neo_strip2.fill(OFF)
    neo_strip2.show()

def signal_handler(sig, frame):
    print('Turning off pixels and exiting...')
    turn_off_pixel_strip1()
    turn_off_pixel_strip2()
    sys.exit(0)

# Octoprint Connection
def connection():
    API_KEY='' # Add API Key from Octoprint
    OCTOPRINT_IP= '' # Add Octoprint IP Address
    headers = {
        'X-Api-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    url = f"http://{OCTOPRINT_IP}/api/printer"
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to get data: {response.status_code}")

def printerActualTemp():
    actual_temp = connection()['temperature']['tool0']['actual']
    print(f"Extruder Actual Temperature: {actual_temp}°C")
    return actual_temp

def printerReadyStatus():
    printingStatus = connection()['state']['flags']['status']['printing']
    return printingStatus
    
def printerPauseStatus():
    printerPaused = connection()['state']['flags']['paused']
    return printerPaused

def printerIsPrinting():
    isPrinting = connection()['state']['flags']['status']['printing']
    return isPrinting

def led_set_pixels_color(start, end, color):
    for i in range(start, end):
        neo_strip1[i] = color

def led_alert(color1, color2, color3, delay1=0.02, delay2=0.1):
    neo_strip2[0] = color1
    neo_strip2.show()
    time.sleep(delay1)
    neo_strip2[0] = color3
    neo_strip2.show()
    time.sleep(delay2)
    neo_strip2[1] = color2
    neo_strip2.show()
    time.sleep(delay1)
    neo_strip2[1] = color3
    neo_strip2.show()
    time.sleep(delay2)

def led_chasing_effect(start, end, color, delay=0.05):
    for i in range(start, end):
        # Turn on the current LED
        neo_strip1[i] = color
        neo_strip1.show()
        time.sleep(delay)

        # Turn off the LED that was just lit, unless it's the first one
        if i != start:
            neo_strip1[i - 1] = OFF
            neo_strip1.show()

    # Turn off the last LED in the segment
    neo_strip1[end - 1] = OFF
    neo_strip1.show()

def led_chasing_effect_reversed(start, end, color, delay=0.05):
    for i in reversed(range(start, end)):
        neo_strip1[i] = color
        neo_strip1.show()
        time.sleep(delay)

        # In reverse order, turn off the next LED in the sequence
        if i != end - 1:
            neo_strip1[i + 1] = OFF

    # After the loop, make sure to turn off the LED at the 'start' position
    neo_strip1[start] = OFF
    neo_strip1.show()

def led_chasing_up_and_down(start, end, color, delay=0.05):
    # Chasing up
    led_chasing_effect(start, end, color, delay)

    # Chasing down
    led_chasing_effect_reversed(start, end, color, delay)
    
def temp_trend(current_temp, delay=0.5):
    global tempState
    if tempState is None:
        trend = "false"
        time.sleep(delay)
        return trend
    elif current_temp > tempState:
        trend = "UP"
        time.sleep(delay)
        return trend
    elif current_temp < tempState:
        trend = "DOWN"
        time.sleep(delay)
        return trend
    else:
        trend = "true"
        time.sleep(delay)
        return trend

############################
### Gracefully shut down ###
############################
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# convert json Data to float    
actualTemp = float(printerActualTemp())
print("converting to a float")
if connection():
    printerOn = True
else:
    printerOn = False


while printerOn:
    # Low Temp
    printerActualTemp()
    actualTemp = float(printerActualTemp())
    
    if actualTemp > temp_low and actualTemp < temp_on:
        print("eval 1")
        led_chasing_effect(0, 4, BLUE)
    
    # PLA Temps
    elif actualTemp > temp_PLA_LOW and actualTemp < temp_PLA_HIGH:
        print("eval 2")
        led_chasing_effect(0, 8, ORANGE)

    # PETG Temps
    elif actualTemp > temp_PETG_LOW and actualTemp < temp_PETG_HIGH:
        print("eval 3")
        led_chasing_effect(0, 12, GREEN)

    # ABS Temps
    elif actualTemp > temp_ABS_LOW and actualTemp < temp_ABS_HIGH:
        print("eval 4")
        led_chasing_effect(0, 16, RED)
    
    else:
        print("eval else")
        turn_off_pixel_strip1()
    
    
        
    
    # Printer Pause Status    
    if printerPauseStatus() == "true" and printerIsPrinting() == 'true':
        print("eval 2.1")
        led_alert(GREEN, ORANGE, OFF, 2, 1)
    else:
        print("eval else.1")
        turn_off_pixel_strip2()
    
    if temp_trend(actualTemp) == "UP" and actualTemp < temp_PLA_LOW and printerReadyStatus() == "true":
        print("eval 3.1")
        led_chasing_effect(0, 16, RED)
        
    elif temp_trend(actualTemp) == "DOWN" and actualTemp > temp_low and printerReadyStatus() == "false":
        print("eval 3.2")
        led_chasing_effect_reversed(0, 16, BLUE)

    elif temp_trend(actualTemp) == "true" and actualTemp > temp_PLA_LOW and printerReadyStatus() == "true":
        print("eval 3.3")
        led_chasing_up_and_down(0, 16, WHITE)
    else:
        print("eval else-3")
    
    
else:
    print("Failed to retrieve temperature.")

neo_strip1.show()
time.sleep(0.05)  # Delay to prevent continuous polling
