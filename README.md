# Humidity-Temp-Sensor-ESP-s

Under branches you will find 2 different mains. 
Main Sensor Contains the micropython script for the Sensor ESP32. This ESP will sense humidity and temperature (F) and send it to the MQTT Broker.
Main Receiver Contains the micropython script for the Reciever ESP32. This ESP will display information to an OLED display and Email you alerts.
For these to work you will have to give the ESP's a SSID and password to a 2.4GHz network, a custom mqtt broker path (to avoid data collision), and an Email account for the Alerts.

##CURRENT STATUS##
The ESP's can talk to eachother through mqtt and transmit the data, circuit diagrams need to be added, cleanup needs added to both scripts, and email needs added to the receiver script.
