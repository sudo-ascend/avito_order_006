from __future__ import annotations

import logging

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.forms import ApplicationForm
from core.models import Page, SiteSettings
from core.utils import (
    TELEGRAM_SUBSCRIBED_MESSAGE,
    TELEGRAM_UNSUBSCRIBED_MESSAGE,
    notify_application,
    send_telegram_message,
    upsert_telegram_subscriber,
)

logger = logging.getLogger(__name__)


class ApplicationResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField()
    message = serializers.CharField()
    errors = serializers.DictField(child=serializers.ListField(child=serializers.CharField()), required=False)


class ApplicationCreateApiView(APIView):
    def post(self, request, slug: str) -> Response:
        page = get_object_or_404(Page.objects.filter(is_active=True), slug=slug)
        form = ApplicationForm(request.data, page=page)

        if not form.is_valid():
            errors = {
                field_name: [item["message"] for item in items]
                for field_name, items in form.errors.get_json_data(escape_html=True).items()
            }
            serializer = ApplicationResponseSerializer(
                {
                    "ok": False,
                    "message": "Пожалуйста, проверьте форму.",
                    "errors": errors,
                }
            )
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

        application = form.save()
        notify_application(application, SiteSettings.objects.first())
        serializer = ApplicationResponseSerializer(
            {
                "ok": True,
                "message": "Спасибо! Заявка отправлена, мы скоро свяжемся с вами.",
            }
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TelegramWebhookApiView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, token: str) -> Response:
        if not settings.TELEGRAM_BOT_TOKEN or token != settings.TELEGRAM_BOT_TOKEN:
            return Response(status=status.HTTP_404_NOT_FOUND)

        message = request.data.get("message") or request.data.get("edited_message") or {}
        chat_data = message.get("chat") or {}
        text = (message.get("text") or "").strip()

        if text.startswith("/start"):
            subscriber = upsert_telegram_subscriber(chat_data, is_active=True)
            if subscriber:
                try:
                    send_telegram_message(TELEGRAM_SUBSCRIBED_MESSAGE, subscriber.chat_id)
                except Exception:
                    logger.exception("Не удалось отправить подтверждение подписки в Telegram %s", subscriber.chat_id)
        elif text.startswith("/stop"):
            subscriber = upsert_telegram_subscriber(chat_data, is_active=False)
            if subscriber:
                try:
                    send_telegram_message(TELEGRAM_UNSUBSCRIBED_MESSAGE, subscriber.chat_id)
                except Exception:
                    logger.exception("Не удалось отправить подтверждение отписки в Telegram %s", subscriber.chat_id)

        return Response({"ok": True})
