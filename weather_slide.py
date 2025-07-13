#!/usr/bin/env python3
"""
Daily HTML weather e‑mail for Inwood, WV.

• Fetches a 10‑day forecast from Open‑Meteo.
• Uses daily apparent temperature as a Heat‑Index proxy.
• Adds precipitation probability, emoji conditions, and heat‑stress policy.
• Sends a responsive HTML e‑mail via SendGrid.

Required packages (see requirements.txt):
    requests
    sendgrid
"""

import os
import datetime as dt
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# ── 1  configuration ────────────────────────────────────────────
LATITUDE   = float(os.getenv("LATITUDE", "39.36"))
LONGITUDE  = float(os.getenv("LONGITUDE", "-78.05"))
TIMEZONE   = os.getenv("TIMEZONE", "America/New_York")
SG_KEY     = os.getenv("SENDGRID_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO   = [e.strip() for e in os.getenv("EMAIL_TO", "").split(",") if e.strip()]

if not (SG_KEY and EMAIL_FROM and EMAIL_TO):
    raise RuntimeError("Missing SendGrid key or e‑mail addresses in environment.")

today_str = dt.date.today().strftime("%Y-%m-%d")

# ── 2  fetch forecast ───────────────────────────────────────────
URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LATITUDE}&longitude={LONGITUDE}"
    "&daily=apparent_temperature_max,temperature_2m_max,temperature_2m_min,"
    "weathercode,precipitation_probability_max"
    "&forecast_days=10&temperature_unit=fahrenheit"
    f"&timezone={TIMEZONE}"
)
daily = requests.get(URL, timeout=15).json()["daily"]
hi_today = round(daily["apparent_temperature_max"][0])

# ── 3  heat‑stress policy ───────────────────────────────────────
POLICY = [
    (80,  90,  "Caution",         "30", "1/20", "Normal",     "Periodic"),
    (91,  103, "Extreme Caution", "15", "1/15", "30-40/10",   "1"),
    (104, 124, "Danger",          "10", "1/10", "20-30/10",   "2"),
    (125, 999, "Extreme Danger",  "0",  "1/10", "10-20/10",   "4"),
]
for lo, hi, warn, work, hyd, wr, chk in POLICY:
    if lo <= hi_today <= hi:
        warn_lvl, work_max, hydration, work_rest, checks_hr = warn, work, hyd, wr, chk
        break

# ── 4  emoji map ────────────────────────────────────────────────
EMOJI = {
    0:"☀️",1:"🌤️",2:"⛅",3:"☁️",45:"🌫️",48:"🌫️",
    51:"🌦️",53:"🌧️",55:"🌧️",61:"🌦️",63:"🌧️",65:"🌧️",
    71:"🌨️",73:"🌨️",75:"❄️",80:"🌦️",81:"🌧️",
    95:"⛈️",96:"⛈️",99:"⛈️"
}

# ── 5  build HTML ───────────────────────────────────────────────
rows = ""
for d, hi, lo, code, rain in zip(
        daily["time"],
        daily["temperature_2m_max"],
        daily["temperature_2m_min"],
        daily["weathercode"],
        daily["precipitation_probability_max"]):
    rows += (
        f"<tr><td>{d}</td><td>{int(hi)}°</td><td>{int(lo)}°</td>"
        f"<td style='text-align:center;font-size:1.2em'>{EMOJI.get(code,'')}</td>"
        f"<td>{rain}%</td></tr>"
    )

policy_html = ""
for lo, hi, warn, work, hyd, wr, chk in POLICY:
    shade = " style='background:#ffcc66'" if warn == warn_lvl else ""
    hi_range = f"{lo}-{hi if hi < 999 else '＋'}"
    policy_html += (
        f"<tr{shade}><td>{warn}</td><td>{hi_range}°</td><td>{work}</td>"
        f"<td>{hyd}</td><td>{wr}</td><td>{chk}</td></tr>"
    )

html = f"""
<h2 style='margin-bottom:4px'>Inwood Weather — {today_str}</h2>
<p style='margin:0;font-size:16px'><b>Peak Heat Index Today:</b> {hi_today} °F ({warn_lvl})</p>
<p style='margin:0 0 8px;font-size:14px;color:#555'>Guidance below ⬇︎</p>

<table border='1' cellpadding='4' cellspacing='0' style='border-collapse:collapse'>
  <thead style='background:#4f81bd;color:#fff'>
    <tr><th>Date</th><th>High °F</th><th>Low °F</th><th>Cond</th><th>Precip %</th></tr>
  </thead><tbody>{rows}</tbody>
</table>

<h3 style='margin:14px 0 4px'>Heat‑Stress Work Practices</h3>
<table border='1' cellpadding='4' cellspacing='0' style='border-collapse:collapse'>
  <thead style='background:#4f81bd;color:#fff'>
    <tr><th>Warning</th><th>HI °F</th><th>Work max</th><th>Hydration</th><th>Work/Rest</th><th>Checks/hr</th></tr>
  </thead><tbody>{policy_html}</tbody>
</table>
"""

# ── 6  send e‑mail ──────────────────────────────────────────────
sg = SendGridAPIClient(SG_KEY)
msg = Mail(
    from_email=EMAIL_FROM,
    to_emails=EMAIL_TO,
    subject=f"John’s WX Brief — {today_str}",
    html_content=html
)
sg.send(msg)
print("HTML weather e‑mail sent.")
