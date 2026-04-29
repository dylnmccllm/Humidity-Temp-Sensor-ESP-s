import network
import time
import machine
import ssd1306
from machine import Pin, SoftI2C
import ubinascii
from umqtt.robust import MQTTClient
import sys

ssid = "SSID"
password = "Password"

# ESP32 Pin assignment 
i2c = SoftI2C(scl=Pin(5), sda=Pin(4))

# screen dimensions
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

mqtt_broker="broker.hivemq.com"
client_id = b"esp32_" + ubinascii.hexlify(machine.unique_id())
temp_topic = b"wyohack/Dylan_McCollum/sensor/temperature"
humid_topic = b"wyohack/Dylan_McCollum/sensor/humidity"

humid = 0
temp = 0


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
    
#MQTT callback to update temp and humidity values
def mqtt_callback(topic, msg):
    global humid, temp
    if topic == temp_topic:
        temp = float(msg.decode())
    elif topic == humid_topic:
        humid = float(msg.decode())
        
#MQTT connection and main loop
wlan = network.WLAN(network.STA_IF)
if connect_wifi(wlan, ssid, password):
    mqtt_client = None
    try:
        mqtt_client = MQTTClient(client_id, mqtt_broker, keepalive = 60)
        mqtt_client.set_callback(mqtt_callback)
        mqtt_client.connect()
        mqtt_client.subscribe(temp_topic)
        mqtt_client.subscribe(humid_topic)
        print("Connected to MQTT Client")
        while True:
            time.sleep(5)
            mqtt_client.check_msg()
            print("message received")
            oled.fill(0)
            oled.text('Humidity: ' + str(humid) + '%', 0, 0)
            oled.text('Temperature: ' + str(temp) + 'F', 0, 10)
            oled.show()
    except OSError as e:
        print(f"MQTT/Network Error: {e}")
        print("Resetting in 5 seconds...")
        time.sleep(5)
        machine.reset()
    except Exception as e:
        print(f"MQTT Connection Failed: {e}")
else:
    print("Cannot start MQTT client without WiFi connection.")
print("Script finished.")