from __future__ import annotations

from django import forms

from core.models import Application, Page, Service
from core.utils import clean_phone_number, format_phone_display


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
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Кратко опишите задачу",
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

        if page:
            self.fields["service"].queryset = page.services.all()

        self.fields["name"].label = "Ваше имя"
        self.fields["phone"].label = "Ваш телефон"

        if page and not self.is_bound:
            first_service = page.services.order_by("order", "pk").first()
            if first_service:
                self.initial.setdefault("service", first_service.pk)

    def clean_phone(self) -> str:
        phone = clean_phone_number(self.cleaned_data["phone"])
        if not phone:
            raise forms.ValidationError("Укажите телефон в формате +7XXXXXXXXXX.")
        return format_phone_display(phone)

    def clean_service(self) -> Service:
        service = self.cleaned_data["service"]
        if self.page and service.page_id != self.page.id:
            raise forms.ValidationError("Услуга выбрана неверно.")
        return service

    def save(self, commit: bool = True) -> Application:
        application = super().save(commit=False)
        if self.page:
            application.page = self.page

        if commit:
            application.save()
            self.save_m2m()

        return application
