from django.urls import path
from .views import index, fire_weather, analyzing, city

urlpatterns = [
    path("", index, name="index"),
    path("fire-weather/", fire_weather, name="fire-weather"),
    path("analyzing/", analyzing, name="analyzing"),
    path("city/", city, name="city"),
]
