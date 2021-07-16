import RPi.GPIO as GPIO
import time
import board
import busio
import adafruit_sgp30
import ctypes
from influxdb import InfluxDBClient

# setup the waveshare hat
class SHTC3:
    def __init__(self):
        self.dll = ctypes.CDLL(
            "/home/pi/code/environment-monitor/SHTC3.so"
        )  # this needs to be the path to the .so file
        init = self.dll.init
        init.restype = ctypes.c_int
        init.argtypes = [ctypes.c_void_p]
        init(None)

    def SHTC3_Read_Temperature(self):
        temperature = self.dll.SHTC3_Read_TH
        temperature.restype = ctypes.c_float
        temperature.argtypes = [ctypes.c_void_p]
        return temperature(None)

    def SHTC3_Read_Humidity(self):
        humidity = self.dll.SHTC3_Read_RH
        humidity.restype = ctypes.c_float
        humidity.argtypes = [ctypes.c_void_p]
        return humidity(None)


shtc3 = SHTC3()
temperature = round(shtc3.SHTC3_Read_Temperature())
humidity = round(shtc3.SHTC3_Read_Humidity())
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

# Setup the SGP30 sensor
# Create library object on our I2C port
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
sgp30.iaq_init()
sgp30.set_iaq_baseline(0x8973, 0x8AAE)
eco2 = 0


# Setup the gpio pins for the CO2 traffic light
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

green = 18
yellow = 27
red = 22

# set pins to out
GPIO.setup(red, GPIO.OUT)
GPIO.setup(yellow, GPIO.OUT)
GPIO.setup(green, GPIO.OUT)

# set all lights to off
GPIO.output(red, False)
GPIO.output(yellow, False)
GPIO.output(green, False)


# the final loop, will run until interrupted
while True:
    eco2 = sgp30.eCO2
    print(
        f"eco2 = {eco2}"
    )  # isn't needed, but visually will tell you if script is running

    if eco2 <= 1000:
        GPIO.output(green, True)
        GPIO.output(yellow, False)
        GPIO.output(red, False)

    if eco2 >= 1001 and eco2 <= 2000:
        GPIO.output(green, False)
        GPIO.output(yellow, True)
        GPIO.output(red, False)

    if eco2 >= 2001:
        GPIO.output(green, False)
        GPIO.output(yellow, False)
        GPIO.output(red, True)

    time.sleep(1)

    # send the data to influxdb
    client = InfluxDBClient(
        host="192.168.178.18", port="8086", username="livingroom", password="livingroom"
    )
    line = f"environments,room=livingroom temperature={temperature},humidity={humidity},eco2={eco2}"
    client.write([line], {"db": "environments"}, 204, "line")
    client.close()
