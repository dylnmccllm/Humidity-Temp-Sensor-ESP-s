import network
import time
import machine
import ubinascii
from umqtt.robust import MQTTClient

#network configs
ssid = "ADD NAME OF NETWORK HERE 2.4GHz ONLY"
password = "ADD PASSWORD HERE"

#prints will be changed to light indicators but is used as print for testing
#WiFi connection function
def connect_wifi(sta_if, ssid, password):
    print(f"connecting to WiFi network: {ssid}...")
    if not sta_if.isconnected():
        sta_if.active(True)
        sta_if.connect(ssid, password)
        max_wait = 15
        while not sta_if.isconnected() and max_wait > 0:
            print(".", end="")
            time.sleep(1)
            max_wait -= 1
        print()
    if sta_if.isconnected():
        print("WiFi Connection Successful!")
        return True
    else:
        print("WiFi Connection Failed!")
        return False