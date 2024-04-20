import RPi.GPIO as GPIO
import time

# Set the GPIO mode to BCM (Broadcom SOC channel numbering)
GPIO.setmode(GPIO.Board)

# Set the GPIO pin for the switch
switch_pin_left = 16
switch_pin_right = 18

# Set the GPIO pin as an input with a pull-up resistor
GPIO.setup(switch_pin_left, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(switch_pin_right, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Loop and read the state of the switch
while True:
    #test left switch
    if GPIO.input(switch_pin_left) == GPIO.HIGH:
        print("Left Switch is pushed.")
    else:
        print("Left Switch is not pushed.")

    time.sleep(2)

    #test right switch
    if GPIO.input(switch_pin_right) == GPIO.HIGH:
        print("Right Switch is pushed.")
    else:
        print("Right Switch is not pushed.")