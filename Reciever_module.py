import network
import time
import machine
import ssd1306
from machine import Pin, SoftI2C
import ubinascii
from umqtt.robust import MQTTClient
import sys
import umail

#enter WiFi credentials here
ssid = "SSID"
password = "PASS"

# Email details
sender_email = 'esp_email'
sender_name = 'ESP32 Alert System'
sender_app_password = 'App_password_esp32' 
recipient_email = 'email you want alerts sent to'

# ESP32 Pin assignment 
i2c = SoftI2C(scl=Pin(5), sda=Pin(4))

# screen dimensions
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# MQTT configuration
mqtt_broker="broker.hivemq.com"
client_id = b"esp32_" + ubinascii.hexlify(machine.unique_id())
temp_topic = b"wyohack/Dylan_McCollum/sensor/temperature"
humid_topic = b"wyohack/Dylan_McCollum/sensor/humidity"

# global variable initialization
humid = 0
temp = 0
last_temp_alert_time = 0
last_humid_alert_time = 0
ALERT_COOLDOWN = 600  # 10 minutes between alerts
MQTT_CHECK_MS = 10000
last_mqtt_check = time.ticks_ms()
blink_state = True
last_message_time = time.time()
MESSAGE_TIMEOUT = 8  # 8 seconds without message triggers reconnect
received_data_temp = False
received_data_humid = False


#WiFi connection function
def connect_wifi(sta_if, ssid, password):
    print(f"connecting to WiFi network: {ssid}...")
    if sta_if.isconnected():
        sta_if.disconnect()
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
    global humid, temp, last_message_time, received_data_temp, received_data_humid
    print("MQTT received:", topic.decode(), msg.decode())
    last_message_time = time.time()
    if topic == temp_topic:
        temp = float(msg.decode())
        received_data_temp = True
    elif topic == humid_topic:
        humid = float(msg.decode())
        received_data_humid = True

# reconnects MQTT client on timeout
def reconnect_mqtt(client):
    try:
        client.disconnect()
    except Exception:
        pass
    client = MQTTClient(client_id, mqtt_broker, keepalive=10)
    client.set_callback(mqtt_callback)
    client.connect()
    client.subscribe(temp_topic)
    client.subscribe(humid_topic)
    print("MQTT reconnected")
    return client

# disconnects MQTT client and WiFi interface on exit
def cleanup(mqtt_client, wlan):
    if mqtt_client is not None:
        try:
            mqtt_client.disconnect()
            print("MQTT disconnected")
        except Exception as e:
            print("MQTT disconnect failed:", e)

    if wlan is not None:
        if wlan.isconnected():
            wlan.disconnect()
            print("WiFi disconnected")
        wlan.active(False)
        print("WiFi interface deactivated")

        
#MQTT connection and main loop
wlan = network.WLAN(network.STA_IF)
if connect_wifi(wlan, ssid, password):
    mqtt_client = None
    try:
        mqtt_client = MQTTClient(client_id, mqtt_broker, keepalive=60)
        mqtt_client.set_callback(mqtt_callback)
        mqtt_client.connect()
        mqtt_client.subscribe(temp_topic)
        mqtt_client.subscribe(humid_topic)
        smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True) # Gmail's SSL port
        smtp.login(sender_email, sender_app_password)
        while True:
            try:
                mqtt_client.check_msg()
            except OSError as e:
                print("MQTT connection lost, reconnecting:", e)
                mqtt_client = reconnect_mqtt(mqtt_client)
            
            current_time = time.time()
            if current_time - last_message_time > MESSAGE_TIMEOUT:
                print("No messages received for", MESSAGE_TIMEOUT, "seconds, reconnecting MQTT")
                mqtt_client = reconnect_mqtt(mqtt_client)
                last_message_time = current_time
            
            print(f"Temp: {temp}F, Humidity: {humid}%")
            oled.fill(0)
            oled.text('Humidity: ' + str(humid) + '%', 0, 0)
            oled.text('Temp: ' + str(temp) + 'F', 0, 10)
            oled.text('*' if blink_state else ' ', 120, 0)
            oled.show()
            blink_state = not blink_state
# feel free to adjust thresholds for environent
            if received_data_temp and received_data_humid:
                if 63 > temp:
                    if current_time - last_temp_alert_time > ALERT_COOLDOWN:
                        smtp.to(recipient_email)
                        smtp.write("From:" + sender_name + "<" + sender_email + ">\n")
                        smtp.write("Subject: Temperature Alert!\n")
                        smtp.write("Temperature is out of range: " + str(temp) + "F\n")
                        smtp.send()
                        print("Temperature alert email sent!")
                        last_temp_alert_time = current_time
                elif 83 < temp:
                    if current_time - last_temp_alert_time > ALERT_COOLDOWN:
                        smtp.to(recipient_email)
                        smtp.write("From:" + sender_name + "<" + sender_email + ">\n")
                        smtp.write("Subject: Temperature Alert!\n")
                        smtp.write("Temperature is out of range: " + str(temp) + "F\n")
                        smtp.send()
                        print("Temperature alert email sent!")
                        last_temp_alert_time = current_time
                if 40 > humid:
                    if current_time - last_humid_alert_time > ALERT_COOLDOWN:
                        smtp.to(recipient_email)
                        smtp.write("From:" + sender_name + "<" + sender_email + ">\n")
                        smtp.write("Subject: Humidity Alert!\n")
                        smtp.write("\n")
                        smtp.write("Humidity is out of range: " + str(humid) + "%\n")
                        smtp.send()
                        print("Humidity alert email sent!")
                        last_humid_alert_time = current_time
                elif 60 < humid:
                    if current_time - last_humid_alert_time > ALERT_COOLDOWN:
                        smtp.to(recipient_email)
                        smtp.write("From:" + sender_name + "<" + sender_email + ">\n")
                        smtp.write("Subject: Humidity Alert!\n")
                        smtp.write("\n")
                        smtp.write("Humidity is out of range: " + str(humid) + "%\n")
                        smtp.send()
                        print("Humidity alert email sent!")
                        last_humid_alert_time = current_time
            time.sleep(1)
    except OSError as e:
        print(f"MQTT/Network Error: {e}")
        print("Resetting in 5 seconds...")
        time.sleep(5)
        machine.reset()
    except Exception as e:
        print(f"MQTT Connection Failed: {e}")
        time.sleep(5)
    finally:
        oled.fill(0)
        oled.show()
        smtp.quit()
        cleanup(mqtt_client, wlan)

        
else:
    print("Cannot start MQTT client without WiFi connection.")
print("Script finished.")


