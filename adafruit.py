from mqtt import MQTTClient
import machine
import time
import sys
import os

client = None

ADAFRUIT_IO_URL = ''
ADAFRUIT_USERNAME = ''
ADAFRUIT_IO_KEY = ''
ADAFRUIT_IO_FEEDNAME = '' 


def subscribe(callback):

    # create a random MQTT clientID
    random_num = int.from_bytes(os.urandom(3), 'little')
    mqtt_client_id = bytes('client_'+str(random_num), 'utf-8')

    # connect to Adafruit IO MQTT broker using unsecure TCP (port 1883)
    #
    # To use a secure connection (encrypted) with TLS:
    #   set MQTTClient initializer parameter to "ssl=True"
    #   Caveat: a secure connection uses about 9k bytes of the heap
    #         (about 1/4 of the micropython heap on the ESP8266 platform)
  
    global ADAFRUIT_IO_URL
    global ADAFRUIT_USERNAME
    global ADAFRUIT_IO_KEY
    global ADAFRUIT_IO_FEEDNAME

    with open('adaconfig', 'r') as f:
        ADAFRUIT_IO_URL = f.readline()
        ADAFRUIT_USERNAME = f.readline()
        ADAFRUIT_IO_KEY = f.readline()
        ADAFRUIT_IO_FEEDNAME = f.readline()    

    global client
    client = MQTTClient(client_id=mqtt_client_id,
                        server=ADAFRUIT_IO_URL,
                        user=ADAFRUIT_USERNAME,
                        password=ADAFRUIT_IO_KEY,
                        ssl=False)

    try:
        client.connect()
    except Exception as e:
        print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
        sys.exit()

    mqtt_feedname = bytes(ADAFRUIT_USERNAME + '/feeds/' + ADAFRUIT_IO_FEEDNAME, 'utf-8')
    client.set_callback(callback)
    client.subscribe(mqtt_feedname)

def retry(callback):
    # print('retry')
    global client
    try:
        client.connect()
    except Exception as e:
        print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
        sys.exit()

    mqtt_feedname = bytes(ADAFRUIT_USERNAME + '/feeds/' + ADAFRUIT_IO_FEEDNAME, 'utf-8')
    client.set_callback(callback)
    client.subscribe(mqtt_feedname)

def check():
    # print('check')
    global client
    client.check_msg()
