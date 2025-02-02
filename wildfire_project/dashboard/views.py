from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
import pyrebase

# Firebase configuration
config = {
    "apiKey": "AIzaSyBds96dPAAEGuzNKzfZDoIvZacCjmPN67U",
    "authDomain": "wildfire-8b733.firebaseapp.com",
    "databaseURL": "https://wildfire-8b733-default-rtdb.firebaseio.com",
    "projectId": "wildfire-8b733",
    "storageBucket": "wildfire-8b733.firebasestorage.app",
    "messagingSenderId": "1079881094805",
    "appId": "1:1079881094805:web:5faa84ca6a6ec506c02d9c",
}
firebase = pyrebase.initialize_app(config)
database = firebase.database()

# API Key for OpenWeatherMap
API_KEY = "a8935096c1502ae040183908562c2db2"

GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/direct"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def index(request):
    return render(request, 'dashboard/index.html')


def fire_weather(request):
    city = request.GET.get("city", "").strip()
    country = request.GET.get("country", "").strip().upper()

    if not city:
        return redirect("index")

    # Get latitude and longitude of the city
    lat, lon = get_coordinates(city, country)
    if not lat or not lon:
        return render(request, "dashboard/fire_weather.html", {
            "error": "City not found. Please check the input.",
            "city": city,
            "country": country
        })

    # Get weather data based on coordinates
    weather_data = get_weather_data(lat, lon)
    if not weather_data:
        return render(request, "dashboard/fire_weather.html", {
            "error": "Weather data not available.",
            "city": city,
            "country": country
        })

    # Render weather data in the template
    return render(request, "dashboard/fire_weather.html", {
        "city": city,
        "country": country,
        **weather_data
    })


def get_weather_data(lat, lon):
    """Fetch weather data and calculate estimated Fire Weather Index (eFWI)."""
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
    response = requests.get(WEATHER_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        precipitation = data.get("rain", {}).get("1h", 0) + data.get("snow", {}).get("1h", 0)

        # Fire Weather Index Calculation
        eFWI = (temp * wind_speed) / (humidity + precipitation) if (humidity + precipitation) > 0 else temp * wind_speed

        return {
            "temperature": temp,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "precipitation": precipitation,
            "estimated_fwi": round(eFWI, 2),
            "risk_level": "High" if eFWI > 40 else "Moderate" if eFWI > 20 else "Low"
        }
    return None


def get_coordinates(city, country=""):
    """Fetch latitude and longitude for a given city using OpenWeatherMap API."""
    location_query = f"{city},{country}" if country else city
    params = {"q": location_query, "appid": API_KEY, "limit": 1}
    response = requests.get(GEOCODE_URL, params=params)

    if response.status_code == 200 and response.json():
        location = response.json()[0]
        return location["lat"], location["lon"]
    return None, None


def analyzing(request):
    """Render the analyzing page."""
    return render(request, 'dashboard/analyzing.html')


def city(request):
    """Render the city page."""
    return render(request, 'dashboard/city.html')


def test_firebase(request):
    """Test Firebase connection by pushing and retrieving data."""
    # Write data to Firebase
    data = {"name": "Test User", "email": "testuser@example.com"}
    database.child("users").push(data)

    # Read data from Firebase
    users = database.child("users").get().val()

    return HttpResponse(f"Users in database: {users}")
