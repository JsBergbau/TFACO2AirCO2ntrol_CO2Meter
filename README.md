# Read TFA AirCO2ntrol Mini and CO2-Meter

With this simple script you can read the CO2-Values of TFA AirCO2ntrol Mini https://www.tfa-dostmann.de/produkt/co2-monitor-airco2ntrol-mini-31-5006/ and CO2Meter https://www.co2meter.com/products/co2mini-co2-indoor-air-quality-monitor

In most cases device is recognized as /dev/hidraw0

Run the script with `sudo ./co2monitor.py /dev/hidraw0`

This script is based on https://hackaday.io/project/5301-reverse-engineering-a-low-cost-usb-co-monitor/log/17909-all-your-base-are-belong-to-us and was ported to python3

Issue once after insert `sudo chmod o+rw /dev/hidraw0` then you can simply run the script withou superuser permissions, which is prefered `./co2monitor.py /dev/hidraw0`

## Send the data of TFA AirCO2ntrol via MQTT

You can send the data of this script via MQTT with this simple commandline
`./co2monitor.py /dev/hidraw0 | grep --line-buffered -oP  "(?<=CO2:).*" | xargs -I % bash -c 'mosquitto_pub -h <IP of MQTT Server> -m % -t /CO2 ; echo %'`
