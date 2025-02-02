import os
import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse
import pyrebase
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder, StandardScaler

config = {
    "apiKey":"AIzaSyBds96dPAAEGuzNKzfZDoIvZacCjmPN67U",
    "authDomain": "wildfire-8b733.firebaseapp.com",
    "databaseURL": "https://wildfire-8b733-default-rtdb.firebaseio.com",
    "projectId": "wildfire-8b733",
    "storageBucket": "wildfire-8b733.firebasestorage.app",
    "messagingSenderId":  "1079881094805",
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




def index(request):
    # Correct path to access the CSV
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_file_path = os.path.join(BASE_DIR, 'data', 'nasadata.csv')

    # Charger les données CSV
    df = pd.read_csv(csv_file_path)

    # Prétraitement des données
    expected_columns = ["latitude", "longitude", "path", "row", "scan", "track", "acq_date", "acq_time", "satellite", "confidence", "daynight"]
    if not all(col in df.columns for col in expected_columns):
        raise ValueError("Des colonnes sont manquantes dans le fichier CSV!")

    df['acq_time'] = df['acq_time'].astype(str).str.zfill(4)
    df['datetime'] = pd.to_datetime(df['acq_date'] + ' ' + df['acq_time'], format='%Y-%m-%d %H%M')
    df = df[(df['latitude'] >= 44) & (df['latitude'] <= 63) & (df['longitude'] >= -80) & (df['longitude'] <= -57)]

    # Encoder et normaliser les données
    label_encoder = LabelEncoder()
    df['satellite'] = label_encoder.fit_transform(df['satellite'])
    df['confidence'] = df['confidence'].map({'L': 0, 'M': 1, 'H': 2})
    df.dropna(inplace=True)

    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df[['latitude', 'longitude', 'path', 'row', 'scan', 'track', 'satellite']])
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(df_scaled)

    # Créer la carte Folium
    m = folium.Map(location=[52.9399, -71.6501], zoom_start=6)
    marker_cluster = MarkerCluster().add_to(m)
    cluster_colors = {0: 'blue', 1: 'green', 2: 'red'}

    for index, row in df.iterrows():
        cluster = int(row['cluster'])
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=(f"Cluster: {cluster}<br>"
                   f"Confiance: {row['confidence']}<br>"
                   f"Satellite: {row['satellite']}<br>"
                   f"Date: {row['datetime']}"),
            icon=folium.Icon(color=cluster_colors[cluster])
        ).add_to(marker_cluster)

    # Convertir la carte en HTML
    map_html = m._repr_html_()

    # Renvoyer la carte à la vue
    return render(request, 'dashboard/index.html', {'map_html': map_html})
