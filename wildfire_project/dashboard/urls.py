from django.urls import path
from . import views

urlpatterns = [
    path("", index, name="index"),
    path("fire-weather/", fire_weather, name="fire-weather"),
]
