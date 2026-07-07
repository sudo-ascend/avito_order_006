from unittest.mock import patch

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from core.models import AdvantageGroup, Application, Page, Service, SiteSettings


class PageViewTests(TestCase):
    def setUp(self):
        SiteSettings.objects.create(
            phone="+7 921 947 80 89",
            email="molniya@profcleaning-comp.ru",
            address="Санкт-Петербург",
            work_time="Работаем 24/7",
        )
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

    def test_page_detail_is_available(self):
        response = self.client.get(self.page.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.page.h1)

    @patch("core.views.notify_application")
    def test_application_post_creates_record(self, notify_application_mock):
        response = self.client.post(
            self.page.get_absolute_url(),
            data={
                "name": "Иван",
                "phone": "+7 (921) 111-22-33",
                "service": self.service.pk,
                "comment": "Нужен срочный выезд",
            },
        )

        self.assertEqual(Application.objects.count(), 1)
        application = Application.objects.get()
        self.assertEqual(application.page, self.page)
        self.assertEqual(application.service, self.service)
        self.assertEqual(application.page_slug, self.page.slug)
        self.assertRedirects(response, f"{self.page.get_absolute_url()}?sent=ok", fetch_redirect_response=False)
        notify_application_mock.assert_called_once()

    def test_robots_txt_is_available(self):
        response = self.client.get(reverse("robots_txt"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User-agent: *")


class DefaultPageBootstrapTests(TestCase):
    def setUp(self):
        SiteSettings.objects.create(
            phone="+7 921 947 80 89",
            email="molniya@profcleaning-comp.ru",
            address="Санкт-Петербург",
            work_time="Работаем 24/7",
        )

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

    def test_bootstrap_reuses_shared_advantage_groups(self):
        self.client.get(reverse("home"))

        pages = Page.objects.filter(
            slug__in=["uborka-posle-potopa", "uborka-posle-pozhara", "b2b-cleaning"]
        ).order_by("slug")

        group_ids = {page.advantage_group_id for page in pages}
        self.assertEqual(len(group_ids), 1)
        self.assertEqual(AdvantageGroup.objects.count(), 5)


class ErrorPageTests(TestCase):
    def setUp(self):
        SiteSettings.objects.create(
            phone="+7 921 947 80 89",
            email="molniya@profcleaning-comp.ru",
            address="Санкт-Петербург",
            work_time="Работаем 24/7",
        )

    @override_settings(DEBUG=False)
    def test_404_uses_custom_template(self):
        response = self.client.get("/stranitsa-kotoroy-net/")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
        self.assertContains(response, "Страница не найдена", status_code=404)

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
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403_csrf.html")
        self.assertContains(response, "Сессия формы истекла", status_code=403)
