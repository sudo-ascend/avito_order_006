from __future__ import annotations

import logging
import re

import requests
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def clean_phone_number(raw_phone: str) -> str | None:
    digits = re.sub(r"\D+", "", raw_phone or "")
    if digits.startswith("8"):
        digits = f"7{digits[1:]}"
    elif len(digits) == 10:
        digits = f"7{digits}"

    if len(digits) != 11 or not digits.startswith("7"):
        return None
    return f"+{digits}"


def format_phone_display(phone: str) -> str:
    digits = re.sub(r"\D+", "", phone)
    if len(digits) != 11:
        return phone
    return f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"


def phone_href(phone: str) -> str:
    digits = re.sub(r"\D+", "", phone or "")
    return f"tel:+{digits}" if digits else "tel:"


def build_application_message(application) -> str:
    parts = [
        "Новая заявка с сайта",
        f"Имя: {application.name}",
        f"Телефон: {application.phone}",
        f"Услуга: {application.service_title}",
        f"Страница: {application.page_slug}",
        f"Время: {application.created_at:%d.%m.%Y %H:%M}",
    ]
    if application.comment:
        parts.append(f"Комментарий: {application.comment}")
    return "\n".join(parts)


def send_application_email(application, recipient_email: str) -> None:
    send_mail(
        subject="Новая заявка с сайта",
        message=build_application_message(application),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        fail_silently=False,
    )


def send_telegram_message(text: str, chat_id: str | None = None) -> bool:
    token = settings.TELEGRAM_BOT_TOKEN
    actual_chat_id = chat_id or settings.TELEGRAM_CHAT_ID
    if not token or not actual_chat_id:
        return False

    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={
            "chat_id": actual_chat_id,
            "text": text,
        },
        timeout=10,
    )
    response.raise_for_status()
    return True


def notify_application(application, site_settings=None) -> dict[str, bool]:
    recipient_email = getattr(site_settings, "application_email", "") or settings.APPLICATION_NOTIFICATION_EMAIL
    chat_id = getattr(site_settings, "telegram_chat_id", "") or settings.TELEGRAM_CHAT_ID

    result = {"email": False, "telegram": False}

    try:
        if recipient_email:
            send_application_email(application, recipient_email)
            result["email"] = True
    except Exception:
        logger.exception("Не удалось отправить email по заявке %s", application.pk)

    try:
        result["telegram"] = send_telegram_message(build_application_message(application), chat_id)
    except Exception:
        logger.exception("Не удалось отправить Telegram по заявке %s", application.pk)

    return result
