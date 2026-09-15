/* KNBMF web app — cache the public pages for install/offline. */
var CACHE = "knbmf-v2";
var PRECACHE = [
  "/",
  "/index.html",
  "/give.html",
  "/donate.html",
  "/css/styles.css",
  "/js/site.js",
  "/js/give.js",
  "/js/qrcode.min.js",
  "/assets/logo-mark.png",
  "/assets/favicon.png",
  "/manifest.webmanifest",
];

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(CACHE).then(function (cache) {
      return cache.addAll(PRECACHE);
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(
        keys.filter(function (k) { return k !== CACHE; }).map(function (k) {
          return caches.delete(k);
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener("fetch", function (event) {
  if (event.request.method !== "GET") return;
  var url = new URL(event.request.url);
  if (url.origin !== location.origin) return;
  event.respondWith(
    caches.match(event.request).then(function (cached) {
      var net = fetch(event.request)
        .then(function (res) {
          if (res && res.ok) {
            var copy = res.clone();
            caches.open(CACHE).then(function (cache) {
              cache.put(event.request, copy);
            });
          }
          return res;
        })
        .catch(function () {
          return cached || caches.match("/index.html");
        });
      return cached || net;
    })
  );
});
