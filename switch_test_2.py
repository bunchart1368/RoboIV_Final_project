import RPi.GPIO as GPIO
import time
import threading
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
RED_PIN = 17
GREEN_PIN = 27
BLUE_PIN = 22
BUTTON1_PIN = 23
BUTTON2_PIN = 24
LMMAX_PIN = 6
LMMIN_PIN = 12
PULSE_PIN = 16
DIRECTION_PIN = 20
ENABLE_PIN = 21

GPIO.setup(RED_PIN, GPIO.OUT)
GPIO.setup(GREEN_PIN, GPIO.OUT)
GPIO.setup(BLUE_PIN, GPIO.OUT)
GPIO.setup(BUTTON1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LMMAX_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LMMIN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PULSE_PIN, GPIO.OUT)
GPIO.setup(DIRECTION_PIN, GPIO.OUT)
GPIO.setup(ENABLE_PIN, GPIO.OUT)
def led_update_thread():
    while True:
        if GPIO.input(LMMAX_PIN) or GPIO.input(LMMIN_PIN):
            GPIO.output(RED_PIN, GPIO.HIGH)
            GPIO.output(GREEN_PIN, GPIO.LOW)
            GPIO.output(BLUE_PIN, GPIO.LOW)
        elif GPIO.input(BUTTON1_PIN) == GPIO.LOW or GPIO.input(BUTTON2_PIN) == GPIO.LOW:
            GPIO.output(RED_PIN, GPIO.LOW)
            GPIO.output(GREEN_PIN, GPIO.LOW)
            GPIO.output(BLUE_PIN, GPIO.HIGH)
        else:
            GPIO.output(RED_PIN, GPIO.LOW)
            GPIO.output(GREEN_PIN, GPIO.HIGH)
            GPIO.output(BLUE_PIN, GPIO.LOW)
        time.sleep(0.1)
led_thread = threading.Thread(target=led_update_thread)
led_thread.start()

def stepper_movement(direction, steps_per_second, stop_condition, buttonIn, buttonOut):
    GPIO.output(ENABLE_PIN, GPIO.LOW)
    GPIO.output(DIRECTION_PIN, direction)
    while (not GPIO.input(stop_condition)) and GPIO.input(buttonIn) == GPIO.LOW and GPIO.input(buttonOut) == GPIO.HIGH:
        GPIO.output(PULSE_PIN, GPIO.HIGH)
        time.sleep(1/(2*steps_per_second))
        GPIO.output(PULSE_PIN, GPIO.LOW)
        time.sleep(1/(2*steps_per_second))
    GPIO.output(PULSE_PIN, GPIO.LOW)

while True:
    if GPIO.input(BUTTON1_PIN) == GPIO.LOW:
        stepper_movement(GPIO.LOW, 100, LMMAX_PIN, BUTTON1_PIN, BUTTON2_PIN)
        print("Let stop move CCW")
    if GPIO.input(BUTTON2_PIN) == GPIO.LOW:
        stepper_movement(GPIO.HIGH, 100, LMMIN_PIN, BUTTON2_PIN, BUTTON1_PIN)
        print("Let stop move CW")
    if GPIO.input(BUTTON1_PIN) == GPIO.LOW and GPIO.input(BUTTON2_PIN) == GPIO.LOW:
        GPIO.output(ENABLE_PIN, GPIO.HIGH)
        print("Nothing press")
    else:
        GPIO.output(ENABLE_PIN, GPIO.LOW)
        print("Impossible to occur")