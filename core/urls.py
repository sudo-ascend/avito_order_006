from django.urls import path

from core import views

urlpatterns = [
    path("", views.home, name="home"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("<slug:slug>/", views.page_detail, name="page_detail"),
]
