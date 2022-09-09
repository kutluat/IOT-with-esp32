from machine import Pin, Timer, ADC
from time import sleep
import network
import time
from umqtt.robust import MQTTClient
import sys

WIFI_SSID     = ''
WIFI_PASSWORD = ''


ADAFRUIT_IO_URL     = 'io.adafruit.com' 
ADAFRUIT_USERNAME   = 'kutluat'
ADAFRUIT_IO_KEY     = ''


CURTAIN_ON_FEED_ID      = 'open'
CURTAIN_OFF_FEED_ID      = 'close'
DAYTIME_FEED_ID      = 'day'


curtain_on = Pin(2,Pin.OUT)
curtain_off = Pin(15,Pin.OUT)

sensor = ADC(Pin(34))
sensor.atten(ADC.ATTN_11DB)
mqtt_client_id = bytes('client_'+'1453', 'utf-8')
sensor_value = sensor.read()

def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.disconnect()
    wifi.connect(WIFI_SSID,WIFI_PASSWORD)
    if not wifi.isconnected():
        print('connecting..')
        timeout = 0
        while (not wifi.isconnected() and timeout < 10):
            print(10 - timeout)
            timeout = timeout + 1
            time.sleep(1) 
    if(wifi.isconnected()):
        print('connected')
    else:
        print('not connected')
        sys.exit()

connect_wifi()


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

def cb (topic, msg):                             
    print('Received Data:  Topic = {}, Msg = {}'.format(topic, msg))
    recieved_data = str(msg,'utf-8')            
    if recieved_data=="b'open":
        curtain_on.value(1)
        time.sleep(7)
        curtain_on.value(0)
        
    elif recieved_data=="b'close":
        curtain_off.value(1)
        time.sleep(7)
        curtain_off.value(0)




curtainon_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, CURTAIN_ON_FEED_ID), 'utf-8') 
curtainoff_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, CURTAIN_OFF_FEED_ID), 'utf-8')  
daytime_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, DAYTIME_FEED_ID), 'utf-8')



client.set_callback(cb)       
client.subscribe(curtainon_feed) 
client.subscribe(curtainoff_feed) 


def sens_data(data):
    sensor_value = sensor.read()
    client.publish(daytime_feed,    
                  bytes(str(sensor_value), 'utf-8'),   
                  qos=0)


timer = Timer(0)
timer.init(period=5000, mode=Timer.PERIODIC, callback = sens_data)



while True:   
    try:
        client.check_msg()                  
    except :
        client.disconnect()
        sys.exit()
