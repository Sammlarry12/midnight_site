# core/urls.py
from django.urls import path
from .views import home, page, wallet_submit
from django.urls import include
from . import views

urlpatterns = [
    path("", home, name="home"),
    path("page/", page, name="page"),
    path("api/wallet/submit/", wallet_submit, name="wallet_submit"),
]


