import RPi.GPIO as GPIO
import time
import threading

# Pin Configuration
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

# GPIO Setup
def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
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

# LED Update Thread
def led_update_thread():
    while not exit_flag:
        if GPIO.input(LMMAX_PIN) or GPIO.input(LMMIN_PIN):
            set_leds(GPIO.HIGH, GPIO.LOW, GPIO.LOW)  # Red
        elif GPIO.input(BUTTON1_PIN) == GPIO.LOW or GPIO.input(BUTTON2_PIN) == GPIO.LOW:
            set_leds(GPIO.LOW, GPIO.LOW, GPIO.HIGH)  # Blue
        else:
            set_leds(GPIO.LOW, GPIO.HIGH, GPIO.LOW)  # Green
        time.sleep(0.1)

# Function to set LED colors
def set_leds(red, green, blue):
    GPIO.output(RED_PIN, red)
    GPIO.output(GREEN_PIN, green)
    GPIO.output(BLUE_PIN, blue)

# Stepper Motor Movement Function
def stepper_movement(direction, steps_per_second, stop_condition, buttonIn, buttonOut):
    GPIO.output(ENABLE_PIN, GPIO.LOW)
    GPIO.output(DIRECTION_PIN, direction)
    while (not GPIO.input(stop_condition)) and GPIO.input(buttonIn) == GPIO.LOW and GPIO.input(buttonOut) == GPIO.HIGH:
        GPIO.output(PULSE_PIN, GPIO.HIGH)
        time.sleep(1/(2*steps_per_second))
        GPIO.output(PULSE_PIN, GPIO.LOW)
        time.sleep(1/(2*steps_per_second))
    GPIO.output(PULSE_PIN, GPIO.LOW)

# Main Function
def main():
    setup_gpio()
    global exit_flag
    exit_flag = False
    led_thread = threading.Thread(target=led_update_thread)
    led_thread.start()

    try:
        while True:
            if GPIO.input(BUTTON1_PIN) == GPIO.LOW:
                stepper_movement(GPIO.LOW, 100, LMMAX_PIN, BUTTON1_PIN, BUTTON2_PIN)
            if GPIO.input(BUTTON2_PIN) == GPIO.LOW:
                stepper_movement(GPIO.HIGH, 100, LMMIN_PIN, BUTTON2_PIN, BUTTON1_PIN)
            if GPIO.input(BUTTON1_PIN) == GPIO.LOW and GPIO.input(BUTTON2_PIN) == GPIO.LOW:
                GPIO.output(ENABLE_PIN, GPIO.HIGH)
            else:
                GPIO.output(ENABLE_PIN, GPIO.LOW)
    except KeyboardInterrupt:
        exit_flag = True
        GPIO.cleanup()

if __name__ == "__main__":
    main()
