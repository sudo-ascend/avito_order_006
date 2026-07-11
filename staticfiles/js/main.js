(function () {
  const body = document.body;
  const toggle = document.querySelector(".menu-toggle, .nav-toggle");
  const menu = document.querySelector("#mobile-menu");
  const mobileServicesToggle = document.querySelector("[data-mobile-services-toggle]");
  const mobileServicesMenu = document.querySelector("#mobile-services-menu");
  const desktopHeaderMedia = window.matchMedia("(min-width: 1121px)");
  const successPopup = document.querySelector("[data-success-popup]");
  const successPopupDialog = successPopup && successPopup.querySelector("[data-success-popup-dialog]");
  const successPopupMessage = successPopup && successPopup.querySelector("[data-success-popup-message]");
  let successPopupReturnFocus = null;

  function closeMobileServicesMenu() {
    if (!mobileServicesToggle || !mobileServicesMenu) return;
    mobileServicesToggle.setAttribute("aria-expanded", "false");
    mobileServicesMenu.hidden = true;
  }

  function closeMenu() {
    if (!toggle || !menu) return;
    toggle.setAttribute("aria-expanded", "false");
    menu.hidden = true;
    body.classList.remove("menu-open");
    closeMobileServicesMenu();
  }

  function closeSuccessPopup() {
    if (!successPopup || successPopup.hidden) return;
    successPopup.hidden = true;
    body.classList.remove("popup-open");

    if (successPopupReturnFocus && typeof successPopupReturnFocus.focus === "function") {
      successPopupReturnFocus.focus();
    }
  }

  function openSuccessPopup(message, trigger) {
    if (!successPopup || !successPopupDialog) return;
    successPopupReturnFocus = trigger || null;

    if (successPopupMessage && message) {
      successPopupMessage.textContent = message;
    }

    successPopup.hidden = false;
    body.classList.add("popup-open");
    window.requestAnimationFrame(() => successPopupDialog.focus());
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
  }

  if (mobileServicesToggle && mobileServicesMenu) {
    closeMobileServicesMenu();

    mobileServicesToggle.addEventListener("click", () => {
      const isOpen = mobileServicesToggle.getAttribute("aria-expanded") === "true";
      mobileServicesToggle.setAttribute("aria-expanded", String(!isOpen));
      mobileServicesMenu.hidden = isOpen;
    });
  }

  function syncMenuWithViewport() {
    if (desktopHeaderMedia.matches) {
      closeMenu();
    }
  }

  window.addEventListener("resize", syncMenuWithViewport);

  if (typeof desktopHeaderMedia.addEventListener === "function") {
    desktopHeaderMedia.addEventListener("change", syncMenuWithViewport);
  } else if (typeof desktopHeaderMedia.addListener === "function") {
    desktopHeaderMedia.addListener(syncMenuWithViewport);
  }

  if (successPopup) {
    successPopup.addEventListener("click", (event) => {
      if (event.target === successPopup || event.target.closest("[data-success-popup-close]")) {
        closeSuccessPopup();
      }
    });
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeMenu();
      closeSuccessPopup();
    }
  });

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

  function extractPhoneDigits(value) {
    let digits = value.replace(/\D/g, "");
    if (digits.startsWith("8")) digits = `7${digits.slice(1)}`;
    if (digits && !digits.startsWith("7")) digits = `7${digits}`;
    return digits.slice(0, 11);
  }

  function formatPhoneDigits(digits) {
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
    return value;
  }

  function normalizePhone(input) {
    input.value = formatPhoneDigits(extractPhoneDigits(input.value));
  }

  function setCursorByDigitIndex(input, digitIndex) {
    const value = input.value;
    if (digitIndex <= 0) {
      input.setSelectionRange(0, 0);
      return;
    }

    let digitsSeen = 0;
    for (let index = 0; index < value.length; index += 1) {
      if (/\d/.test(value[index])) {
        digitsSeen += 1;
        if (digitsSeen >= digitIndex) {
          input.setSelectionRange(index + 1, index + 1);
          return;
        }
      }
    }

    input.setSelectionRange(value.length, value.length);
  }

  function handlePhoneDeletion(input, key) {
    const start = input.selectionStart ?? 0;
    const end = input.selectionEnd ?? start;
    const rawDigits = extractPhoneDigits(input.value);
    const prefixDigits = extractPhoneDigits(input.value.slice(0, start)).length;
    const selectedDigits = extractPhoneDigits(input.value.slice(start, end)).length;

    let digits = rawDigits;
    let cursorDigitIndex = prefixDigits;

    if (start !== end) {
      if (!selectedDigits) return false;
      const from = prefixDigits - selectedDigits;
      digits = `${rawDigits.slice(0, from)}${rawDigits.slice(prefixDigits)}`;
      cursorDigitIndex = from;
    } else if (key === "Backspace") {
      if (prefixDigits <= 1) return true;
      digits = `${rawDigits.slice(0, prefixDigits - 1)}${rawDigits.slice(prefixDigits)}`;
      cursorDigitIndex = prefixDigits - 1;
    } else {
      if (prefixDigits >= rawDigits.length) return true;
      digits = `${rawDigits.slice(0, prefixDigits)}${rawDigits.slice(prefixDigits + 1)}`;
      cursorDigitIndex = prefixDigits;
    }

    input.value = formatPhoneDigits(digits);
    setCursorByDigitIndex(input, cursorDigitIndex);
    return true;
  }

  function hasLink(value) {
    return /(https?:\/\/|www\.|t\.me\/)/i.test(value);
  }

  function validateName(input) {
    const value = input.value.trim().replace(/\s+/g, " ");
    const lettersCount = (value.match(/[A-Za-zА-Яа-яЁё]/g) || []).length;
    const digitsCount = (value.match(/\d/g) || []).length;

    if (value.length < 2) {
      input.setCustomValidity("Укажите имя не короче 2 символов.");
    } else if (value.length > 80) {
      input.setCustomValidity("Имя должно быть не длиннее 80 символов.");
    } else if (lettersCount < 2 || digitsCount > 3 || hasLink(value)) {
      input.setCustomValidity("Укажите реальное имя без ссылок.");
    } else {
      input.setCustomValidity("");
    }

    input.value = value;
    input.classList.toggle("is-invalid", !input.checkValidity());
  }

  function validatePhone(input) {
    normalizePhone(input);
    const digits = input.value.replace(/\D/g, "");

    if (digits.length !== 11 || !digits.startsWith("7")) {
      input.setCustomValidity("Укажите телефон в формате +7XXXXXXXXXX.");
    } else {
      input.setCustomValidity("");
    }

    input.classList.toggle("is-invalid", !input.checkValidity());
  }

  function validateComment(input) {
    const value = input.value.trim();

    if (value.length > 1000) {
      input.setCustomValidity("Комментарий должен быть не длиннее 1000 символов.");
    } else if (hasLink(value)) {
      input.setCustomValidity("Ссылки в комментарии запрещены.");
    } else {
      input.setCustomValidity("");
    }

    input.classList.toggle("is-invalid", !input.checkValidity());
  }

  function getCsrfToken(form) {
    const tokenInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
    return tokenInput ? tokenInput.value : "";
  }

  function clearFieldErrors(form) {
    form.querySelectorAll(".field-error[data-generated-error]").forEach((node) => node.remove());
    form.querySelectorAll(".is-invalid").forEach((field) => field.classList.remove("is-invalid"));
  }

  function renderStatus(form, messages, type) {
    const statusBox = form.querySelector("[data-form-status]");
    if (!statusBox) return;

    statusBox.innerHTML = "";
    const items = Array.isArray(messages) ? messages : [messages];
    items.filter(Boolean).forEach((message) => {
      const item = document.createElement("p");
      item.className = `status-list__item status-list__item--${type}`;
      item.textContent = message;
      statusBox.appendChild(item);
    });
    statusBox.hidden = statusBox.childElementCount === 0;
  }

  function appendFieldError(field, message) {
    if (!field || !message) return;
    field.classList.add("is-invalid");
    const error = document.createElement("small");
    error.className = "field-error";
    error.dataset.generatedError = "true";
    error.textContent = message;
    const container = field.closest("label, fieldset");
    if (container) {
      container.appendChild(error);
    }
  }

  function renderServerErrors(form, errors) {
    const summary = [];

    Object.entries(errors || {}).forEach(([name, items]) => {
      const messages = (items || []).filter(Boolean);
      if (!messages.length) return;

      if (name === "__all__" || name === "non_field_errors") {
        summary.push(...messages);
        return;
      }

      const field = form.querySelector(`[name="${name}"]`);
      appendFieldError(field, messages[0]);
      summary.push(...messages);
    });

    renderStatus(form, summary, "error");
  }

  function setSubmitButtonLoadingState(button, isLoading) {
    if (!button) return;
    button.disabled = isLoading;
    button.classList.toggle("is-loading", isLoading);
    button.setAttribute("aria-busy", String(isLoading));
  }

  document.querySelectorAll('input[name="phone"]').forEach((input) => {
    input.addEventListener("focus", () => {
      if (!input.value.trim()) input.value = "+7 ";
    });
    input.addEventListener("keydown", (event) => {
      if (event.key !== "Backspace" && event.key !== "Delete") return;
      if (!/\D/.test(input.value)) return;
      if (!handlePhoneDeletion(input, event.key)) return;
      event.preventDefault();
      validatePhone(input);
    });
    input.addEventListener("input", () => validatePhone(input));
    input.addEventListener("blur", () => validatePhone(input));
  });

  document.querySelectorAll("[data-application-form]").forEach((form) => {
    const nameInput = form.querySelector('input[name="name"]');
    const phoneInput = form.querySelector('input[name="phone"]');
    const commentInput = form.querySelector('textarea[name="comment"]');

    if (nameInput) {
      nameInput.addEventListener("input", () => validateName(nameInput));
      nameInput.addEventListener("blur", () => validateName(nameInput));
    }

    if (commentInput) {
      commentInput.addEventListener("input", () => validateComment(commentInput));
      commentInput.addEventListener("blur", () => validateComment(commentInput));
    }

    form.addEventListener("submit", async (event) => {
      if (nameInput) validateName(nameInput);
      if (phoneInput) validatePhone(phoneInput);
      if (commentInput) validateComment(commentInput);

      if (!form.checkValidity()) {
        event.preventDefault();
        form.reportValidity();
        const invalidField = form.querySelector(":invalid");
        if (invalidField) invalidField.focus();
        return;
      }

      event.preventDefault();
      clearFieldErrors(form);
      renderStatus(form, [], "info");

      const submitButton = form.querySelector('button[type="submit"]');
      setSubmitButtonLoadingState(submitButton, true);

      try {
        const response = await fetch(form.dataset.applicationEndpoint || form.action, {
          method: "POST",
          headers: {
            "X-CSRFToken": getCsrfToken(form),
            "X-Requested-With": "XMLHttpRequest"
          },
          body: new FormData(form)
        });
        const payload = await response.json();

        if (!response.ok) {
          renderServerErrors(form, payload.errors);
          const invalidField = form.querySelector(".is-invalid, :invalid");
          if (invalidField) invalidField.focus();
          return;
        }

        form.reset();
        openSuccessPopup(
          payload.message || "Мы скоро свяжемся с вами.",
          submitButton
        );
      } catch (error) {
        renderStatus(form, "Не удалось отправить заявку. Попробуйте еще раз.", "error");
      } finally {
        setSubmitButtonLoadingState(submitButton, false);
      }
    });
  });
})();
