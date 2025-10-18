import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class Shifter:
    # Handles all shift register operations (SN74HC595)

    def __init__(self, serialPin: int, clockPin: int, latchPin: int):
        # Save pin numbers for later use
        self.serialPin = serialPin
        self.clockPin  = clockPin
        self.latchPin  = latchPin

        # Set up pins as outputs and make sure they start low
        GPIO.setup(self.serialPin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.clockPin,  GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.latchPin,  GPIO.OUT, initial=GPIO.LOW)

    # Quick pulse used for both the clock and latch pins
    def __ping(self, pin: int) -> None:
        GPIO.output(pin, GPIO.HIGH)
        GPIO.output(pin, GPIO.LOW)

    # Sends an 8-bit value to the shift register
    def shiftByte(self, value: int) -> None:
        value &= 0xFF  # make sure it stays within 8 bits
        for i in range(8):
            bit = (value >> i) & 1  # shift out one bit at a time (LSB first)
            GPIO.output(self.serialPin, GPIO.HIGH if bit else GPIO.LOW)
            self.__ping(self.clockPin)  # pulse clock to shift data in
        self.__ping(self.latchPin)      # latch all bits to outputs

    # Turn all LEDs off
    def clear(self):
        self.shiftByte(0x00)

    # Turn all LEDs on
    def all_on(self):
        self.shiftByte(0xFF)
