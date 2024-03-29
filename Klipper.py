#!/usr/bin/python3
import requests
import time
import board
import neopixel
import signal
import sys
from setproctitle import setproctitle

## Set a process name for the script
setproctitle("neopixel_script")

###############
#### BOARD ####
###############
pixel_pin = board.D21

#################
#### PRINTER ####
#################
printer_ip = ''

####################
#### LEDS STRIP ####
####################
ORDER = neopixel.GRB
total_pixels = 9 # Total number of LEDs
bright1 = 0.6
bright2 = 0.6
pixels_low = 2
pixels_high = 9

pixels = neopixel.NeoPixel(pixel_pin, total_pixels, brightness=bright1, 
         auto_write=False, pixel_order=ORDER)
         
pixel1 = neopixel.NeoPixel(pixel_pin, pixels_low, brightness=bright2, 
         auto_write=False, pixel_order=ORDER)

################
#### COLORS ####
################
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
OFF = (0, 0, 0)
WHITE = (255,255,255)
PURPLE = (128,0,128)
CYAN = (0,255,255)

###################
#### TEMP VARS ####
###################
TEMP_LOW = 13
TEMP_ON = 100

PLA_LOW = 170
PLA_HIGH = 215

PETG_LOW = 215
PETG_HIGH = 255

ABS_LOW = 255
ABS_HIGH = 295

###################
#### FUNCTIONS ####
###################
# Turn off stip 1
def turn_off_pixels():
    pixels.fill(OFF)
    pixels.show()

# Turn off strip 2
def turn_off_pixels1():
    pixel1.fill(OFF)
    pixel1.show()

# Quit script gracefully and turn off LEDs
def signal_handler(sig, frame):
    print('Turning off pixels and exiting...')
    turn_off_pixels()
    turn_off_pixels1()
    sys.exit(0)

# Get the printer temps
def get_extruder_temperature(printer_ip, printer_port="80"):
    url = f"http://{printer_ip}:{printer_port}/printer/objects/query?extruder"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['result']['status']['extruder']['temperature']
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None

# Registering signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Low Temp Stay on
def lowTempStayOn(color1):
    for i in range (start, end):
        pixel1[i] = color1
        pixel1[i].show()

# Low Temp Blink
def lowtemp(color1, color2, color3=OFF, delay1=0.3, delay2=0.5):
    pixel1[0] = color1
    pixel1.show()
    time.sleep(delay1)
    pixel1[0] = color3
    pixel1.show()
    time.sleep(delay2)
    pixel1[1] = color2
    pixel1.show()
    time.sleep(delay1)
    pixel1[1] = color3
    pixel1.show()
    time.sleep(delay2)

Strip1 - Stay On
def stayOn(color, start, end):
    for i in range (end):
        pixels[i] = color
        pixels.show()

# Chase UP
def chasing_effect(start, end, color, delay=0.05):
    for i in range(start, end):
        # Turn on the current LED
        pixels[i] = color
        pixels.show()
        time.sleep(delay)

        # Turn off the LED that was just lit, unless it's the first one
        if i != start:
            pixels[i - 1] = OFF
        pixels.show()

    # Turn off the last LED in the segment
    pixels[end - 1] = OFF
    pixels.show()

# Chase Down
def chasing_effect_reversed(start, end, color, delay=0.05):
    for i in reversed(range(start, end)):
        pixels[i] = color
        pixels.show()
        time.sleep(delay)

        # In reverse order, turn off the next LED in the sequence
        if i != end - 1:
            pixels[i + 1] = OFF

    # After the loop, make sure to turn off the LED at the 'start' position
    pixels[start] = OFF
    pixels.show()


# Chase Up and Down
def chasing_up_and_down(start, end, color, delay=0.05):
    # Chasing up
    chasing_effect(start, end, color, delay)
    # Chasing Down
    chasing_effect_reversed(start, end, color, delay)

# Connections
def connection(printer_ip, printer_port="80"):
    url = f"http://{printer_ip}:{printer_port}/printer/objects/query?extruder"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data:
            return True
        else:
            return False
    except requests.RequestException as e:
        print(f"Error: {e}")
        return False

# Rainbow Effects
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)

# Cycle through the Wheel of colors
def rainbow_cycle(wait):
    for j in range(255):
        for i in range(total_pixels):
            pixel_index = (i * 256 // total_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)

# Loop logic
con = connection(printer_ip)


while con:
    temperature = get_extruder_temperature(printer_ip)
    if temperature is not None:
        et = float(temperature)
        print("Temperature is " + str(et))

        if et > TEMP_LOW and  et < TEMP_ON:
            #chasing_effect(0, 2, BLUE)
            rainbow_cycle(0.01)
        ## PLA ##
        elif et > TEMP_ON and  et < PLA_LOW:
            chasing_effect(3, 5, GREEN)
            
        elif et > PLA_LOW and  et <= PLA_HIGH:
            chasing_up_and_down(0, 8, GREEN, 0.05)
       
        ## PETG ##
        elif et > PLA_HIGH and et < PETG_LOW:
            chasing_effect(6, 8, CYAN)

        elif et > PETG_LOW and et < PETG_HIGH:
            chasing_up_and_down(0, 8, CYAN, 0.05)
        
        ## ABS ##
        elif et > PETG_HIGH and et < ABS_LOW:
            chasing_effect(6, 8, RED)

        elif et > ABS_LOW and et < ABS_HIGH:
            chasing_up_and_down(0, 8, RED, 0.05)
        else:
            turn_off_pixels()

        if et < TEMP_LOW:
            lowtemp(BLUE, RED)
        else:
            turn_off_pixels1()
    else:
        print("Failed to retrieve temperature.")
        pixel1[0] = WHITE
        time.sleep(1)
        pixel1.show()
        pixel1[0] = OFF
        time.sleep(1)
        

while con == False:
    chasing_effect(0, 8, PURPLE, delay=.5)
    turn_off_pixels1()
    turn_off_pixels()
    time.sleep(2)
    stayOn(WHITE, 0, 8)
    time.sleep(5)
    turn_off_pixels1()
    turn_off_pixels()
    
    
pixels.show()
time.sleep(0.05)  # Delay to prevent continuous polling
