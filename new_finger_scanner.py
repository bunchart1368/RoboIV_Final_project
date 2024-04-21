import time
import board
import busio
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint

# Initialize UART communication
uart = busio.UART(board.TX, board.RX, baudrate=57600)

# Initialize fingerprint scanner
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

# Initialize built-in LED for status indication
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

def wait_for_finger():
    """Wait for a finger to be placed on the scanner."""
    print("Waiting for finger...")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass

def enroll_new_fingerprint():
    """Enroll a new fingerprint."""
    print("Place finger on sensor...")
    wait_for_finger()
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        print("Error: Failed to template image.")
        return False
    print("Remove finger and place again...")
    wait_for_finger()
    if finger.image_2_tz(2) != adafruit_fingerprint.OK:
        print("Error: Failed to template image.")
        return False
    if finger.create_model() != adafruit_fingerprint.OK:
        print("Error: Failed to create fingerprint model.")
        return False
    print("Fingerprint enrolled successfully!")
    return True

def search_fingerprint():
    """Search for a fingerprint match."""
    print("Searching for fingerprint...")
    if get_fingerprint():
        print("Fingerprint found! ID:", finger.finger_id, "Confidence:", finger.confidence)
    else:
        print("Fingerprint not found.")

def delete_fingerprint():
    """Delete a fingerprint."""
    print("Enter fingerprint ID to delete:")
    fingerprint_id = get_num()
    if finger.delete_model(fingerprint_id) == adafruit_fingerprint.OK:
        print("Fingerprint", fingerprint_id, "deleted successfully!")
    else:
        print("Failed to delete fingerprint", fingerprint_id)

def get_num():
    """Get a valid number from 1 to 127."""
    while True:
        try:
            num = int(input("Enter a number (1-127): "))
            if 1 <= num <= 127:
                return num
            else:
                print("Number must be between 1 and 127.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def main():
    while True:
        print("----------------")
        if finger.read_templates() != adafruit_fingerprint.OK:
            raise RuntimeError("Failed to read templates")
        print("Fingerprint templates:", finger.templates)
        print("e) Enroll fingerprint")
        print("f) Find fingerprint")
        print("d) Delete fingerprint")
        print("----------------")
        choice = input("Enter your choice: ").strip().lower()
        if choice == "e":
            enroll_new_fingerprint()
        elif choice == "f":
            search_fingerprint()
        elif choice == "d":
            delete_fingerprint()
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
