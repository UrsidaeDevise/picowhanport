import network
import time
import gc
import machine
import config
from machine import UART
from machine import Pin
from umqtt.simple import MQTTClient

def passthrough(s):
   if s is None:
      return " "
   else:
      return s

uart = UART(1, baudrate=115200, invert=UART.INV_RX, rx=Pin(5), timeout=11000)

led = machine.Pin("LED", machine.Pin.OUT)
led.on()

network.hostname('HANmeter')
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config.SSID, config.PSK)
led.off()

waitcount = 0
while wlan.status() != 3:
   waitcount+=1
   time.sleep(0.5)
   led.toggle()
   if waitcount > 120:
      led.off()
      machine.reset()

#led on when connected to wlan
led.on()
print("WIFI CONNECTED")
mqc = MQTTClient("HANMeter", config.MQTTHost, 1883, config.MQTTUser, config.MQTTPass)
try:
   mqc.connect()
except:
   machine.soft_reset()
print("MQTT CONNECTED")
workbuffert = bytearray(1024)
mv = memoryview(workbuffert)

while True:
   mvpos=0
   i=0
   s = passthrough(uart.readline())
   while s[0] != ord('/'):
      s = passthrough(uart.readline())
      print("In loop", i)
      i=i+1
   print("NEW HAN PACKAGE")

   mv[mvpos : mvpos+len(s)] = s
   mvpos += len(s)
   led.off()
   while s[0]!= ord('!'):
      s = uart.readline()
      mv[mvpos : mvpos+len(s)] = s
      mvpos += len(s)
   try:
      mqc.publish(config.MQTTTopic,workbuffert[0:mvpos])
   except:
      machine.soft_reset()

   gc.collect()
   led.on()