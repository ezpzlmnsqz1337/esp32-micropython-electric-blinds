from mqtt import MQTTClient
import machine
import time
import sys
import os


def readLineFromFileAsBytes(file):
    return bytes(file.readline().rstrip('\n').rstrip('\r'), 'utf-8')


with open('adaconfig', 'r') as f:
    ADAFRUIT_IO_URL = readLineFromFileAsBytes(f)
    ADAFRUIT_USERNAME = readLineFromFileAsBytes(f)
    ADAFRUIT_IO_KEY = readLineFromFileAsBytes(f)
    ADAFRUIT_IO_FEEDNAME = readLineFromFileAsBytes(f)

# create a random MQTT clientID
random_num = int.from_bytes(os.urandom(3), 'little')
mqtt_client_id = bytes('client_'+str(random_num), 'utf-8')

client = MQTTClient(client_id=mqtt_client_id,
                    server=ADAFRUIT_IO_URL,
                    user=ADAFRUIT_USERNAME,
                    password=ADAFRUIT_IO_KEY,
                    ssl=False)


def subscribe(callback):
    global client

    try:
        client.connect()
    except Exception as e:
        print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
        # sys.exit()

    mqtt_feedname = bytes(ADAFRUIT_USERNAME.decode('utf-8') + '/feeds/' +
                          ADAFRUIT_IO_FEEDNAME.decode('utf-8'), 'utf-8')
    # print(mqtt_feedname)
    client.set_callback(callback)
    try:
        client.subscribe(mqtt_feedname)
    except Exception as e:
        print('could not subscribe to feed of MQTT server {}{}'.format(
            type(e).__name__, e))
        # sys.exit()


def check():
    # print('check')
    global client
    client.check_msg()
