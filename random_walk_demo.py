# random_walk_demo.py  (Step 4)
import time, random
import RPi.GPIO as GPIO
from shifter import Shifter

def main():
    s = Shifter(23, 25, 24)   # SER=23, SRCLK=25, RCLK=24
    x = 3
    dt = 0.05                 # <= requirement: 0.05 s timestep (clamped edges)
    s.shiftByte(1 << x)
    try:
        while True:
            step = random.choice([-1, 1])
            x = max(0, min(7, x + step))   # clamp at edges
            s.shiftByte(1 << x)
            time.sleep(dt)
    except KeyboardInterrupt:
        pass
    finally:
        s.clear()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
