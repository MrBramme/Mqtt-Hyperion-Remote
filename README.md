# Mqtt-Hyperion-Remote
An MQTT approach to the remote of Hyperion for the Openelec distribution. My main objective was to integrate Home-Assistant and have topics to handle HSV colors as well (homebridge for IOS).
As I'm a big fan of the [Homie convention](https://github.com/marvinroger/homie) I'm using the Homie-python module.

## Assumption
- you have a dedicated raspberry pi running Openelec: [Openelec site](http://openelec.tv/get-openelec)
- This raspberry pi also runs your Hyperion ambilight system: [Hyperion project](https://hyperion-project.org)
- You have an instance of Home-Assistant active: [Home assistant](https://home-assistant.io)
- You have an MQTT broker active
- (Optional) You have a Homebridge instance active for Homekit integration: [Homebridge](https://github.com/nfarina/homebridge)

## Installing
1. Setup the python scripts on your openelec system
  1. SSH into your openelec instance
  2. Setup a scripts folder
  ```bash
  mkdir scripts
  cd scripts
  ```
  3. Place the files mqttHyperion.py and homie-python.json in there as well as the modules folder.
  4. Next, it's time to add your MQTT config
  ```bash
  nano homie-python.json
  ```
  5. Start the script and your client will be set up! For a first run, I advice using the command 'python mqttHyperion.py' and keeping that terminal window open. Once you're satisfied, run the script in the background using 'nohup python mqttHyperion.py &'

2. Setup the Home assistant config. This should go into the lights section.

```json
- platform: mqtt
  name: "Ambilight"
  command_topic: "home/kodi/openelec/status/on/set"
  state_topic: "home/kodi/openelec/status/on"
  rgb_state_topic: "home/kodi/openelec/color/rgb"
  rgb_command_topic: "home/kodi/openelec/color/rgb/set"
  brightness_state_topic: "home/kodi/openelec/brightness/value"
  brightness_command_topic: "home/kodi/openelec/brightness/value/set"
  payload_on: "true"
  payload_off: "false"
  brightness_scale: 100
  optimistic: false
```
Turning on the 'light' will start hyperion with it's screen grabber. Setting a color will ... set a color :) and brightness will change the brightness globally (both for colors and screen grabbing).
To reset from color to screen grabbing, toggle off and on.

3. Setup the homebridge end of things:

Warning: Since I don't want to reduce global brightness when setting a color, we will create 2 controls for homebridge! One for color and one for global brightness.
  1. Add this plugin to homebridge: [mqttlightbulb](https://github.com/ameeuw/homebridge-mqttlightbulb)
  2. Set the config as follows

  ```json
  {
          "accessory": "mqttlightbulb",
          "name": "AmbiLightColor",
          "url": "mqtt://<insert IP here>",
          "username": "username",
          "password": "password",
          "caption": "AmbiLight Color",
          "payloadisjson": "false",
          "topics": {
                "getOn":                "home/kodi/openelec/status/on",
                "setOn":                "home/kodi/openelec/status/on/set",
                "getBrightness":        "home/kodi/openelec/color/val",
                "setBrightness":        "home/kodi/openelec/color/val/set",
                "getHue":               "home/kodi/openelec/color/hue",
                "setHue":               "home/kodi/openelec/color/hue/set",
                "getSaturation":        "home/kodi/openelec/color/sat",
                "setSaturation":        "home/kodi/openelec/color/sat/set"
          }
  }
  ```

  After this you'll have 2 buttons on homekit:
  - The one from Home-assistant (if you have the homebridge plugin) that can be used to turn on/off and set global brightness
  - The one we just set up which can be used to set the color of the system and turn it on/off.

  And on Home-assistant you'll be able to set a color as well, and turn on/off and set global brightness.
