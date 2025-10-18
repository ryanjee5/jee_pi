# bug.py
import time, random, threading
import RPi.GPIO as GPIO
from shifter import Shifter

# -------- Bug class (Step 5) --------
class Bug:
    """
    Random-walk LED "bug" on an 8-LED bar (via 74HC595).
    Defaults per spec: timestep=0.1, x=3, isWrapOn=False.
    Composition: private __shifter (Shifter object).
    """
    def __init__(self, timestep: float = 0.1, x: int = 3, isWrapOn: bool = False,
                 serialPin: int = 23, clockPin: int = 25, latchPin: int = 24):
        self.timestep = float(timestep)     # Step 5: attribute
        self.x        = max(0, min(7, int(x)))  # Step 5: attribute
        self.isWrapOn = bool(isWrapOn)      # Step 5: attribute
        self.__shifter = Shifter(serialPin, clockPin, latchPin)  # Step 5: private composition

        self.__running = False
        self.__thread  = None
        self.__shifter.shiftByte(1 << self.x)

    def __step_once(self):
        move = random.choice([-1, 1])
        nx = self.x + move
        if self.isWrapOn:
            self.x = (nx + 8) % 8
        else:
            self.x = 0 if nx < 0 else (7 if nx > 7 else nx)
        self.__shifter.shiftByte(1 << self.x)

    def __loop(self):
        try:
            while self.__running:
                self.__step_once()
                time.sleep(self.timestep)
        finally:
            self.__shifter.clear()

    def start(self):  # Step 5: start()
        if self.__running:
            return
        self.__running = True
        self.__thread = threading.Thread(target=self.__loop, daemon=True)
        self.__thread.start()

    def stop(self):   # Step 5: stop()
        if not self.__running:
            self.__shifter.clear()
            return
        self.__running = False
        if self.__thread:
            self.__thread.join()
            self.__thread = None
        self.__shifter.clear()

# -------- Step 6: S1/S2/S3 control loop --------
S1 = 5    # a) on/off
S2 = 6    # b) wrap toggle on any state change
S3 = 13   # d) 3x speed when on

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(S1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(S2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(S3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    bug = Bug()                # Step 6 says: default speed/position/wrapping
    base_dt = 0.1
    running = False
    prev_s2 = GPIO.input(S2)

    try:
        while True:
            s1 = GPIO.input(S1)
            s2 = GPIO.input(S2)
            s3 = GPIO.input(S3)

            # (b) S1 controls on/off
            if s1 and not running:
                bug.start()
                running = True
            elif not s1 and running:
                bug.stop()
                running = False

            # (c) S2 edge flips wrapping state
            if s2 != prev_s2:
                bug.isWrapOn = not bug.isWrapOn
                prev_s2 = s2
                time.sleep(0.1)  # simple debounce

            # (d) S3 triples speed (delay ÷ 3)
            bug.timestep = (base_dt / 3.0) if s3 else base_dt

            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        bug.stop()
        GPIO.cleanup()
