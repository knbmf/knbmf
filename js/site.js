(function () {
  var SITE = "https://kashtnivaranbalajimandirfoundation.org/";
  var GIVE = SITE + "give.html";
  var SHARE_TEXT =
    "काशीपुर की धारा 8 संस्था — कष्ट निवारण बालाजी मंदिर फाउंडेशन। मंगलवार निःशुल्क क्लिनिक चल रहा है। विद्यालय, गौशाला, वृद्धाश्रम बनेंगे। दान: " +
    GIVE +
    "  UPI knbmfoundatio@ybl  अस्थायी 80G।";

  var btn = document.querySelector(".menu-btn");
  var nav = document.querySelector(".nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        nav.classList.remove("open");
        btn.setAttribute("aria-expanded", "false");
      }
    });
  }

  var path = location.pathname.replace(/\/+$/, "");
  var file = path.split("/").pop() || "index.html";
  if (file === "" || file === "knbmf") file = "index.html";
  document.querySelectorAll(".nav a").forEach(function (a) {
    var href = a.getAttribute("href");
    if (href === file || (file === "index.html" && href === "index.html")) {
      a.setAttribute("aria-current", "page");
    }
  });

  var hideDock = file === "give.html" || file === "donate.html";
  if (!hideDock) {
    var dock = document.createElement("div");
    dock.className = "donate-dock";
    dock.setAttribute("role", "region");
    dock.setAttribute("aria-label", file === "en.html" ? "Donate" : "दान");
    dock.innerHTML =
      file === "en.html"
        ? '<a class="btn btn-gold" href="give.html">Donate now</a><a class="btn btn-ghost" href="share.html">Share</a>'
        : '<a class="btn btn-gold" href="give.html">अभी दान करें</a><a class="btn btn-ghost" href="share.html">साझा करें</a>';
    document.body.appendChild(dock);
    document.body.classList.add("has-dock");
  }

  var WA_CHAT = "917668397233";
  function waUrl(text) {
    var note = text || SHARE_TEXT;
    return "https://wa.me/" + WA_CHAT + "?text=" + encodeURIComponent(note);
  }
  function fbUrl(url) {
    return "https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(url);
  }
  function xUrl(text, url) {
    return (
      "https://twitter.com/intent/tweet?text=" +
      encodeURIComponent(text) +
      "&url=" +
      encodeURIComponent(url)
    );
  }

  function shareHref(el) {
    var kind = el.getAttribute("data-share");
    var text = el.getAttribute("data-text") || SHARE_TEXT;
    var from = el.getAttribute("data-from");
    if (from) {
      var node = document.querySelector(from);
      if (node) text = node.value || node.textContent || text;
    }
    var url = el.getAttribute("data-url") || GIVE;
    if (kind === "whatsapp") return waUrl(text);
    if (kind === "facebook") return fbUrl(url);
    if (kind === "x") return xUrl(text, url);
    if (kind === "telegram") {
      return (
        "https://t.me/share/url?url=" +
        encodeURIComponent(url) +
        "&text=" +
        encodeURIComponent(text)
      );
    }
    return "";
  }
  document.querySelectorAll("[data-share]").forEach(function (el) {
    var href = shareHref(el);
    if (href) el.setAttribute("href", href);
    el.addEventListener("click", function (ev) {
      var next = shareHref(el);
      if (!next) return;
      el.setAttribute("href", next);
      if (el.getAttribute("data-share") === "whatsapp") {
        ev.preventDefault();
        window.open(next, "_blank", "noopener");
      }
    });
  });

  document.querySelectorAll("[data-copy]").forEach(function (btnEl) {
    btnEl.addEventListener("click", function () {
      var sel = btnEl.getAttribute("data-copy");
      var node = sel ? document.querySelector(sel) : null;
      var text = "";
      if (node) text = node.value || node.textContent || "";
      if (!text) text = SHARE_TEXT;
      function done() {
        var old = btnEl.textContent;
        btnEl.textContent = "कॉपी हो गया";
        setTimeout(function () {
          btnEl.textContent = old;
        }, 1600);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done).catch(function () {});
      }
    });
  });

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("sw.js").catch(function () {});
  }
})();
