(function () {
  var VPA = "74076501@ubin";
  var PAYEE = "Kast Nivaran Balaji Mandir Foundation";
  var MAIL = "support@kashtnivaranbalajimandirfoundation.org";
  var SEQ_KEY = "knbmf-web-n-v4";
  var LOG_KEY = "knbmf-web-log-v4";

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
    if (n < 1) {
      var buf = new Uint16Array(1);
      if (window.crypto && crypto.getRandomValues) crypto.getRandomValues(buf);
      else buf[0] = Math.floor(Math.random() * 65000);
      n = 1000 + (buf[0] % 8000);
    }
    n += 1;
    try {
      localStorage.setItem(SEQ_KEY, String(n));
    } catch (e) {}
    return "web" + n;
  }

  function remember(entry) {
    try {
      var log = JSON.parse(localStorage.getItem(LOG_KEY) || "[]");
      log.push(entry);
      localStorage.setItem(LOG_KEY, JSON.stringify(log.slice(-200)));
    } catch (e) {}
  }

  function upiUri(amount, note) {
    return (
      "upi://pay?pa=" +
      encodeURIComponent(VPA).replace("%40", "@") +
      "&pn=" +
      encodeURIComponent(PAYEE) +
      "&am=" +
      String(amount) +
      "&cu=INR&tn=" +
      encodeURIComponent(note) +
      "&tr=" +
      encodeURIComponent(note)
    );
  }

  function validate(name, phone, email, amount) {
    if (!name || name.length < 2) return "Please enter the donor name.";
    if (!/^[6-9]\d{9}$/.test(phone)) return "Enter a valid 10-digit Indian mobile number.";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return "Enter a valid email — the office uses this for the receipt.";
    if (!amount || amount < 1 || amount > 500000) return "Amount must be between ₹1 and ₹5,00,000.";
    return "";
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
      "<br>Remark <b>" +
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
