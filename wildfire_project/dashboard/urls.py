from django.urls import path
from . import views
from .views import index, fire_weather

urlpatterns = [
    path("", index, name="index"),
    path("fire-weather/", fire_weather, name="fire-weather"),
]
