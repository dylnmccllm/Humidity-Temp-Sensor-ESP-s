# Humidity-Temp-Sensor-ESP-s

Under branches you will find 2 different mains. 
Main Sensor Contains the micropython script for the Sensor ESP32. This ESP will sense humidity and temperature (F) and send it to the MQTT Broker.
Main Receiver Contains the micropython script for the Reciever ESP32. This ESP will display information to an OLED display and Email you alerts. This wil also contain 2 libraries for the oled screen and the email.
For these to work you will have to give the ESP's a SSID and password to a 2.4GHz network, a custom mqtt broker path (to avoid data collision), and an Email account for the Alerts.
You will also need to make an email for the esp to send from with an app password for it to use. 
