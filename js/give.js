(function () {
  var VPA = "74076501@ubin";
  var MAIL = "support@kashtnivaranbalajimandirfoundation.org";
  var LOG_KEY = "knbmf-web-log-v6";

  ["give-summary", "give-risk", "give-note"].forEach(function (id) {
    var n = document.getElementById(id);
    if (n) n.remove();
  });

  var form = document.getElementById("give-form");
  var result = document.getElementById("give-result");
  var qrBox = document.getElementById("give-qr");
  var err = document.getElementById("give-error");
  if (!form || !result || !qrBox) return;

  function showError(msg) {
    if (!err) return;
    err.hidden = !msg;
    err.textContent = msg || "";
  }

  function rupees(n) {
    return Number(n).toLocaleString("en-IN");
  }

  function remember(entry) {
    try {
      var log = JSON.parse(localStorage.getItem(LOG_KEY) || "[]");
      log.push(entry);
      localStorage.setItem(LOG_KEY, JSON.stringify(log.slice(-200)));
    } catch (e) {}
  }

  function upiUri(amount) {
    var uri = "upi://pay?pa=" + VPA + "&cu=INR";
    if (amount) uri += "&am=" + String(amount);
    return uri;
  }

  function openUpiApp(uri) {
    var rest = uri.replace(/^upi:\/\//, "");
    if (/android/i.test(navigator.userAgent || "")) {
      window.location.href =
        "intent://" +
        rest +
        "#Intent;scheme=upi;action=android.intent.action.VIEW;category=android.intent.category.BROWSABLE;end";
      return;
    }
    window.location.href = uri;
  }

  function validate(name, phone, email, amount) {
    if (!name || name.length < 2) return "कृपया दानकर्ता का नाम लिखें।";
    if (!/^[6-9]\d{9}$/.test(phone)) return "सही 10 अंकों का भारतीय मोबाइल नंबर लिखें।";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return "रसीद के लिए सही ईमेल लिखें।";
    if (!amount || amount < 1 || amount > 500000) return "राशि ₹1 से ₹5,00,000 के बीच होनी चाहिए।";
    return "";
  }

  document.querySelectorAll(".amount-chip").forEach(function (chip) {
    chip.addEventListener("click", function () {
      form.amount.value = chip.getAttribute("data-amount") || "";
      document.querySelectorAll(".amount-chip").forEach(function (c) {
        c.classList.toggle("on", c === chip);
      });
      form.amount.focus();
    });
  });

  function showQr(name, phone, email, amount) {
    var uri = upiUri(amount);
    qrBox.innerHTML = "";
    new QRCode(qrBox, {
      text: uri,
      width: 220,
      height: 220,
      colorDark: "#5a241e",
      colorLight: "#ffffff",
      correctLevel: QRCode.CorrectLevel.M,
    });

    document.getElementById("give-amount").textContent = "₹" + rupees(amount);

    remember({
      name: name,
      phone: phone,
      email: email,
      amount: amount,
      at: new Date().toISOString(),
    });

    var upiBtn = document.getElementById("give-upi");
    if (upiBtn) {
      var openUri = upiUri("");
      upiBtn.setAttribute("href", openUri);
      upiBtn.onclick = function (ev) {
        ev.preventDefault();
        openUpiApp(openUri);
      };
    }
    var copyVpa = document.getElementById("give-copy-vpa");
    if (copyVpa) {
      copyVpa.onclick = function () {
        var text = VPA;
        function done() {
          var old = copyVpa.textContent;
          copyVpa.textContent = "कॉपी हो गया";
          setTimeout(function () {
            copyVpa.textContent = old;
          }, 1600);
        }
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done).catch(function () {});
        }
      };
    }

    var q = [
      "Donation from website",
      "",
      "Name: " + name,
      "Mobile: " + phone,
      "Email: " + email,
      "Amount: INR " + amount,
      "UPI ID: " + VPA,
      "",
      "UTR / UPI reference:",
      "PAN (if 80G receipt needed):",
    ].join("\n");
    var mail = document.getElementById("give-mail");
    if (mail) {
      mail.setAttribute(
        "href",
        "mailto:" +
          MAIL +
          "?subject=" +
          encodeURIComponent("Donation · ₹" + amount + " · " + name) +
          "&body=" +
          encodeURIComponent(q)
      );
    }

    form.hidden = true;
    result.hidden = false;
    result.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var name = (form.name.value || "").trim().replace(/\s+/g, " ");
    var phone = (form.phone.value || "").replace(/\D/g, "").slice(-10);
    var email = (form.email.value || "").trim().toLowerCase();
    var amount = parseInt(String(form.amount.value || "").replace(/,/g, ""), 10);
    var msg = validate(name, phone, email, amount);
    if (msg) {
      showError(msg);
      return;
    }
    showError("");

    var api = (window.KNBMF_PAY_API || "").replace(/\/$/, "");
    var submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;
    fetch(api + "/api/uropay/order", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ name: name, phone: phone, email: email, amount: amount }),
    })
      .then(function (res) {
        return res.json().then(function (body) {
          return { ok: res.ok, body: body };
        });
      })
      .then(function (out) {
        if (out.ok && out.body && out.body.openUrl) {
          window.location.href = out.body.openUrl;
          return;
        }
        showQr(name, phone, email, amount);
      })
      .catch(function () {
        showQr(name, phone, email, amount);
      })
      .finally(function () {
        if (submitBtn) submitBtn.disabled = false;
      });
  });

  var again = document.getElementById("give-again");
  if (again) {
    again.addEventListener("click", function () {
      result.hidden = true;
      form.hidden = false;
      qrBox.innerHTML = "";
      form.amount.focus();
    });
  }
})();
