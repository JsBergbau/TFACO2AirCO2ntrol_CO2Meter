#! /usr/bin/python3
'''
You need to install phao-mqtt-module -> https://pypi.org/project/paho-mqtt/
Set your username and password in ./module/secrets.py 
Change other variables to your liking/env
You can add other sensor output if you want, see values part in this script and the actuall ranges on co2_monitor.py in the github repo
'''
import paho.mqtt.client as mqtt 
import time
from module import secrets
import sys, fcntl, time

mqttBroker ="mosquitfoo.example.com" 
client = mqtt.Client("raspi-desk")
client.username_pw_set(username = secrets.username, password = secrets.password)
client.tls_set(ca_certs='/etc/ssl/certs/ca-certificates.crt')
client.clean_session = True
client.connect(mqttBroker, port=8883, keepalive=70)
co2 = 0

#code from https://github.com/JsBergbau/TFACO2AirCO2ntrol_CO2Meter/blob/main/co2monitor.py, i only added the mqtt part
def decrypt(key,  data):
	cstate = [0x48,  0x74,  0x65,  0x6D,  0x70,  0x39,  0x39,  0x65]
	shuffle = [2, 4, 0, 7, 1, 6, 5, 3]
	
	phase1 = [0] * 8
	for i, o in enumerate(shuffle):
		phase1[o] = data[i]
	
	phase2 = [0] * 8
	for i in range(8):
		phase2[i] = phase1[i] ^ key[i]
	
	phase3 = [0] * 8
	for i in range(8):
		phase3[i] = ( (phase2[i] >> 3) | (phase2[ (i-1+8)%8 ] << 5) ) & 0xff
	
	ctmp = [0] * 8
    for i in range(8):
		ctmp[i] = ( (cstate[i] >> 4) | (cstate[i]<<4) ) & 0xff
	
	out = [0] * 8
	for i in range(8):
		out[i] = (0x100 + phase3[i] - ctmp[i]) & 0xff
	
	return out

def hd(d):
	return " ".join("%02X" % e for e in d)

if __name__ == "__main__":
	# Key retrieved from /dev/random, guaranteed to be random ;)
	key = [0xc4, 0xc6, 0xc0, 0x92, 0x40, 0x23, 0xdc, 0x96]

	if (len(sys.argv) != 2):
		print("Please specifiy the device, mostly it is /dev/hidraw0")
		exit(1)
	
	fp = open(sys.argv[1], "a+b",  0)
	
	HIDIOCSFEATURE_9 = 0xC0094806
	set_report = [0x00] + key
	set_report = bytearray(set_report)
	fcntl.ioctl(fp, HIDIOCSFEATURE_9, set_report)
	
	values = {}

client.loop_start()
while True:
  data = list(fp.read(8))
  decrypted = None
  if data[4] == 0x0d and (sum(data[:3]) & 0xff) == data[3]:
    decrypted = data
  else:
    decrypted = decrypt(key, data)

  if decrypted[4] != 0x0d or (sum(decrypted[:3]) & 0xff) != decrypted[3]:
     print (hd(data), " => ", hd(decrypted),  "Checksum error")
  else:
    op = decrypted[0]
    val = decrypted[1] << 8 | decrypted[2]
	
    values[op] = val
    if 0x50 in values:
      if co2 != values[0x50]:
        co2 = (int(values[0x50]))
    
        #print('send')
        client.publish("living/air_quality/co2", co2, retain=True)
        #print("send: " + str(co2) + " to topic living/air_quality/co2")
client.loop_stop()
