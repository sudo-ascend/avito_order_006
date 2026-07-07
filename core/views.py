from __future__ import annotations

from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse

from core.default_pages import ensure_default_page, ensure_default_pages
from core.forms import ApplicationForm
from core.models import Page, SiteSettings
from core.utils import notify_application


def get_page_template(slug: str) -> str:
    template_name = f"pages/{slug}.html"
    try:
        get_template(template_name)
    except TemplateDoesNotExist as exc:
        raise Http404("Страница не найдена") from exc
    return template_name


def home(request):
    ensure_default_pages()
    pages = Page.objects.filter(is_active=True).only(
        "slug",
        "name",
        "subtitle",
        "hero_image",
        "hero_image_alt",
    )
    return render(
        request,
        "home.html",
        {
            "pages": pages,
            "body_class": "page page--home",
        },
    )


def page_detail(request, slug: str):
    template_name = get_page_template(slug)
    ensure_default_page(slug)

    queryset = Page.objects.prefetch_related(
        "services",
        "advantage_group__advantages",
        "work_examples",
        "steps",
        "equipment",
    )
    page = get_object_or_404(queryset, slug=slug, is_active=True)

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES, page=page)
        if form.is_valid():
            application = form.save()
            notify_application(application, SiteSettings.objects.first())
            messages.success(request, "Спасибо! Заявка отправлена, мы скоро свяжемся с вами.")
            return redirect(f"{page.get_absolute_url()}?sent=ok")
    else:
        form = ApplicationForm(page=page)

    return render(
        request,
        template_name,
        {
            "page": page,
            "form": form,
            "body_class": "page page--service",
            "sent_ok": request.GET.get("sent") == "ok",
        },
    )


def robots_txt(request):
    sitemap_url = request.build_absolute_uri(reverse("sitemap"))
    content = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            f"Sitemap: {sitemap_url}",
        ]
    )
    return HttpResponse(content, content_type="text/plain; charset=utf-8")


def error_400(request, exception):
    return render(request, "400.html", status=400)


def error_403(request, exception):
    return render(request, "403.html", status=403)


def error_404(request, exception):
    return render(request, "404.html", status=404)


def error_500(request):
    return render(request, "500.html", status=500)


def csrf_failure(request, reason=""):
    return render(request, "403_csrf.html", status=403)
