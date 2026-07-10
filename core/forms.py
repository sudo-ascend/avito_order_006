from __future__ import annotations

import re

from django import forms

from core.models import Application, Page, Service
from core.utils import clean_phone_number, format_phone_display

LINK_RE = re.compile(r"(https?://|www\.|t\.me/)", re.IGNORECASE)
NAME_MAX_LENGTH = 80
COMMENT_MAX_LENGTH = 1000


class ApplicationForm(forms.ModelForm):
    service = forms.ModelChoiceField(
        label="Услуга",
        widget=forms.RadioSelect,
        queryset=Service.objects.none(),
        empty_label=None,
    )
    comment = forms.CharField(
        label="Комментарий",
        required=False,
        max_length=COMMENT_MAX_LENGTH,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "maxlength": str(COMMENT_MAX_LENGTH),
                "placeholder": "Кратко опишите задачу",
            }
        ),
    )
    consent = forms.BooleanField(
        label="Согласен на обработку персональных данных",
        required=True,
        error_messages={"required": "Подтвердите согласие на обработку персональных данных."},
    )
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(
            attrs={
                "tabindex": "-1",
                "autocomplete": "off",
                "aria-hidden": "true",
            }
        ),
    )

    class Meta:
        model = Application
        fields = ("name", "phone", "service", "comment")
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "autocomplete": "name",
                    "maxlength": str(NAME_MAX_LENGTH),
                    "minlength": "2",
                    "placeholder": "Ваше имя",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "autocomplete": "tel",
                    "inputmode": "tel",
                    "placeholder": "+7 (___) ___-__-__",
                }
            ),
        }

    def __init__(self, *args, page: Page | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = page
        self.fields["name"].label = "Ваше имя"
        self.fields["phone"].label = "Ваш телефон"

        page_services = []
        for item in Page.objects.filter(is_active=True).order_by("pk"):
            service = item.services.order_by("order", "pk").first()
            if service:
                page_services.append(service.pk)

        self.fields["service"].queryset = Service.objects.select_related("page").filter(pk__in=page_services).order_by("page__pk")
        self.fields["service"].label_from_instance = lambda service: service.page.name

        if page and not self.is_bound:
            first_service = page.services.order_by("order", "pk").first()
            if first_service:
                self.initial.setdefault("service", first_service.pk)

    def clean_name(self) -> str:
        name = " ".join((self.cleaned_data.get("name") or "").split())
        letters_count = sum(char.isalpha() for char in name)
        digits_count = sum(char.isdigit() for char in name)

        if len(name) < 2:
            raise forms.ValidationError("Укажите имя не короче 2 символов.")
        if len(name) > NAME_MAX_LENGTH:
            raise forms.ValidationError(f"Имя должно быть не длиннее {NAME_MAX_LENGTH} символов.")
        if letters_count < 2:
            raise forms.ValidationError("Укажите реальное имя.")
        if digits_count > 3 or LINK_RE.search(name):
            raise forms.ValidationError("Имя заполнено некорректно.")

        return name

    def clean_phone(self) -> str:
        phone = clean_phone_number(self.cleaned_data["phone"])
        if not phone:
            raise forms.ValidationError("Укажите телефон в формате +7XXXXXXXXXX.")
        return format_phone_display(phone)

    def clean_comment(self) -> str:
        comment = (self.cleaned_data.get("comment") or "").strip()
        if LINK_RE.search(comment):
            raise forms.ValidationError("Ссылки в комментарии запрещены.")
        return comment

    def clean_website(self) -> str:
        value = (self.cleaned_data.get("website") or "").strip()
        if value:
            raise forms.ValidationError("Не удалось отправить заявку.")
        return value

    def save(self, commit: bool = True) -> Application:
        application = super().save(commit=False)
        if self.page:
            application.page = self.page

        if commit:
            application.save()
            self.save_m2m()

        return application
