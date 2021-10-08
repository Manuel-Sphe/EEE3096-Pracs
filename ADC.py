#!/usr/bin/python3
 
import spidev
import time
import os
import threading
import datetime
import RPi.GPIO as GPIO



 
# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000
 
# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7

count = 1 # global 

def setup():
  # setup the board the mode
  GPIO.setmode(GPIO.BOARD)
  GPIO.setwarnings(False)

  GPIO.setup(7,GPIO.IN,pull_up_down = GPIO.PUD_UP)

 
  GPIO.add_event_detect(7,GPIO.FALLING,callback = general ,bouncetime = 300)


def general(channel):
    fun_10()

def fun_10():
  global count 
  count +=1 
  print_time_thread(10)

def fun_5(): 
  global count
  count +=1 
  print_time_thread(5)

def fun_1():
  global count
  count +=1
  print_time_thread(1)
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data
 
# Function to convert data to voltage level,
# rounded to specified number of decimal places.
def ConvertVolts(data,places):
  volts = (data * 3.3) / float(1023)
  volts = round(volts,places)
  return volts
 
# Function to calculate temperature from
# TMP36 data, rounded to specified
# number of decimal places.
def ConvertTemp(data,places):
 
  # ADC Value
  # (approx)  Temp  Volts
  #    0      -50    0.00
  #   78      -25    0.25
  #  155        0    0.50
  #  233       25    0.75
  #  310       50    1.00
  #  465      100    1.50
  #  775      200    2.50
  # 1023      280    3.30
 
  temp = ((data * 330)/float(1023))-50
  temp = round(temp,places)
  return temp
 
# Define sensor channels
light_channel = 0
temp_channel  = 1
 
# Define delay between readings
delay = 5

print("Runtime\t\tTemp Reading\t\tTemp\t\tLight Reading")

record = [] # for storing the run times
lap = [] # for storing the durations

Duration = [] # for storing time objects
def print_time_thread(length):
    """
    This functions prints the time to the screen every 10 seconds 
    """


    t_start =datetime.datetime.now()
    Duration.append(t_start)
  
    #print(Duration)
  
    thread = threading.Timer(length,print_time_thread,args = (length,) )
    thread.daemon = True # Daemon thread exit when the program does 
    
    thread.start()
    output  = ""
    if(len(Duration)==1):
      output = "Os"
      record.append(output)
    else:
      for i in range(len(Duration)-1):
        diff = Duration[i+1] - Duration[0] 
        output  = str(round(diff.total_seconds()))
        output = output+"s"
        #output = output[:output.index('.')]+"s"
      record.append(output) 


    #print(record)
    # read the light sensor data 
    light_level = ReadChannel(light_channel)
    light_volts = ConvertVolts(light_level,2)

    # Read the temperature sensor data 
    temp_level = ReadChannel(temp_channel)
    temp_volts = ConvertVolts(temp_level,2)
    temp = ConvertTemp(temp_level,2)

    # print out the results
    print(record[-1]+"\t\t"+str(temp_level)+"\t\t\t"+str(temp)+" C\t\t"+str(light_level))

if __name__ == "__main__":
    try:
      setup()
      # print_time_thread(10)
      # the program to run indefinitely
      i = 0 
      while i<7:
        time.sleep(10)
        i += 1
        pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
