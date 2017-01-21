import sys
import time
import subprocess
import logging

sys.path.append("/storage/scripts/modules")
import colorutils
import homie

#####Setup logging
logging.basicConfig(level=logging.DEBUG)

####Global vars
gStatus = False
gBrightness = 0
gHue = 200
gSat = 1
gVal = 1
gColor = colorutils.Color(rgb=(0,0,0))

####Homie config
Homie = homie.Homie("homie-python.json")
statusNode = Homie.Node("status", "on")
colorNode = Homie.Node("color", "rgb,hue,sat,val")
brightnessNode = Homie.Node("brightness", "value")

def setColorOfLeds(newColor):
    global gStatus
    hex = newColor.hex
    logging.debug('Setting color to hex: ' + str(hex))
    subprocess.Popen("/storage/hyperion/bin/hyperion-remote.sh -c '" + hex + "'", stdout=subprocess.PIPE , shell=True) 
    if gColor == colorutils.Color((0,0,0)) and gStatus == True: 
        gStatus = False
        Homie.setNodeProperty(statusNode, "on", "false", True)
    elif gColor != colorutils.Color((0,0,0)) and gStatus == False:
        gStatus = True
        Homie.setNodeProperty(statusNode, "on", "true", True)

def switchOnHandler(mqttc, obj, msg):
    global gStatus
    payload = msg.payload.decode("UTF-8").lower()
    logging.debug('Setting device state to ' + payload)
    if payload == 'true' and gStatus == False:
        subprocess.Popen("/storage/hyperion/bin/hyperion-remote.sh --clearall", stdout=subprocess.PIPE, shell=True)
        Homie.setNodeProperty(statusNode, "on", "true", True)
        gStatus = True
    elif payload == 'false' and gStatus == True:
        subprocess.Popen("/storage/hyperion/bin/hyperion-remote.sh -c '#000000'", stdout=subprocess.PIPE, shell=True)
        Homie.setNodeProperty(statusNode, "on", "false", True)
        gStatus = False
		
def rgbHandler(mqttc, obj, msg):
    global gColor
    payload = msg.payload.decode("UTF-8").lower() #string 'r,g,b'
    rgb = payload.split(",")
    gColor = colorutils.Color(rgb=(int(rgb[0]),int(rgb[1]),int(rgb[2])))
    setColorOfLeds(gColor)
    Homie.setNodeProperty(colorNode, "rgb", payload, True)

def hsvColorHandler():
    global gHue
    global gSat
    global gVal
    global gColor
    gColor = colorutils.Color(hsv=(gHue,gSat,gVal))
    setColorOfLeds(gColor)

def hueHandler(mqttc, obj, msg):
    global gHue
    payload = msg.payload.decode("UTF-8") #value between 0-350
    gHue = float(payload)
    hsvColorHandler()
    Homie.setNodeProperty(colorNode, "hue", payload, True)

def satHandler(mqttc, obj, msg):
    global gSat
    payload = msg.payload.decode("UTF-8") #value between 0-100
    gSat = float(float(payload) / 100)
    hsvColorHandler()
    Homie.setNodeProperty(colorNode, "sat", payload, True)

def valHandler(mqttc, obj, msg):
    global gVal
    payload = msg.payload.decode("UTF-8") #value between 0-100
    gVal = float(float(payload) / 100)
    hsvColorHandler()
    Homie.setNodeProperty(colorNode, "val", payload, True)
	
def brightnessHandler(mqttc, obj, msg):
    payload = msg.payload.decode("UTF-8") #value between 0-100
    brightness = float(float(payload) / 100)
    logging.debug('Setting brightness to ' + str(brightness))
    subprocess.Popen("/storage/hyperion/bin/hyperion-remote.sh -m " + str(brightness), stdout=subprocess.PIPE, shell=True)
    Homie.setNodeProperty(brightnessNode, "value", payload, True)

def main():
    global gColor
    global gHue
    global gSat
    global gVal
    Homie.setFirmware("hyperion-control", "1.0.0")
    Homie.subscribe(statusNode, "on", switchOnHandler)
    Homie.subscribe(colorNode, "rgb", rgbHandler)
    Homie.subscribe(colorNode, "hue", hueHandler)
    Homie.subscribe(colorNode, "sat", satHandler)
    Homie.subscribe(colorNode, "val", valHandler)
    Homie.subscribe(brightnessNode, "value", brightnessHandler)
    Homie.setup()
    logging.debug('Homie is setup')
	
    while True:
        time.sleep(1)

if __name__ == '__main__':
    try:
        logging.info('Starting')
        main()
    except (KeyboardInterrupt, SystemExit):
        logging.info('Quiting')

