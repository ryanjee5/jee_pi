#PWM
#note f= 1/T
#f = 0.2 --> T = 5 seconds
#brightness --> B = (sin(2πƒt))^2)

#initialize variables
import RPi.GPIO as GPIO
import time
import math
GPIO.setmode(GPIO.BCM)
p=4 #pin number
base_f = 500
f= 0.2 #frequency

GPIO.setup(p, GPIO.OUT)
pwm = GPIO.PWM(p, base_f)
pwm.start(0)
t0 = time.time()

try:


	while True:
		t = time.time() - t0
		B = math.sin(2*math.pi*f*t)**2
		dc= B * 100 #duty cycle
pwm.ChangeDutyCycle(dc)
except KeyboardInterrupt:
    pass		

finally:
pwm.stop()
GPIO.cleanup()