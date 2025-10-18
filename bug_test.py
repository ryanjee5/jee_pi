import RPi.GPIO as GPIO
import time

# Same pins as in bug.py
S1 = 5
S2 = 6
S3 = 13

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(S1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(S2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(S3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

print("Monitoring switches... (Press Ctrl+C to stop)")
print("Press or release any switch to see its state change.\n")

prev_states = {S1: GPIO.input(S1), S2: GPIO.input(S2), S3: GPIO.input(S3)}

try:
    while True:
        for pin, name in [(S1, "S1"), (S2, "S2"), (S3, "S3")]:
            state = GPIO.input(pin)
            if state != prev_states[pin]:
                print(f"{name} {'ON' if state else 'OFF'}")
                prev_states[pin] = state
        time.sleep(0.05)

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
