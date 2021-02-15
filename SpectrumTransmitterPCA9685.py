#!/usr/bin/python3

# This script reads out the spectrum data from a named pipe
# and forwards it via i2c towards an PCA9685 device.
# This device is able to create up to 16 PWM signals.

# run sudo pip3 install adafruit-circuitpython-pca9685 once

import time
import os
import string

## Adafruit stuff
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685

## Initializing i2c and PCA 
i2c_bus = busio.I2C(SCL, SDA)
pca = PCA9685(i2c_bus)
pca.frequency = 2000

## Some definitions
pipe_name = '/home/pi/myfifosa'
size = 0
update_ui_interval = 0.01# update rate of the spectrum visualisation

pipe = None
pipe_polling_interval = 0.001 # readout rate of the named pipe, last valid dataset is taken

str = os.popen("cat /home/pi/.asoundrc | grep spectrum_size").read()
str = str.replace(" ","")
str = str.replace("spectrum_size","")
str = str.replace("\n","")
size = int(str)
pipe_size = 4 * size
## Open the pipe
try:            
    pipe = os.open(pipe_name, os.O_RDONLY | os.O_NONBLOCK)
    print('Pipe opened')
except Exception as e:
    print("Cannot open named pipe: " + self.pipe_name)
    
    
## Read data from the pipe and forward it, forever    
while True:
    
    data = [0]*pipe_size
    length = len(data)
    while True:
        try:
            n_data = os.read(pipe, pipe_size)
            time.sleep(pipe_polling_interval)
            if len(n_data) == length:
                data = n_data
        except:
            # print('Failed reading pipe.\n')
            break

    length = len(data)
    words = int(length / 4)
    out = [0]*words

    for m in range(words):
        v = data[4 * m] + (data[4 * m + 1] << 8) + (data[4 * m + 2] << 16) + (data[4 * m + 3] << 24)  
        
        out[m] = v
        # print(out[m])
# Send data to PCA9685 (pwm board)
    for m in range(16):
        pca.channels[m].duty_cycle = out[m]
    """
    os.system("clear")
    print("Spectrum")
    for line in range(22,-1, -1):
        outstr = "{:06} |".format(3000*line)
        for i in range(size):
            if out[i]>=3000*line:
                outstr = outstr + " ##"
            else:
                outstr = outstr + "   "
        print(outstr)

        outstr="" """
    time.sleep(update_ui_interval)
