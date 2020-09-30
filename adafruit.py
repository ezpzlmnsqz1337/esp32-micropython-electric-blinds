from mqtt import MQTTClient
import machine
import time
import sys
import os

client = None


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

    ADAFRUIT_IO_URL = b'io.adafruit.com'
    ADAFRUIT_USERNAME = b'ezpzlmnsqz1337'
    ADAFRUIT_IO_KEY = b'aio_bugv6280YvKRrteaHgNKkTsKRFLv'
    ADAFRUIT_IO_FEEDNAME = b'blinds'

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

    mqtt_feedname = bytes('ezpzlmnsqz1337/feeds/blinds', 'utf-8')
    client.set_callback(callback)
    client.subscribe(mqtt_feedname)


def check():
    global client
    print(client)
    try:
        client.check_msg()
    except:
        client.connect()
        client.check_msg()
