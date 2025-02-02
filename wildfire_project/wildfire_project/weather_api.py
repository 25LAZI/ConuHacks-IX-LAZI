import requests

API_KEY = "a8935096c1502ae040183908562c2db2"

GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"


def get_coordinates(city):
    """Fetch latitude and longitude for a given city."""
    params = {"q": city, "appid": API_KEY, "limit": 1}
    response = requests.get(GEOCODE_URL, params=params)

    if response.status_code == 200 and response.json():
        location = response.json()[0]
        return location["lat"], location["lon"]
    else:
        print("Error fetching location. Check city name or API key.")
        return None, None


def get_fire_weather(lat, lon):
    """Fetch fire weather data based on coordinates."""
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"  # Use "imperial" for Fahrenheit
    }
    response = requests.get(WEATHER_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        print("\n🔥 Fire Weather Conditions 🔥")
        print(f"Temperature: {data['main']['temp']}°C")
        print(f"Humidity: {data['main']['humidity']}%")
        print(f"Wind Speed: {data['wind']['speed']} m/s")
        print(f"Weather: {data['weather'][0]['description']}")

        fwi = 0.0272 * data['main']['temp'] + 0.211 * data['main']['humidity'] - 0.7 * data['wind']['speed'] + 2.0

        if fwi > 40:
            print("🔥🚨 HIGH Fire Danger!")
        elif fwi > 20:
            print("⚠️ MODERATE Fire Risk")
        else:
            print("✅ LOW Fire Risk")

    else:
        print("Error fetching weather data.")


if __name__ == "main":
    city_name = input("Enter city name: ")
    lat, lon = get_coordinates(city_name)

    if lat and lon:
        get_fire_weather(lat, lon)
