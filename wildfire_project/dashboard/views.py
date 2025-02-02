from django.shortcuts import render
from django.http import HttpResponse
import pyrebase

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
    return render(request, 'dashboard/index.html')

def analyzing(request):
    return render(request, 'dashboard/analyzing.html')

def city(request):
    search_query = request.GET.get('search', '')
    return render(request, 'dashboard/city.html', {'search_query': search_query})
def test_firebase(request):
    # Write data to Firebase
    data = {"name": "Test User", "email": "testuser@example.com"}
    database.child("users").push(data)

    # Read data from Firebase
    users = database.child("users").get().val()

    return HttpResponse(f"Users in database: {users}")