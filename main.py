# Complete project details at https://RandomNerdTutorials.com

import machine
import dht
import time
from machine import Pin, SoftI2C, time_pulse_us
from machine_i2c_lcd import I2cLcd
from time import sleep_us

# Global sensor variables
current_temp = 0
current_humidity = 0
current_distance = 0

# Sensor setup
dht_sensor = dht.DHT22(Pin(4))
TRIG = Pin(27, Pin.OUT)
ECHO = Pin(26, Pin.IN)

# LCD setup
I2C_ADDR = 0x27
i2c = SoftI2C(sda=Pin(21), scl=Pin(22), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

def read_sensors():
    global current_temp, current_humidity, current_distance
    
    # Read DHT22
    try:
        dht_sensor.measure()
        current_temp = dht_sensor.temperature()
        current_humidity = dht_sensor.humidity()
    except OSError:
        current_temp = 0
        current_humidity = 0
    
    # Read ultrasonic
    TRIG.off(); sleep_us(2)
    TRIG.on(); sleep_us(10)
    TRIG.off()
    t = time_pulse_us(ECHO, 1, 30000)
    current_distance = (t * 0.0343) / 2.0 if t > 0 else 0

def web_page():
  if led.value() == 1:
    gpio_state="ON"
  else:
    gpio_state="OFF"
  
  html = """<html><head> <title>ESP IoT Lab Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="2">
  <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
  h1{color: #0F3376; padding: 2vh;}p{font-size: 1.2rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
  border-radius: 4px; color: white; padding: 12px 30px; text-decoration: none; font-size: 18px; margin: 5px; cursor: pointer;}
  .button2{background-color: #4286f4;}.button3{background-color: #28a745;}.sensor{background-color: #f8f9fa; padding: 10px; margin: 10px; border-radius: 5px;}
  input[type=text]{padding: 8px; margin: 5px; font-size: 16px; width: 200px;}</style></head><body> 
  <h1>ESP32 IoT Lab Control</h1> 
  
  <div class="sensor"><h3>LED Control</h3>
  <p>GPIO state: <strong>""" + gpio_state + """</strong></p>
  <p><a href="/?led=on"><button class="button">LED ON</button></a>
  <a href="/?led=off"><button class="button button2">LED OFF</button></a></p></div>
  
  <div class="sensor"><h3>Sensor Readings</h3>
  <p>Temperature: <strong>""" + str(current_temp) + """°C</strong></p>
  <p>Humidity: <strong>""" + str(current_humidity) + """%</strong></p>
  <p>Distance: <strong>""" + str(current_distance) + """ cm</strong></p></div>
  
  <div class="sensor"><h3>LCD Display Control</h3>
  <p><a href="/?show=temp"><button class="button button3">Show Temp on LCD</button></a>
  <a href="/?show=distance"><button class="button button3">Show Distance on LCD</button></a></p>
  <form action="/" method="get">
  <input type="text" name="lcd_text" placeholder="Enter custom message" maxlength="32">
  <button type="submit" class="button">Send to LCD</button></form></div>
  
  </body></html>"""
  return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
  conn, addr = s.accept()
  print('Got a connection from %s' % str(addr))
  request = conn.recv(1024)
  request = str(request)
  print('Content = %s' % request)
  # Read sensors before processing request
  read_sensors()
  
  # Parse URL parameters
  led_on = request.find('/?led=on')
  led_off = request.find('/?led=off')
  show_temp = request.find('/?show=temp')
  show_distance = request.find('/?show=distance')
  lcd_text_start = request.find('/?lcd_text=')
  
  # LED control
  if led_on == 6:
    print('LED ON')
    led.value(1)
  if led_off == 6:
    print('LED OFF')
    led.value(0)
  
  # LCD control
  if show_temp == 6:
    print('Showing temperature on LCD')
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr('Temp: {:.1f}C'.format(current_temp))
    lcd.move_to(0, 1)
    lcd.putstr('Humidity: {:.1f}%'.format(current_humidity))
  elif show_distance == 6:
    print('Showing distance on LCD')
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr('Distance:')
    lcd.move_to(0, 1)
    lcd.putstr('{:.1f} cm'.format(current_distance))
  elif lcd_text_start == 6:
    # Extract text from URL
    text_end = request.find(' HTTP')
    if text_end > lcd_text_start + 10:
      text = request[lcd_text_start + 10:text_end].replace('%20', ' ').replace('+', ' ')
      print('Displaying custom text:', text)
      lcd.clear()
      lcd.move_to(0, 0)
      if len(text) <= 16:
        lcd.putstr(text)
      else:
        lcd.putstr(text[:16])
        lcd.move_to(0, 1)
        lcd.putstr(text[16:32])
  response = web_page()
  conn.send('HTTP/1.1 200 OK\n')
  conn.send('Content-Type: text/html\n')
  conn.send('Connection: close\n\n')
  conn.sendall(response)
  conn.close()
