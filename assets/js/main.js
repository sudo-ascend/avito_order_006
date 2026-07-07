(function () {
  const body = document.body;
  const toggle = document.querySelector(".menu-toggle, .nav-toggle");
  const menu = document.querySelector("#mobile-menu");

  function closeMenu() {
    if (!toggle || !menu) return;
    toggle.setAttribute("aria-expanded", "false");
    menu.hidden = true;
    body.classList.remove("menu-open");
  }

  if (toggle && menu) {
    closeMenu();

    toggle.addEventListener("click", () => {
      const isOpen = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!isOpen));
      menu.hidden = isOpen;
      body.classList.toggle("menu-open", !isOpen);
    });

    menu.addEventListener("click", (event) => {
      if (event.target.closest("a")) {
        closeMenu();
      }
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeMenu();
      }
    });
  }

  document.querySelectorAll('a[href^="#"], a[href="/#contact"]').forEach((link) => {
    link.addEventListener("click", (event) => {
      const href = link.getAttribute("href");
      const targetId = href === "/#contact" ? "contact" : href.slice(1);
      const target = document.getElementById(targetId);
      if (!target) return;
      event.preventDefault();
      closeMenu();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  document.querySelectorAll("[data-scroll-button]").forEach((button) => {
    button.addEventListener("click", () => {
      const section = button.closest(".works-section");
      const rail = section && section.querySelector("[data-scroll-rail]");
      if (!rail) return;
      const direction = button.dataset.scrollButton === "prev" ? -1 : 1;
      rail.scrollBy({ left: direction * Math.max(280, rail.clientWidth * 0.82), behavior: "smooth" });
    });
  });

  function normalizePhone(input) {
    let digits = input.value.replace(/\D/g, "");
    if (digits.startsWith("8")) digits = `7${digits.slice(1)}`;
    if (!digits.startsWith("7")) digits = `7${digits}`;
    digits = digits.slice(0, 11);
    const parts = [
      digits.slice(1, 4),
      digits.slice(4, 7),
      digits.slice(7, 9),
      digits.slice(9, 11)
    ];
    let value = "+7";
    if (parts[0]) value += ` (${parts[0]}`;
    if (parts[0].length === 3) value += ")";
    if (parts[1]) value += ` ${parts[1]}`;
    if (parts[2]) value += `-${parts[2]}`;
    if (parts[3]) value += `-${parts[3]}`;
    input.value = value;
  }

  document.querySelectorAll('input[name="phone"]').forEach((input) => {
    input.addEventListener("focus", () => {
      if (!input.value.trim()) input.value = "+7 ";
    });
    input.addEventListener("input", () => normalizePhone(input));
  });

  document.querySelectorAll("[data-form]").forEach((form) => {
    const nameInput = form.querySelector('input[name="name"]');
    const phoneInput = form.querySelector('input[name="phone"]');
    const message = form.querySelector(".form-message");

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const nameValid = nameInput.value.trim().length > 1;
      const phoneDigits = phoneInput.value.replace(/\D/g, "");
      const phoneValid = phoneDigits.length === 11 && phoneDigits.startsWith("7");

      nameInput.classList.toggle("is-invalid", !nameValid);
      phoneInput.classList.toggle("is-invalid", !phoneValid);

      if (!nameValid || !phoneValid) {
        message.textContent = "Заполните имя и телефон в формате +7.";
        message.style.color = "#ffb1b1";
        return;
      }

      // Connect email, CRM, or Telegram submission here.
      const payload = Object.fromEntries(new FormData(form).entries());
      console.info("Form payload ready for integration", payload);
      message.textContent = "Спасибо! Заявка отправлена. Мы свяжемся с вами в ближайшее время.";
      message.style.color = "#a2c62c";
      form.reset();
    });
  });
})();
