document.addEventListener("DOMContentLoaded", function () {
  const banner = document.getElementById("cookie-banner");
  const acceptBtn = document.getElementById("cookie-accept");
  const rejectBtn = document.getElementById("cookie-reject");

  // --- helpers ---
  function setConsentCookie(value) {
    // 180 days, site-wide, HTTPS-friendly
    const maxAge = 60 * 60 * 24 * 180;
    const secure = location.protocol === "https:" ? "; Secure" : "";
    document.cookie = "cookieConsent=" + value + "; path=/; max-age=" + maxAge + "; SameSite=Lax" + secure;
  }

  function getCookie(name) {
    return document.cookie
      .split("; ")
      .find((row) => row.startsWith(name + "="))
      ?.split("=")[1];
  }

  function loadRecaptchaIfPossible() {
    // If there is a recaptcha placeholder and it has a sitekey, load script
    const el = document.querySelector(".g-recaptcha");
    if (!el) return; // no placeholder → nothing to do
    const sitekey = el.getAttribute("data-sitekey");
    if (!sitekey) {
      console.warn("reCAPTCHA site key not set in template. Skipping load.");
      return;
    }

    // If script already loaded, do nothing
    if (window.grecaptcha || document.querySelector('script[src*="recaptcha/api.js"]')) return;

    const s = document.createElement("script");
    s.src = "https://www.google.com/recaptcha/api.js";
    s.async = true;
    s.defer = true;
    document.head.appendChild(s);
  }

  // --- initial state ---
  const stored = localStorage.getItem("cookieConsent");
  const cookie = getCookie("cookieConsent");

  if (stored === "accepted" || cookie === "accepted") {
    banner && (banner.style.display = "none");
    loadRecaptchaIfPossible();
  } else if (stored === "rejected" || cookie === "rejected") {
    banner && (banner.style.display = "none");
  } else {
    banner && (banner.style.display = "flex");
  }

  // --- actions ---
  acceptBtn?.addEventListener("click", function () {
    localStorage.setItem("cookieConsent", "accepted");
    setConsentCookie("accepted");
    banner && (banner.style.display = "none");

    // load reCAPTCHA without reloading the page
    loadRecaptchaIfPossible();
  });

  rejectBtn?.addEventListener("click", function () {
    localStorage.setItem("cookieConsent", "rejected");
    setConsentCookie("rejected");
    banner && (banner.style.display = "none");
  });
});
