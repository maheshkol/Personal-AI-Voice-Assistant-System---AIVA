import sys
sys.path.insert(0, r"E:\Personal AI Voice Assistant System - AIVA\aiva\src")

from aiva.tools.weather import WeatherTool
from aiva.tools.wikipedia_tool import WikipediaTool

# ── Weather Tests ──────────────────────────────────────
print("=== Weather Tool Tests ===\n")
weather = WeatherTool()

# Test English
print("--- Nagpur Weather (English) ---")
result = weather.get_weather_for_aiva("Nagpur", language="en")
print(result)

# Test Hindi
print("\n--- Mumbai Weather (Hindi) ---")
result = weather.get_weather_for_aiva("Mumbai", language="hi")
print(result)

# Test Marathi
print("\n--- Pune Weather (Marathi) ---")
result = weather.get_weather_for_aiva("Pune", language="mr")
print(result)

# ── Wikipedia Tests ────────────────────────────────────
print("\n=== Wikipedia Tool Tests ===\n")
wiki = WikipediaTool(default_language="en")

# Test English
print("--- Search: Artificial Intelligence (English) ---")
result = wiki.search_for_aiva("Artificial Intelligence", language="en")
print(result)

# Test Hindi Wikipedia
print("\n--- Search: महात्मा गांधी (Hindi) ---")
result = wiki.search_for_aiva("महात्मा गांधी", language="hi")
print(result)

# Test Marathi Wikipedia
print("\n--- Search: छत्रपती शिवाजी महाराज (Marathi) ---")
result = wiki.search_for_aiva("छत्रपती शिवाजी महाराज", language="mr")
print(result)

print("\n✅ All tool tests done!")