from django.urls import path
from . import views

urlpatterns = [
    path('', views.diode_view, name='diode_home'), 
    path("diode/constants", views.diode_constants, name="diode_constants"),
    path("calculate/", views.calculate, name="calculate"),
    
]

