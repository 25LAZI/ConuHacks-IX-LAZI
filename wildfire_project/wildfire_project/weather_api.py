import requests

API_KEY = "a8935096c1502ae040183908562c2db2"

GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/direct"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

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

def get_weather_data(lat, lon):
    """Fetch weather data and calculate estimated Fire Weather Index (eFWI)."""
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    }
    response = requests.get(WEATHER_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        precipitation = data.get("rain", {}).get("1h", 0) + data.get("snow", {}).get("1h", 0)

        # Simplified Fire Weather Index formula
        if humidity + precipitation > 0:
            eFWI = (temp * wind_speed) / (humidity + precipitation)
        else:
            eFWI = temp * wind_speed  # Avoid division by zero

        print("\n🔥 Estimated Fire Weather Index (eFWI) 🔥")
        print(f"Temperature: {temp}°C")
        print(f"Humidity: {humidity}%")
        print(f"Wind Speed: {wind_speed} m/s")
        print(f"Precipitation: {precipitation} mm")
        print(f"Estimated Fire Weather Index: {round(eFWI, 2)}")

        # Risk Level (Basic Interpretation)
        if eFWI > 40:
            print("🔥🚨 HIGH Fire Danger!")
        elif eFWI > 20:
            print("⚠️ MODERATE Fire Risk")
        else:
            print("✅ LOW Fire Risk")

    else:
        print("Error fetching weather data.")

if __name__ == "__main__":
    city_name = input("Enter city name: ")
    lat, lon = get_coordinates(city_name)

    if lat and lon:
        get_weather_data(lat, lon)
