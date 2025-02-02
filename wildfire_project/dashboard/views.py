import os

from django.shortcuts import render
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