import network
import time
import machine
from machine import Pin
import ubinascii
from umqtt.robust import MQTTClient
import dht
import sys

#network configs
ssid = "SSID"
password = "Password"

#sensor configs use whatever pin you have sensor connected to.
sensor = dht.DHT11(Pin(4))


#MQTT configs
mqtt_broker="broker.hivemq.com"
client_id = b"esp32_" + ubinascii.hexlify(machine.unique_id())
temp_topic = b"wyohack/Dylan_McCollum/sensor/temperature"
humid_topic = b"wyohack/Dylan_McCollum/sensor/humidity"

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


#MQTT function
wlan = network.WLAN(network.STA_IF)
if connect_wifi(wlan, ssid, password):
    mqtt_client = None
    try:
        mqtt_client = MQTTClient(client_id, mqtt_broker, keepalive=60)
        mqtt_client.connect()
        print("Connected to MQTT Client")
        while True:
            time.sleep(5)
            sensor.measure()
            temp = sensor.temperature()
            hum = sensor.humidity()
            temp_f = temp * (9/5) +32.0
            mqtt_client.publish(temp_topic, str(temp_f))
            mqtt_client.publish(humid_topic, str(hum))
            print(f"Published Temperature: {temp_f}°F, Humidity: {hum}%")
    except OSError as e:
        print(f"MQTT/Network Error: {e}")
        print("Resetting device in 5 seconds...")
        time.sleep(5)
        machine.reset()
    except Exception as e:
        print(f"MQTT Connection Failed: {e}")
else:
    print("Cannot start MQTT client without WiFi connection.")
print("End of script.")