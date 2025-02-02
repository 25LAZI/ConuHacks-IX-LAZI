from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Main dashboard view
    path('analyzing/', views.analyzing, name='analyzing'),
    path('city/', views.city, name='city'),

    path('test-firebase/', views.test_firebase, name='test_firebase'),
]
