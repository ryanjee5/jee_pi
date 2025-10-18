# bug.py
import time, random, threading
import RPi.GPIO as GPIO
from shifter import Shifter   # <-- use your shifter.py

# ----------------- Bug class -----------------
class Bug:
    """
    Random-walk LED 'bug' on an 8-LED bar (74HC595 via Shifter).
    Defaults: timestep=0.1 s, start x=3, wrap off.
    """
    def __init__(self, timestep=0.1, x=3, isWrapOn=False,
                 serialPin=23, clockPin=25, latchPin=24):
        self.timestep = float(timestep)
        self.x        = max(0, min(7, int(x)))
        self.isWrapOn = bool(isWrapOn)
        self.__shifter = Shifter(serialPin, clockPin, latchPin)

        self.__running = False
        self.__thread  = None
        self.__shifter.shiftByte(1 << self.x)  # show initial LED

    def __step_once(self):
        step  = random.choice([-1, 1])
        nx    = self.x + step
        self.x = (nx + 8) % 8 if self.isWrapOn else max(0, min(7, nx))
        self.__shifter.shiftByte(1 << self.x)

    def __loop(self):
        try:
            while self.__running:
                self.__step_once()
                time.sleep(self.timestep)
        finally:
            self.__shifter.clear()  # turn off LED when stopping

    def start(self):
        if self.__running:
            return
        self.__running = True
        self.__thread = threading.Thread(target=self.__loop, daemon=True)
        self.__thread.start()

    def stop(self):
        if not self.__running:
            self.__shifter.clear()
            return
        self.__running = False
        if self.__thread:
            self.__thread.join()
            self.__thread = None
        self.__shifter.clear()

# ----------------- Main control loop -----------------
# Inputs for your switches:
S1 = 5    # on/off
S2 = 6    # wrap toggle (edge-triggered)
S3 = 13   # 3x speed while pressed

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(S1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(S2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(S3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    bug = Bug()                  # defaults: timestep=0.1, x=3, wrap=False
    base_dt = 0.1
    running = False
    prev_s2 = GPIO.input(S2)     # for edge detection

    try:
        while True:
            s1 = GPIO.input(S1)
            s2 = GPIO.input(S2)
            s3 = GPIO.input(S3)

            # a) S1 controls ON/OFF
            if s1 and not running:
                bug.start()
                running = True
            elif not s1 and running:
                bug.stop()
                running = False

            # b) S2 change flips wrap mode
            if s2 != prev_s2:
                bug.isWrapOn = not bug.isWrapOn
                prev_s2 = s2
                time.sleep(0.1)   # debounce

            # c) S3 speeds up by 3x while pressed
            bug.timestep = (base_dt / 3.0) if s3 else base_dt

            time.sleep(0.05)      # poll rate

    except KeyboardInterrupt:
        pass
    finally:
        bug.stop()
        GPIO.cleanup()
