(function () {
  var VPA = "knbmfoundatio@ybl";
  var PAYEE = "Kast Nivaran Balaji Mandir Foundation";
  var MAIL = "support@kashtnivaranbalajimandirfoundation.org";
  var SEQ_KEY = "knbmf-note-n-v5";
  var LOG_KEY = "knbmf-web-log-v5";

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

  function nextWebNote() {
    var n = 0;
    try {
      n = parseInt(localStorage.getItem(SEQ_KEY) || "0", 10) || 0;
    } catch (e) {
      n = 0;
    }
    n += 1;
    try {
      localStorage.setItem(SEQ_KEY, String(n));
    } catch (e) {}
    return "knbmf" + n;
  }

  function remember(entry) {
    try {
      var log = JSON.parse(localStorage.getItem(LOG_KEY) || "[]");
      log.push(entry);
      localStorage.setItem(LOG_KEY, JSON.stringify(log.slice(-200)));
    } catch (e) {}
  }

  function upiUri(amount, note) {
    // P2P payee. Do not send tr/mc — those are merchant fields.
    // Spaces in tr are declined by NPCI and often shown as "UPI risk policy".
    return (
      "upi://pay?pa=" +
      VPA +
      "&pn=" +
      encodeURIComponent(PAYEE) +
      "&am=" +
      String(amount) +
      "&cu=INR&tn=" +
      encodeURIComponent(note)
    );
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

    var note = nextWebNote();
    var uri = upiUri(amount, note);
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
    var noteEl = document.getElementById("give-note");
    if (noteEl) noteEl.textContent = note;
    document.getElementById("give-summary").innerHTML =
      "<b>" +
      name.replace(/</g, "") +
      "</b><br>" +
      phone +
      "<br>" +
      email.replace(/</g, "") +
      "<br>टिप्पणी <b>" +
      note +
      "</b> · UPI " +
      VPA;

    remember({
      note: note,
      name: name,
      phone: phone,
      email: email,
      amount: amount,
      at: new Date().toISOString(),
    });

    var upiBtn = document.getElementById("give-upi");
    if (upiBtn) upiBtn.setAttribute("href", uri);
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
      "Remark: " + note,
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
          encodeURIComponent("Donation " + note + " · ₹" + amount + " · " + name) +
          "&body=" +
          encodeURIComponent(q)
      );
    }

    form.hidden = true;
    result.hidden = false;
    result.scrollIntoView({ behavior: "smooth", block: "start" });
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
