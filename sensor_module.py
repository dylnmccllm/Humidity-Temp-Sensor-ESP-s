import network
import time
import machine
from machine import Pin
import ubinascii
from umqtt.robust import MQTTClient
import adafruit_dht
import sys

#network configs
ssid = "ADD NAME OF NETWORK HERE 2.4GHz ONLY"
password = "ADD PASSWORD HERE"

#sensor configs
sensor = dht.DHT11(Pin(4))


#MQTT configs
mqtt_broker="broker.hivemq.com"
client_id = b"esp32_" + ubinascii.hexlify(machine.unique_id())
temp_topic = b"esp32/temperature"
humid_topic = b"esp32/humidity" 

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

def sens_data(data):
    sensor.measure()
    temp = sensor.temperature()
    humid = sensor.humidity()
    mqtt_client.publish(temp_topic,
                   bytes(str(temp), 'utf-8'),
                   qos-0)
    mqtt_client.publish(humid_topic,
                   bytes(str(humid), 'utf-8'),
                   qos=0)
#MQTT function
wlan = network.WLAN(network.STA_IF)
if connect_wifi(wlan, ssid, password):
    mqtt_client = None
    try:
        mqtt_client = MQTTClient(client_id, mqtt_broker)
        mqtt_client.connect()
        while True:
            timer = Timer(0)
            timer.init(period=5000, mode=Timer.PERIODIC, callback = sens_data)
    except OSError as e:
        time.sleep(5)
        machine.reset()
else:
    time.sleep(5)
    sys.exit()
    