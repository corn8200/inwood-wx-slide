import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from weather_slide import build_html


def test_build_html_basic():
    daily = {
        "apparent_temperature_max": [95],
        "time": ["2025-07-14"],
        "temperature_2m_max": [90],
        "temperature_2m_min": [70],
        "weathercode": [0],
        "precipitation_probability_max": [10],
    }
    html = build_html(daily, "2025-07-14")
    assert "Inwood Weather" in html
    assert "95 °F" in html
    assert "<tr><td>2025-07-14</td><td>90°</td><td>70°</td>" in html
