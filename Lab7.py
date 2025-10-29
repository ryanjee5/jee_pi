#!/usr/bin/env python3
# rpi_led_web_pwm.py
#
# Simple HTTP server (no JS) that controls 3 LED brightness levels via PWM.
# Uses Python's built-in http.server (TCP/IP) + RPi.GPIO.

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import RPi.GPIO as GPIO
import sys

# ---------- Hardware config ----------
# BCM pin numbers for your LEDs (change if needed)
LED_PINS = [17, 27, 22]       # LED1, LED2, LED3
PWM_FREQ = 500                # Hz

# ---------- GPIO setup ----------
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

_pwms = []
_duty = [0, 0, 0]             # persistent brightness levels (0–100)
_selected = 0                 # which LED the form currently shows as selected

for p in LED_PINS:
    GPIO.setup(p, GPIO.OUT, initial=GPIO.LOW)
    pwm = GPIO.PWM(p, PWM_FREQ)
    pwm.start(0)              # start off
    _pwms.append(pwm)

def set_brightness(idx: int, duty: int):
    duty = max(0, min(100, int(duty)))
    _duty[idx] = duty
    _pwms[idx].ChangeDutyCycle(duty)

def render_page() -> bytes:
    # Build radio buttons with the correct "checked" state and live % labels
    radios = []
    for i in range(3):
        checked = " checked" if i == _selected else ""
        label = f"LED {i+1} ({_duty[i]}%)"
        radios.append(
            f'<div><input type="radio" id="led{i}" name="led" value="{i}"{checked}>'
            f'<label for="led{i}">&nbsp;{label}</label></div>'
        )
    radios_html = "\n".join(radios)

    # Slider shows the CURRENT value for the currently selected LED
    slider_value = _duty[_selected]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>LED Brightness</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }}
    .card {{
      width: 280px; padding: 14px; border: 1px solid #ccc; border-radius: 8px;
      margin: 18px; background: #fafafa;
    }}
    fieldset {{ border: none; margin: 0; padding: 0; }}
    .btn {{
      margin-top: 10px; padding: 6px 10px; border: 1px solid #aaa; border-radius: 6px;
      background: #eee; cursor: pointer;
    }}
    small {{ color: #444; }}
  </style>
</head>
<body>
  <div class="card">
    <form method="POST" action="/">
      <fieldset>
        <div><strong>Brightness level:</strong></div>
        <input type="range" name="level" min="0" max="100" value="{slider_value}">
      </fieldset>
      <br>
      <fieldset>
        <div><strong>Select LED:</strong></div>
        {radios_html}
      </fieldset>
      <button class="btn" type="submit">Change Brightness</button>
    </form>

    <p><small>
      Current levels — LED1: {_duty[0]}% · LED2: {_duty[1]}% · LED3: {_duty[2]}%
    </small></p>
  </div>
</body>
</html>"""
    return html.encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        body = render_page()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        global _selected
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = self.rfile.read(length).decode("utf-8")
            form = parse_qs(data)

            # Which LED radio was chosen?
            if "led" in form and len(form["led"]) > 0:
                _selected = int(form["led"][0])

            # New level applies only to the selected LED
            if "level" in form and len(form["level"]) > 0:
                new_level = int(float(form["level"][0]))
                set_brightness(_selected, new_level)

        except Exception as e:
            print(f"POST parse/apply error: {e}", file=sys.stderr)

        # Always return a fresh page showing current levels
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        body = render_page()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # Quiet the default logging a bit
    def log_message(self, fmt, *args):
        return

def main(port=8000):
    server = HTTPServer(("", port), Handler)
    print(f"Serving on http://0.0.0.0:{port}  (Ctrl+C to quit)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        for pwm in _pwms:
            pwm.stop()
        GPIO.cleanup()
        print("\nClean exit.")

if __name__ == "__main__":
    # Optionally accept a port number: python3 rpi_led_web_pwm.py 8080
    if len(sys.argv) > 1:
        main(int(sys.argv[1]))
    else:
        main()
