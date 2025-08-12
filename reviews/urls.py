from django.urls import path
from . import views

urlpatterns = [
    path('', views.reviews_section, name='reviews_section'),
]
