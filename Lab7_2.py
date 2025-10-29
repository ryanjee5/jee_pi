import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import RPi.GPIO as GPIO
import sys

LED_PINS = [17, 27, 22]       # LED1, LED2, LED3
PWM_FREQ = 500                # Hz

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

_pwms = []
_duty = [0, 0, 0]             # brightness levels (0–100)
_selected = 0                 # the selected LED

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
    sliders_html = []
    for i in range(3):
        sliders_html.append(f"""
        <div class="row">
          <div class="label">LED{i+1}</div>
          <input id="s{i}" type="range" min="0" max="100" value="{_duty[i]}">
          <div class="val"><span id="v{i}">{_duty[i]}</span></div>
        </div>
        """)
    sliders_html = "\n".join(sliders_html)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>LED Controls</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }}
    .card {{ width: 360px; padding: 14px; border: 1px solid #ccc; border-radius: 10px;
             margin: 18px; background: #fafafa; }}
    .row {{ display: grid; grid-template-columns: 60px 1fr 40px; align-items: center; gap: 10px; margin: 12px 0; }}
    .label {{ color: #333; }}
    .val {{ text-align: right; width: 40px; }}
    input[type=range] {{ width: 100%; }}
    .hint {{ color:#555; font-size:12px; }}
  </style>
</head>
<body>
  <div class="card">
    {sliders_html}
    <div class="hint">Triple Slider!</div>
  </div>

  <script>
    // Simple debounce so we don't spam the server while dragging.
    function debounce(fn, ms) {{
      let t; return (...args) => {{ clearTimeout(t); t = setTimeout(() => fn(...args), ms); }};
    }}

    function postLevel(led, level) {{
      const body = new URLSearchParams();
      body.append('led', String(led));
      body.append('level', String(level));
      fetch('/', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
        body
      }})
      .then(r => r.json())
      .then(data => {{
        // Optionally keep labels in sync with server's authoritative values
        if (data && Array.isArray(data.duty)) {{
          data.duty.forEach((val, idx) => {{
            const vs = document.getElementById('v' + idx);
            if (vs) vs.textContent = val;
          }});
        }}
      }})
      .catch(() => {{ /* ignore network hiccups */ }});
    }}

    // Hook up sliders
    for (let i = 0; i < 3; i++) {{
      const s = document.getElementById('s' + i);
      const v = document.getElementById('v' + i);
      const send = debounce(() => postLevel(i, s.value), 80); // ~12.5 Hz
      if (s && v) {{
        s.addEventListener('input', () => {{
          v.textContent = s.value; // live display
          send();
        }});
      }}
    }}
  </script>
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

            # translates code to be read in python
            form = parse_qs(data)

            if "led" in form and form["led"]:
                _selected = int(form["led"][0])

            if "level" in form and form["level"]:
                new_level = int(float(form["level"][0]))
                set_brightness(_selected, new_level)

            # Respond with JSON so fetch can update labels
            payload = json.dumps({
                "ok": True,
                "duty": _duty,
                "selected": _selected
            }).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        except Exception as e:
            err = json.dumps({"ok": False, "error": str(e)}).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(err)))
            self.end_headers()
            self.wfile.write(err)

   
    def log_message(self, fmt, *args): #no spam
        return


def main(port=8000): #starts server
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

if __name__ == "__main__":#if the file is ran start the server
    
    if len(sys.argv) > 1:
        main(int(sys.argv[1]))
    else:
        main()
