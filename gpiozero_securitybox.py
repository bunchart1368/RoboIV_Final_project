#import library for fingerprint
import time
import board
import busio
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint

#import library for stepper motor, switch and button
from gpiozero import LED, Button, DigitalOutputDevice, DigitalInputDevice
from gpiozero.tools import negated
import time
import threading

#Set up for fingerprint
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

import serial
uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)

finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

#Set up for stepper motor, switch and button
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

# Setup LED outputs
red_led = LED(RED_PIN)
green_led = LED(GREEN_PIN)
blue_led = LED(BLUE_PIN)

# Setup Button inputs with pull-up resistors
button1 = Button(BUTTON1_PIN, pull_up=True)
button2 = Button(BUTTON2_PIN, pull_up=True)

# Setup other GPIO outputs
enable_output = DigitalOutputDevice(ENABLE_PIN)
direction_output = DigitalOutputDevice(DIRECTION_PIN)
pulse_output = DigitalOutputDevice(PULSE_PIN)

# Set up limit switch
# Create button objects for stop conditions
lmmax = DigitalInputDevice(6)
lmmin = DigitalInputDevice(12)

# Create negated button objects for use with stepper_movement
lmmax_negated = negated(lmmax)
lmmin_negated = negated(lmmin)

#This is for limit checking
def led_update_thread():
        if LMMAX_PIN.is_active:
            red_led.on()
            green_led.off()
            blue_led.off()
        elif LMMIN_PIN.is_active:
            red_led.off()
            green_led.off()
            blue_led.on()
        else:
            red_led.off()
            green_led.on()
            blue_led.off()
        time.sleep(0.1)
led_thread = threading.Thread(target=led_update_thread)
led_thread.start()

######################Function for fingerprint############################


def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image...")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Searching...")
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True


# pylint: disable=too-many-branches
def get_fingerprint_detail():
    """Get a finger print image, template it, and see if it matches!
    This time, print out each error instead of just returning on failure"""
    print("Getting image...", end="")
    i = finger.get_image()
    if i == adafruit_fingerprint.OK:
        print("Image taken")
    else:
        if i == adafruit_fingerprint.NOFINGER:
            print("No finger detected")
        elif i == adafruit_fingerprint.IMAGEFAIL:
            print("Imaging error")
        else:
            print("Other error")
        return False

    print("Templating...", end="")
    i = finger.image_2_tz(1)
    if i == adafruit_fingerprint.OK:
        print("Templated")
    else:
        if i == adafruit_fingerprint.IMAGEMESS:
            print("Image too messy")
        elif i == adafruit_fingerprint.FEATUREFAIL:
            print("Could not identify features")
        elif i == adafruit_fingerprint.INVALIDIMAGE:
            print("Image invalid")
        else:
            print("Other error")
        return False

    print("Searching...", end="")
    i = finger.finger_fast_search()
    # pylint: disable=no-else-return
    # This block needs to be refactored when it can be tested.
    if i == adafruit_fingerprint.OK:
        print("Found fingerprint!")
        return True
    else:
        if i == adafruit_fingerprint.NOTFOUND:
            print("No match found")
        else:
            print("Other error")
        return False


# pylint: disable=too-many-statements
def enroll_finger(location):
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="",flush=True)
            sensor=1
        else:
            print("Place same finger again...", end="",flush=True)

        time.sleep(1)
        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                print("Image taken",flush=True)
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="",flush=True)
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Imaging error",flush=True)
                return False
            else:
                print("Other error",flush=True)
                return False

        print("Templating...", end="",flush=True)
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            print("Templated",flush=True)
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image too messy",flush=True)
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could not identify features",flush=True)
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image invalid",flush=True)
            else:
                print("Other error",flush=True)
            return False

        if fingerimg == 1:
            print("Remove finger")
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creating model...", end="")
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print("Storing model #%d..." % location, end="")
    i = finger.store_model(location)
    if i == adafruit_fingerprint.OK:
        print("Stored")
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            print("Bad storage location")
        elif i == adafruit_fingerprint.FLASHERR:
            print("Flash storage error")
        else:
            print("Other error")
        return False

    return True

def get_num():
    """Use input() to get a valid number from 1 to 127. Retry till success!"""
    i = 0
    while (i > 127) or (i < 1):
            i = int(input("Enter ID # from 1-127: "))
    return i


######################Function for stepper and switch############################
# Function to control stepper movement
def stepper_movement(direction, steps_per_second, stop_condition):
    enable_output.on()  # Enable the stepper motor
    direction_output.value = direction  # Set the direction

    while not stop_condition.is_active:
        pulse_output.on()  # Generate a pulse
        time.sleep(1 / (2 * steps_per_second))
        pulse_output.off()
        time.sleep(1 / (2 * steps_per_second))

    pulse_output.off()  # Ensure pulse pin is low after movement
    return

def close_box(steps_per_second):
    stepper_movement(0, steps_per_second, lmmax_negated)
    return

def open_box(steps_per_second):
    stepper_movement(1, steps_per_second, lmmin_negated)
    return

# Function to move the motor
def motor_move(direction):
    if direction == 'cw':
        stepper_movement(1, 50, lmmin_negated)
    elif direction == 'ccw':
        stepper_movement(0, 50, lmmax_negated)

####################### Main ############################
def main():
    #Main parameter
    previous_finger_id=0
    current_finger_id=0

    steps_per_second=50

    while True:
        print("----------------")
        if finger.read_templates() != adafruit_fingerprint.OK:
            raise RuntimeError("Failed to read templates")
        print("Fingerprint templates:", finger.templates)
        print("e) enroll print")
        print("f) find print")
        print("d) delete print")
        print("----------------")
        c = input("> ")

        if c == "e":
            enroll_finger(get_num())
        if c == "f":
            exit=False
            print("Security box activated(Press anything to exit)")
            try:
                while not(exit) :
                    if get_fingerprint():
                        current_finger_id=finger.finger_id
                        if(current_finger_id==previous_finger_id):
                            close_box(steps_per_second)
                            previous_finger_id=0
                        else:
                            open_box(steps_per_second)
                        print("Detected #", finger.finger_id, "with confidence", finger.confidence)
                        previous_finger_id=finger.finger_id
                    else:
                        print("Finger not found, please try again")
                        time.sleep(1)
                pass
            except KeyboardInterrupt:
                print("Keyboard interrupt detected. Exiting...")
                exit=True
        if c == "d":
            if finger.delete_model(get_num()) == adafruit_fingerprint.OK:
                print("Deleted!")
            else:
                print("Failed to delete")

if __name__ == "__main__":
    main()
    #motor_move('cw')
    #motor_move('ccw')