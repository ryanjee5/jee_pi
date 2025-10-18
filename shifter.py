# shifter.py
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class Shifter:
    """
    74HC595 driver.
    serialPin -> SER  (pin 14)
    clockPin  -> SRCLK (pin 11)
    latchPin  -> RCLK (pin 12)
    """
    def __init__(self, serialPin: int, clockPin: int, latchPin: int):
        self.serialPin = serialPin
        self.clockPin  = clockPin
        self.latchPin  = latchPin
        GPIO.setup(self.serialPin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.clockPin,  GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.latchPin,  GPIO.OUT, initial=GPIO.LOW)

    # private "ping" per spec (Python-private via name-mangling)
    def __ping(self, pin: int) -> None:
        GPIO.output(pin, GPIO.HIGH)
        GPIO.output(pin, GPIO.LOW)

    # public method per spec
    def shiftByte(self, value: int) -> None:
        value &= 0xFF
        for i in range(8):                  # LSB-first to QA..QH
            bit = (value >> i) & 1
            GPIO.output(self.serialPin, GPIO.HIGH if bit else GPIO.LOW)
            self.__ping(self.clockPin)      # rising edge clocks bit
        self.__ping(self.latchPin)          # latch outputs

    def clear(self):
        self.shiftByte(0x00)

    def all_on(self):
        self.shiftByte(0xFF)

# (optional) quick self-test for Step 2 if you run `python3 shifter.py` directly
if __name__ == "__main__":
    s = Shifter(23, 25, 24)   # SER, SRCLK, RCLK
    try:
        for i in range(8):
            s.shiftByte(1 << i)
        s.all_on()
    finally:
        s.clear()
