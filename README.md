# Read TFA AirCO2ntrol Mini, CO2-Meter and AIRCO2NTROL Coach CO2 Monitor

With this simple script you can read the CO2-Values of TFA AirCO2ntrol Mini https://www.tfa-dostmann.de/produkt/co2-monitor-airco2ntrol-mini-31-5006/ , CO2Meter https://www.co2meter.com/products/co2mini-co2-indoor-air-quality-monitor and AIRCO2NTROL Coach CO2 Monitor https://www.tfa-dostmann.de/produkt/co2-monitor-airco2ntrol-coach-31-5009/

In most cases device is recognized as /dev/hidraw0

Run the script with `sudo ./co2monitor.py /dev/hidraw0`

This script is based on https://hackaday.io/project/5301-reverse-engineering-a-low-cost-usb-co-monitor/log/17909-all-your-base-are-belong-to-us and was ported to python3

Issue once after insert `sudo chmod o+rw /dev/hidraw0` then you can simply run the script withou superuser permissions, which is prefered ./co2monitor.py /dev/hidraw0

## Send the data of TFA AirCO2ntrol via MQTT

You can send the data of this script via MQTT with this simple commandline. Note: if there is any connection error to the broker, 

`while true; do ./co2monitor.py /dev/hidraw0 | grep --line-buffered -oP "(?<=CO2:).*" | tee /dev/tty | mosquitto_pub -t CO2 -h <MQTT-Server> [-u username] [-P pw] -l -q 1 ; done`

If you don't need the CO2 level printed to console leave out the `tee` part, so 

`while true; do ./co2monitor.py /dev/hidraw0 | grep --line-buffered -oP "(?<=CO2:).*" | tee /dev/tty | mosquitto_pub -t CO2 -h <MQTT-Server> [-u username] [-P pw] -l -q 1 ; done`

Be sure to have -q 1. Without if you do a restart of mosquitto mosquitto_pub won't notice that connection is closed and seems still sending data but no data is actually transmitted. 

You can also use it with QOS 0 and xargs. However that is less efficient as mosquitto_pub is executed on every new value and has to establish a new connection on each value ./co2monitor.py /dev/hidraw0 | grep --line-buffered -oP "(?<=CO2:).*" | xargs -I % bash -c 'mosquitto_pub -h <IP of MQTT Server> -m % -t /CO2 ; echo %'
