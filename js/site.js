(function () {
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
})();
