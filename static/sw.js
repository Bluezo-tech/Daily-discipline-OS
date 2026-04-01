const CACHE_NAME = "discipline-os-v4";
const STATIC_ASSETS = [
    "/static/css/styles.css",
    "/static/js/app.js",
    "/manifest.webmanifest",
    "/static/icons/icon-72x72.png",
    "/static/icons/icon-192x192.png",
    "/static/icons/icon-512x512.png",
];

// Install
self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
    );
    self.skipWaiting();
});

// Activate
self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) =>
            Promise.all(
                cacheNames
                    .filter((name) => name !== CACHE_NAME)
                    .map((name) => caches.delete(name))
            )
        )
    );
    self.clients.claim();
});

// Fetch
self.addEventListener("fetch", (event) => {
    if (event.request.method !== "GET") return;

    const url = new URL(event.request.url);

    // Never cache dynamic pages
    if (
        event.request.mode === "navigate" ||
        url.pathname.startsWith("/admin/") ||
        url.pathname.startsWith("/admin-panel/") ||
        url.pathname.startsWith("/login/") ||
        url.pathname.startsWith("/logout/") ||
        url.pathname.startsWith("/register/") ||
        url.pathname.startsWith("/dashboard/") ||
        url.pathname.startsWith("/tasks/") ||
        url.pathname.startsWith("/habits/") ||
        url.pathname.startsWith("/notifications/") ||
        url.pathname.startsWith("/accounts/") ||
        url.pathname.startsWith("/theme/")
    ) {
        return;
    }

    // Cache only static assets and manifest
    if (
        !url.pathname.startsWith("/static/") &&
        url.pathname !== "/manifest.webmanifest"
    ) {
        return;
    }

    event.respondWith(
        caches.match(event.request).then((response) => {
            if (response) return response;

            return fetch(event.request).then((networkResponse) => {
                if (
                    !networkResponse ||
                    networkResponse.status !== 200
                ) {
                    return networkResponse;
                }

                const responseToCache = networkResponse.clone();
                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(event.request, responseToCache);
                });

                return networkResponse;
            });
        })
    );
});

// Push
self.addEventListener("push", (event) => {
    if (!event.data) return;

    const data = event.data.json();
    const options = {
        body: data.body,
        icon: "/static/icons/icon-192x192.png",
        badge: "/static/icons/icon-72x72.png",
        vibrate: [100, 50, 100],
        data: {
            url: data.url || "/"
        }
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// Notification click
self.addEventListener("notificationclick", (event) => {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url || "/")
    );
});