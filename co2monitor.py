#!/usr/bin/python3 -u

import sys, fcntl, time

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
			
			 # Output all data, mark just received value with asterisk
			 #print (", ".join( "%s%02X: %04X %5i" % ([" ", "*"][op==k], k, v, v) for (k, v) in sorted(values.items())), "  ",)
			 ## From http://co2meters.com/Documentation/AppNotes/AN146-RAD-0401-serial-communication.pdf
			 if 0x50 in values:
				 print ("CO2: %4i" % values[0x50]) 
			 if 0x42 in values:
				 print ("T: %2.2f" % (values[0x42]/16.0-273.15))
			 if 0x44 in values:
				 print ("RH: %2.2f" % (values[0x44]/100.0))
			 print
