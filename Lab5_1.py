#PWM
#note f= 1/T
#f = 0.2 --> T = 5 seconds
#brightness --> B = (sin(2πƒt))^2)

#initialize variables
import RPi.GPIO as GPIO
import time
import math
GPIO.setmode(GPIO.BCM)

pins=[4, 17, 27, 22, 5, 6, 13, 19, 26, 23] #pin number
base_f = 500
f= 0.2 #frequency
phase_sign = 1

for p in pins: #set each individualy pin as O
	GPIO.setup(p, GPIO.OUT)

pwms = [GPIO.PWM(p, base_f) for p in pins] #creates individual O
for pwm in pwms:
	pwm.start(0)

t0 = time.time()

button = 21  
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def button_push(channel):
	global phase_sign #can't be local
	phase_sign *=-1

GPIO.add_event_detect(button, GPIO.RISING, callback = button_push, bouncetime=250)

try:
	while True:
		t = time.time() - t0
		for i, pwm in enumerate(pwms): #index array of pins
			phi_i =i * (math.pi/9) * phase_sign # we have 10 leds not 12
			B_i = math.sin(2*math.pi*f*t-phi_i)**2 
			#change to +- phi to change direction
			dc_i= B_i * 100 #duty cycle
			pwm.ChangeDutyCycle(dc_i)
except KeyboardInterrupt:
    pass		

finally:
	GPIO.remove_event_detect(button)
	for pwm in pwms:
		pwm.ChangeDutyCycle(0)
		pwm.stop()
	GPIO.cleanup()