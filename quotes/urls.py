from django.urls import path
from .views import random_quote_view, like_quote, dislike_quote, dashboard_view

app_name = "quotes"

urlpatterns = [
    path("", random_quote_view, name="random_quote"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("quote/<int:quote_id>/like/", like_quote, name="like_quote"),
    path("quote/<int:quote_id>/dislike/", dislike_quote, name="dislike_quote"),
]
