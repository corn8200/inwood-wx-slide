# Inwood Weather Slide

This project sends a daily HTML weather e-mail with the current forecast for Inwood, WV.

## Requirements

- Python 3
- The packages listed in `requirements.txt`
- A valid [SendGrid](https://sendgrid.com/) API key and e-mail configuration

## Installation

1. Install Python dependencies:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

2. Set the required environment variables:

   - `SENDGRID_API_KEY` – your SendGrid API key
   - `EMAIL_FROM` – the sender address
   - `EMAIL_TO` – comma-separated recipient address(es)

   Optional variables include `LATITUDE`, `LONGITUDE`, and `TIMEZONE`.

## Running

Execute the script directly:

```bash
python weather_slide.py
```

The script will fetch the 10‑day forecast, build an HTML e‑mail, and send it using the provided SendGrid credentials.
