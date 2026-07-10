from django.urls import path

from core.api import ApplicationCreateApiView, TelegramWebhookApiView
from core import views

urlpatterns = [
    path("", views.home, name="home"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("api/telegram/<str:token>/", TelegramWebhookApiView.as_view(), name="telegram_webhook_api"),
    path("api/pages/<slug:slug>/application/", ApplicationCreateApiView.as_view(), name="application_create_api"),
    path("<slug:slug>/", views.page_detail, name="page_detail"),
]
