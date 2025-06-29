from django.urls import path
from .views import random_quote_view

app_name = 'quotes'

urlpatterns = [
    path('', random_quote_view, name='random_quote'),
]