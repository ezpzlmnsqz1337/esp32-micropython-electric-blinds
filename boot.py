# This file is executed on every boot (including wake-boot from deepsleep)
import time
import network
import webrepl
import stepper
import esp
esp.osdebug(None)

# disable motors first thing we do
# motors settings
motors = (
    stepper.MyStepper(5, 18, 19, 21, 0),
    stepper.MyStepper(13, 12, 14, 27, 1)
)

for m in motors:
    m.disable()

#from upysh import *
#import machine

# mdns = network.mDNS()
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Hardcoded password in plaintext :-D
NETWORKS = {
    "ssid": "password"
}

wifiConnected = False


def startAP():
    wlanAP = network.WLAN(network.AP_IF)
    wlanAP.active(True)
    return wlanAP


cycle = 0
while not wlan.isconnected() and cycle < 10:
    print("Scanning networks...")
    scanResult = wlan.scan()
    for i in range(len(scanResult)):
        ssid = scanResult[i][0].decode()

        if ssid in NETWORKS:
            print("Trying to connect to ", ssid)

            # SSID found in a table of known APs
            wlan.connect(ssid, NETWORKS[ssid])

            timeout = 0
            while not wlan.isconnected():
                timeout += 1
                time.sleep(1)
                print("Attempt ", timeout, " out of 10")
                if (timeout >= 10):
                    print("Unable to connect to the WiFi")
                    break

            wifiConnected = wlan.isconnected()

        else:
            print("Record for SSID ", ssid, " not found, let's try next one")

    cycle += 1

if wifiConnected:
    print("Connected to the wifi")
    print(wlan.ifconfig())

else:
    print("Unable to connect to the WiFi, let's start own AP")
    AP = startAP()
    print(AP.ifconfig())

del(cycle)
del(ssid)
del(i)
del(wifiConnected)

#mdns.start('mPy', 'MicroPython ESP32')
#ftp.start(user='YOUR_USERNAME', password='YOUR_PASSWORD')
#telnet.start(user='YOUR_USERNAME', password='YOUR_PASSWORD')

webrepl.start()
