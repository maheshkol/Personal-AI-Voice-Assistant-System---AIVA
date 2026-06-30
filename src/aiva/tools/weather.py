import requests


class WeatherTool:
    """
    Weather Tool for AIVA.
    Fetches real-time weather data using Open-Meteo API.
    Completely FREE — no API key required!
    Supports any city in the world including Indian cities.
    """

    # Open-Meteo API endpoints (free, no key needed)
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_URL   = "https://api.open-meteo.com/v1/forecast"

    # Weather condition codes → human readable
    WEATHER_CODES = {
        0:  "Clear sky",
        1:  "Mainly clear",
        2:  "Partly cloudy",
        3:  "Overcast",
        45: "Foggy",
        48: "Icy fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Heavy drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Slight showers",
        81: "Moderate showers",
        82: "Heavy showers",
        95: "Thunderstorm",
        99: "Thunderstorm with hail"
    }

    def __init__(self):
        """Initialize Weather Tool."""
        self.timeout = 10  # Request timeout in seconds
        print("✅ Weather Tool initialized (Open-Meteo — Free, no API key)")

    def get_coordinates(self, city: str) -> dict:
        """
        Get latitude and longitude for a city name.

        Args:
            city: City name e.g. "Nagpur", "Mumbai", "Delhi"

        Returns:
            dict with lat, lon, city_name, country
            or None if city not found
        """
        try:
            params = {
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            }

            response = requests.get(
                self.GEOCODING_URL,
                params=params,
                timeout=self.timeout
            )
            data = response.json()

            if "results" not in data or len(data["results"]) == 0:
                print(f"⚠️  City not found: {city}")
                return None

            result = data["results"][0]

            return {
                "lat":       result["latitude"],
                "lon":       result["longitude"],
                "city_name": result["name"],
                "country":   result.get("country", ""),
                "state":     result.get("admin1", "")
            }

        except Exception as e:
            print(f"❌ Geocoding error: {e}")
            return None

    def get_weather(self, city: str) -> dict:
        """
        Get current weather for a city.

        Args:
            city: City name e.g. "Nagpur", "Pune", "Mumbai"

        Returns:
            dict with weather details
            or None if error
        """
        print(f"🌤️  Fetching weather for: {city}")

        # Step 1 — Get coordinates
        location = self.get_coordinates(city)
        if not location:
            return None

        try:
            # Step 2 — Get weather data
            params = {
                "latitude":        location["lat"],
                "longitude":       location["lon"],
                "current":         [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "weather_code",
                    "wind_speed_10m",
                    "precipitation"
                ],
                "timezone":        "auto",
                "forecast_days":   1
            }

            response = requests.get(
                self.WEATHER_URL,
                params=params,
                timeout=self.timeout
            )
            data = response.json()

            current = data["current"]
            weather_code = current.get("weather_code", 0)
            condition = self.WEATHER_CODES.get(weather_code, "Unknown")

            weather_info = {
                "city":              location["city_name"],
                "state":             location["state"],
                "country":           location["country"],
                "temperature":       current["temperature_2m"],
                "feels_like":        current["apparent_temperature"],
                "humidity":          current["relative_humidity_2m"],
                "wind_speed":        current["wind_speed_10m"],
                "precipitation":     current["precipitation"],
                "condition":         condition,
                "weather_code":      weather_code
            }

            print(f"✅ Weather fetched for {weather_info['city']}")
            return weather_info

        except Exception as e:
            print(f"❌ Weather fetch error: {e}")
            return None

    def format_for_voice(self, weather: dict, language: str = "en") -> str:
        """
        Format weather data into a natural spoken sentence.
        Supports English, Hindi and Marathi.

        Args:
            weather:  Weather dict from get_weather()
            language: "en", "hi", or "mr"

        Returns:
            Natural language string ready for TTS
        """
        if not weather:
            messages = {
                "en": "Sorry, I could not fetch the weather information.",
                "hi": "क्षमा करें, मैं मौसम की जानकारी नहीं ला सकी।",
                "mr": "माफ करा, मला हवामान माहिती मिळवता आली नाही।"
            }
            return messages.get(language, messages["en"])

        city        = weather["city"]
        temp        = weather["temperature"]
        feels_like  = weather["feels_like"]
        humidity    = weather["humidity"]
        condition   = weather["condition"]
        wind        = weather["wind_speed"]

        if language == "hi":
            return (
                f"{city} में अभी मौसम {condition} है। "
                f"तापमान {temp} डिग्री सेल्सियस है, "
                f"और महसूस होता है {feels_like} डिग्री जैसा। "
                f"नमी {humidity} प्रतिशत है "
                f"और हवा की गति {wind} किलोमीटर प्रति घंटा है।"
            )
        elif language == "mr":
            return (
                f"{city} मध्ये सध्या हवामान {condition} आहे। "
                f"तापमान {temp} अंश सेल्सियस आहे, "
                f"आणि {feels_like} अंशांसारखे वाटते। "
                f"आर्द्रता {humidity} टक्के आहे "
                f"आणि वाऱ्याचा वेग {wind} किलोमीटर प्रति तास आहे।"
            )
        else:
            return (
                f"The weather in {city} is currently {condition}. "
                f"The temperature is {temp} degrees Celsius, "
                f"and it feels like {feels_like} degrees. "
                f"Humidity is {humidity} percent "
                f"and wind speed is {wind} kilometers per hour."
            )

    def get_weather_for_aiva(self, city: str, language: str = "en") -> str:
        """
        Main method called by AIVA conversation loop.
        Returns a ready-to-speak weather string.

        Args:
            city:     City name
            language: Current language code

        Returns:
            Voice-ready weather string
        """
        weather = self.get_weather(city)
        return self.format_for_voice(weather, language)