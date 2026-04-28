import network
import time
import machine
from machine import Pin
import ubinascii
from umqtt.robust import MQTTClient
import sys

ssid = "SSID"
password = "Password"

mqtt_broker="broker.hivemq.com"
client_id = b"esp32_" + ubinascii.hexlify(machine.unique_id())
temp_topic = b"wyohack/Dylan_McCollum/sensor/temperature"
humid_topic = b"wyohack/Dylan_McCollum/sensor/humidity"

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