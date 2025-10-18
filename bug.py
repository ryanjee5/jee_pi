import RPi.GPIO as GPIO
import time
from bug import Bug   

S1 = 5     # on/off switch
S2 = 6     # wrap toggle switch
S3 = 13    # speed (3x faster when on)


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(S1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(S2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(S3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

bug = Bug()

bug_running = False
prev_s2 = GPIO.input(S2)

try:
    while True:
        s1 = GPIO.input(S1)  # on/off
        s2 = GPIO.input(S2)  # wrap toggle
        s3 = GPIO.input(S3)  # speed

        # a) s1 controls ON/OFF
        if s1 and not bug_running:
            bug.start()
            bug_running = True
        elif not s1 and bug_running:
            bug.stop()
            bug_running = False

        # b) when s2 changes, flip wrapping mode
        if s2 != prev_s2:
            bug.isWrapOn = not bug.isWrapOn
            prev_s2 = s2
            time.sleep(0.1)  # small delay to debounce

        # c) s3 triples the bug speed
        if s3:
            bug.timestep = 0.1 / 3.0
        else:
            bug.timestep = 0.1

        time.sleep(0.05)

except KeyboardInterrupt:
    pass

finally:
    bug.stop()
    GPIO.cleanup()
