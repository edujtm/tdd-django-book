from django.urls import path
from lists import api

urlpatterns = [
    path('lists/<int:pk>/', api.get_list, name='api_list')
]
