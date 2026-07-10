import json
from unittest.mock import patch

from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from core.models import AdvantageGroup, Application, Page, Service, SiteSettings, TelegramSubscriber
from core.utils import notify_application


class BaseSiteTestCase(TestCase):
    def setUp(self):
        SiteSettings.objects.create(
            phone="+7 921 947 80 89",
            telegram_username="FoodMood2024",
            whatsapp_phone="89669318089",
            email="molniya@profcleaning-comp.ru",
            address="Санкт-Петербург",
            work_time="Работаем 24/7",
        )


class PageViewTests(BaseSiteTestCase):
    def setUp(self):
        super().setUp()
        self.page = Page.objects.create(
            slug="uborka-posle-potopa",
            name="Уборка после потопа",
            h1="Уборка после потопа",
            subtitle="Тестовая страница",
            guarantee_text="Тестовая гарантия",
            guarantee_items="Работаем по договору",
        )
        self.service = Service.objects.create(
            page=self.page,
            title="Тестовая услуга",
            description="Тестовое описание",
        )

    def test_home_is_available(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/uborka-posle-potopa/")
        self.assertContains(response, "/static/css/style.css")
        self.assertNotContains(response, "/assets/css/style.css")
        self.assertContains(response, '<footer class="footer">')

    def test_page_detail_is_available(self):
        response = self.client.get(self.page.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.page.h1)
        self.assertNotContains(response, '<footer class="footer">')

    def test_page_detail_uses_only_seo_title_for_head_title(self):
        response = self.client.get(self.page.get_absolute_url())

        self.assertContains(response, "<title>Молния-Клининг</title>", html=True)
        self.assertNotContains(response, f"<title>{self.page.h1}</title>", html=True)

    def test_page_detail_renders_explicit_seo_title_in_head(self):
        self.page.seo_title = "SEO заголовок страницы"
        self.page.save(update_fields=["seo_title"])

        response = self.client.get(self.page.get_absolute_url())

        self.assertContains(response, "<title>SEO заголовок страницы</title>", html=True)

    @patch("core.api.notify_application")
    def test_application_api_creates_record(self, notify_application_mock):
        response = self.client.post(
            reverse("application_create_api", kwargs={"slug": self.page.slug}),
            data={
                "name": "Иван",
                "phone": "+7 (921) 111-22-33",
                "service": self.service.pk,
                "comment": "Нужен срочный выезд",
                "consent": "on",
                "website": "",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Application.objects.count(), 1)

        application = Application.objects.get()
        self.assertEqual(application.page, self.page)
        self.assertEqual(application.service, self.service)
        self.assertEqual(application.page_slug, self.page.slug)
        self.assertTrue(response.json()["ok"])
        notify_application_mock.assert_called_once()

    def test_robots_txt_is_available(self):
        response = self.client.get(reverse("robots_txt"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User-agent: *")


class DefaultPageBootstrapTests(BaseSiteTestCase):
    def test_home_seeds_default_pages_when_database_is_empty(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Page.objects.count(), 7)

    def test_page_detail_bootstraps_known_default_page(self):
        response = self.client.get(reverse("page_detail", kwargs={"slug": "uborka-posle-potopa"}))

        page = Page.objects.get(slug="uborka-posle-potopa")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, page.h1)
        self.assertEqual(Page.objects.count(), 7)
        self.assertTrue(page.services.exists())
        self.assertTrue(page.advantages.exists())
        self.assertTrue(page.steps.exists())

    def test_bootstrap_creates_separate_advantage_groups_for_pages(self):
        self.client.get(reverse("home"))

        pages = Page.objects.filter(
            slug__in=["uborka-posle-potopa", "uborka-posle-pozhara", "b2b-cleaning"]
        ).order_by("slug")

        group_ids = {page.advantage_group_id for page in pages}
        self.assertEqual(len(group_ids), 3)
        self.assertEqual(AdvantageGroup.objects.count(), Page.objects.count())


class ErrorPageTests(BaseSiteTestCase):
    @override_settings(DEBUG=False)
    def test_404_uses_custom_template(self):
        response = self.client.get("/stranitsa-kotoroy-net/")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "error_pages/404.html")

    def test_csrf_failure_uses_custom_template(self):
        page = Page.objects.create(
            slug="test-service",
            name="Тестовая услуга",
            h1="Тестовая услуга",
            subtitle="Тест",
            guarantee_text="Гарантия",
            guarantee_items="Работаем по договору",
        )
        service = Service.objects.create(
            page=page,
            title="Тестовая услуга",
            description="Тест",
        )
        csrf_client = Client(enforce_csrf_checks=True)

        response = csrf_client.post(
            page.get_absolute_url(),
            data={
                "name": "Иван",
                "phone": "+7 (921) 111-22-33",
                "service": service.pk,
                "comment": "Проверка страницы ошибки",
                "consent": "on",
                "website": "",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "error_pages/403_csrf.html")


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    APPLICATION_NOTIFICATION_EMAIL="notify@example.com",
    TELEGRAM_BOT_TOKEN="",
    TELEGRAM_CHAT_ID="",
)
class NotificationTests(BaseSiteTestCase):
    def test_notify_application_sends_html_email(self):
        page = Page.objects.create(
            slug="test-email-page",
            name="Тестовая страница",
            h1="Тестовая страница",
        )
        service = Service.objects.create(
            page=page,
            title="Тестовая услуга",
        )
        application = Application.objects.create(
            name="Иван",
            phone="+7 (921) 111-22-33",
            page=page,
            service=service,
            comment="Нужен выезд сегодня",
        )

        result = notify_application(application, SiteSettings.objects.first())

        self.assertTrue(result["email"])
        self.assertFalse(result["telegram"])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Новая заявка с сайта")
        self.assertIn("Иван", mail.outbox[0].body)
        self.assertEqual(len(mail.outbox[0].alternatives), 1)
        html_body, mimetype = mail.outbox[0].alternatives[0]
        self.assertEqual(mimetype, "text/html")
        self.assertIn("Новая заявка с сайта", html_body)
        self.assertIn("Тестовая услуга", html_body)

    @override_settings(
        TELEGRAM_BOT_TOKEN="test-bot-token",
        TELEGRAM_CHAT_ID="123456",
    )
    @patch("core.utils.requests.post")
    def test_notify_application_sends_html_telegram_message_with_copyable_phone(self, requests_post_mock):
        page = Page.objects.create(
            slug="test-telegram-page",
            name="Тестовая страница",
            h1="Тестовая страница",
        )
        service = Service.objects.create(
            page=page,
            title="Тестовая услуга",
        )
        application = Application.objects.create(
            name="Иван",
            phone="8 (921) 111-22-33",
            page=page,
            service=service,
            comment="Позвоните перед выездом",
        )

        result = notify_application(application, SiteSettings.objects.first())

        self.assertTrue(result["telegram"])
        requests_post_mock.assert_called_once()
        self.assertEqual(
            requests_post_mock.call_args.kwargs["data"],
            {
                "chat_id": "123456",
                "text": (
                    "<b>Новая заявка с сайта</b>\n"
                    "<b>Имя:</b> Иван\n"
                    "<b>Телефон:</b> <code>+79211112233</code>\n"
                    "<b>Услуга:</b> Тестовая услуга\n"
                    "<b>Страница:</b> test-telegram-page\n"
                    f"<b>Время:</b> {application.created_at:%d.%m.%Y %H:%M}\n"
                    "<b>Комментарий:</b> Позвоните перед выездом"
                ),
                "parse_mode": "HTML",
                "disable_web_page_preview": "true",
            },
        )

    @override_settings(
        TELEGRAM_BOT_TOKEN="test-bot-token",
        TELEGRAM_CHAT_ID="legacy-chat-id",
    )
    @patch("core.utils.requests.post")
    def test_notify_application_sends_to_all_active_telegram_subscribers(self, requests_post_mock):
        TelegramSubscriber.objects.create(chat_id="111", username="first", is_active=True)
        TelegramSubscriber.objects.create(chat_id="222", username="second", is_active=True)
        TelegramSubscriber.objects.create(chat_id="333", username="inactive", is_active=False)
        page = Page.objects.create(
            slug="telegram-broadcast-page",
            name="Тестовая страница",
            h1="Тестовая страница",
        )
        service = Service.objects.create(
            page=page,
            title="Тестовая услуга",
        )
        application = Application.objects.create(
            name="Иван",
            phone="+7 (921) 111-22-33",
            page=page,
            service=service,
        )

        result = notify_application(application, SiteSettings.objects.first())

        self.assertTrue(result["telegram"])
        self.assertEqual(requests_post_mock.call_count, 2)
        chat_ids = sorted(call.kwargs["data"]["chat_id"] for call in requests_post_mock.call_args_list)
        self.assertEqual(chat_ids, ["111", "222"])


@override_settings(
    TELEGRAM_BOT_TOKEN="test-bot-token",
    TELEGRAM_CHAT_ID="",
)
class TelegramWebhookTests(BaseSiteTestCase):
    @patch("core.api.send_telegram_message")
    def test_start_subscribes_chat(self, send_telegram_message_mock):
        response = self.client.post(
            reverse("telegram_webhook_api", kwargs={"token": "test-bot-token"}),
            data=json.dumps(
                {
                    "update_id": 1,
                    "message": {
                        "message_id": 10,
                        "text": "/start",
                        "chat": {
                            "id": 123456,
                            "username": "cleaning_admin",
                            "first_name": "Иван",
                            "last_name": "Петров",
                        },
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TelegramSubscriber.objects.count(), 1)
        subscriber = TelegramSubscriber.objects.get()
        self.assertEqual(subscriber.chat_id, "123456")
        self.assertTrue(subscriber.is_active)
        self.assertEqual(subscriber.username, "cleaning_admin")
        send_telegram_message_mock.assert_called_once_with(
            "Вы подписались на уведомления о новых заявках.",
            "123456",
        )

    @patch("core.api.send_telegram_message")
    def test_stop_deactivates_chat(self, send_telegram_message_mock):
        TelegramSubscriber.objects.create(chat_id="123456", username="cleaning_admin", is_active=True)

        response = self.client.post(
            reverse("telegram_webhook_api", kwargs={"token": "test-bot-token"}),
            data=json.dumps(
                {
                    "update_id": 2,
                    "message": {
                        "message_id": 11,
                        "text": "/stop",
                        "chat": {
                            "id": 123456,
                            "username": "cleaning_admin",
                            "first_name": "Иван",
                        },
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(TelegramSubscriber.objects.get(chat_id="123456").is_active)
        send_telegram_message_mock.assert_called_once_with(
            "Вы отписались от уведомлений о новых заявках.",
            "123456",
        )
