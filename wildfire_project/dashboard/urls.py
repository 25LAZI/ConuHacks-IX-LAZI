from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Main dashboard view
    path('test-firebase/', views.test_firebase, name='test_firebase'),
]
