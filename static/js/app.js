// Daily Discipline OS - Main JavaScript

let deferredPrompt = null;
let reminderInterval = null;
let notifiedTasks = new Set(
    JSON.parse(sessionStorage.getItem("ddos_notified_tasks") || "[]")
);

// -----------------------------
// Helpers
// -----------------------------
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function isIOSDevice() {
    return /iphone|ipad|ipod/i.test(window.navigator.userAgent);
}

function isStandaloneMode() {
    return window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
}

function isAuthenticatedPage() {
    const body = document.body;
    return body && body.dataset.authenticated === "true";
}

function currentPath() {
    return window.location.pathname.toLowerCase();
}

function getReminderGraceUntil() {
    return parseInt(sessionStorage.getItem("ddos_reminder_grace_until") || "0", 10);
}

function setReminderGraceUntil(value) {
    sessionStorage.setItem("ddos_reminder_grace_until", String(value));
}

// -----------------------------
// PWA Installation
// -----------------------------
window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt = e;

    const installButton = document.getElementById("install-button");
    if (installButton && !isIOSDevice() && !isStandaloneMode()) {
        installButton.classList.remove("hidden");
        installButton.classList.add("flex");
    }
});

window.addEventListener("appinstalled", () => {
    const installButton = document.getElementById("install-button");
    if (installButton) {
        installButton.classList.add("hidden");
        installButton.classList.remove("flex");
    }

    const iosOverlay = document.getElementById("ios-install-overlay");
    if (iosOverlay) {
        iosOverlay.classList.add("hidden");
    }

    deferredPrompt = null;
    localStorage.setItem("ddos_pwa_installed", "true");
    console.log("PWA was installed");
});

function installPWA() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            console.log("Install choice:", choiceResult.outcome);
            deferredPrompt = null;
        });
        return;
    }

    if (isIOSDevice()) {
        showIOSInstallOverlay(true);
        return;
    }

    alert("To install on Android, open your browser menu and tap 'Install app' or 'Add to Home screen'.");
}

function showIOSInstallOverlay(forceShow = false) {
    const iosOverlay = document.getElementById("ios-install-overlay");
    const installButton = document.getElementById("install-button");

    if (!iosOverlay) return;
    if (!isIOSDevice()) return;
    if (isStandaloneMode()) return;

    const dismissedForSession = sessionStorage.getItem("ddos_ios_install_hidden_session") === "true";
    if (!forceShow && dismissedForSession) return;

    if (installButton) {
        installButton.classList.add("hidden");
        installButton.classList.remove("flex");
    }

    iosOverlay.classList.remove("hidden");
}

function setupIOSInstallOverlay() {
    const iosOverlay = document.getElementById("ios-install-overlay");
    const closeButton = document.getElementById("ios-install-close");

    if (!iosOverlay || !closeButton) return;

    closeButton.addEventListener("click", function () {
        iosOverlay.classList.add("hidden");
        sessionStorage.setItem("ddos_ios_install_hidden_session", "true");
    });

    if (isIOSDevice() && !isStandaloneMode()) {
        showIOSInstallOverlay(false);
    }
}

function setupAndroidInstallFallback() {
    const installButton = document.getElementById("install-button");
    if (!installButton) return;
    if (isIOSDevice() || isStandaloneMode()) return;

    setTimeout(() => {
        if (!deferredPrompt) {
            installButton.classList.remove("hidden");
            installButton.classList.add("flex");
        }
    }, 3000);
}

// -----------------------------
// Service Worker
// -----------------------------
// -----------------------------
// Service Worker
// -----------------------------
if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("/static/sw.js")
            .then((registration) => {
                console.log("SW registered:", registration);
            })
            .catch((error) => {
                console.log("SW registration failed:", error);
            });
    });
}

// -----------------------------
// Theme Toggle
// -----------------------------
function setupThemeToggle() {
    const themeToggle = document.getElementById("theme-toggle");
    if (!themeToggle) return;

    themeToggle.addEventListener("click", function () {
        const html = document.documentElement;
        const isDark = html.classList.contains("dark");

        if (isDark) {
            html.classList.remove("dark");
        } else {
            html.classList.add("dark");
        }

        fetch("/theme/toggle/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "X-Requested-With": "XMLHttpRequest"
            }
        });
    });
}

// -----------------------------
// Notification Dropdown
// -----------------------------
function setupNotificationDropdown() {
    const notificationBtn = document.getElementById("notification-btn");
    const notificationDropdown = document.getElementById("notification-dropdown");

    if (!notificationBtn || !notificationDropdown) return;

    notificationBtn.addEventListener("click", function (e) {
        const isMobile = window.innerWidth < 768;

        if (isMobile) {
            window.location.href = "/notifications/";
            return;
        }

        e.stopPropagation();
        notificationDropdown.classList.toggle("hidden");

        if (!notificationDropdown.classList.contains("hidden")) {
            loadNotifications();
        }
    });

    document.addEventListener("click", function (e) {
        if (!notificationDropdown.contains(e.target) && e.target !== notificationBtn) {
            notificationDropdown.classList.add("hidden");
        }
    });
}

function buildNotificationItem(n) {
    const unreadDot = !n.is_read
        ? '<span class="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-1"></span>'
        : "";

    const linkHtml = n.has_action && n.action_url
        ? `<a href="${n.action_url}" target="_blank" rel="noopener noreferrer" class="inline-flex mt-2 text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline">${n.action_text || "Open Link"}</a>`
        : "";

    return `
        <div class="px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 border-b border-gray-100 dark:border-gray-700 last:border-0 ${n.is_read ? "opacity-60" : ""}">
            <div class="flex items-start justify-between gap-3">
                <div class="min-w-0 flex-1">
                    <p class="text-sm font-medium text-gray-900 dark:text-white">${n.title}</p>
                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">${n.message}</p>
                    <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">${n.created_at}</p>
                    ${linkHtml}
                </div>
                ${unreadDot}
            </div>
        </div>
    `;
}

function loadNotifications() {
    fetch("/notifications/dropdown/", {
        cache: "no-store",
        headers: {
            "X-Requested-With": "XMLHttpRequest"
        }
    })
        .then(response => response.json())
        .then(data => {
            const notificationList = document.getElementById("notification-list");
            const notificationBadge = document.getElementById("notification-badge");

            if (notificationList) {
                if (!data.notifications || data.notifications.length === 0) {
                    notificationList.innerHTML = '<div class="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">No notifications</div>';
                } else {
                    notificationList.innerHTML = data.notifications.map(buildNotificationItem).join("");
                }
            }

            if (notificationBadge) {
                if (data.unread_count > 0) {
                    notificationBadge.textContent = data.unread_count;
                    notificationBadge.classList.remove("hidden");
                } else {
                    notificationBadge.classList.add("hidden");
                }
            }
        })
        .catch(error => console.error("Error loading notifications:", error));
}

// -----------------------------
// Reminder System
// -----------------------------
function setupReminderGracePeriod() {
    if (!isAuthenticatedPage()) return;

    const referrer = (document.referrer || "").toLowerCase();

    if (
        referrer.includes("/login/") ||
        referrer.includes("/register/") ||
        referrer.includes("/logout/")
    ) {
        const delayMs = isIOSDevice() ? 180000 : 90000;
        setReminderGraceUntil(Date.now() + delayMs);
        return;
    }

    if (isIOSDevice()) {
        const currentGrace = getReminderGraceUntil();
        if (currentGrace < Date.now()) {
            setReminderGraceUntil(Date.now() + 30000);
        }
    }
}

function shouldRunReminderChecker() {
    if (!isAuthenticatedPage()) return false;

    const path = currentPath();
    const blockedPaths = [
        "/login/",
        "/register/",
        "/logout/",
        "/admin/",
        "/admin-panel/"
    ];

    if (blockedPaths.some(blocked => path.startsWith(blocked))) {
        return false;
    }

    const graceUntil = getReminderGraceUntil();
    if (Date.now() < graceUntil) {
        return false;
    }

    return true;
}

function setupAudioUnlock() {
    const unlockAudio = () => {
        if (!shouldRunReminderChecker()) {
            return;
        }

        try {
            const audio = document.getElementById("custom-alarm-audio");
            if (audio) {
                audio.volume = 0;
                const playPromise = audio.play();

                if (playPromise !== undefined) {
                    playPromise
                        .then(() => {
                            audio.pause();
                            audio.currentTime = 0;
                            audio.volume = 1.0;
                            console.log("Custom audio unlocked successfully");
                        })
                        .catch((e) => {
                            console.error("Custom audio unlock failed:", e);
                        });
                }
            }
        } catch (e) {
            console.error("Error unlocking custom audio:", e);
        }

        document.removeEventListener("click", unlockAudio);
        document.removeEventListener("keydown", unlockAudio);
        document.removeEventListener("touchstart", unlockAudio);
    };

    document.addEventListener("click", unlockAudio, { once: true });
    document.addEventListener("keydown", unlockAudio, { once: true });
    document.addEventListener("touchstart", unlockAudio, { once: true });
}

function setupNotificationPermissionOnInteraction() {
    const askPermission = () => {
        if (!shouldRunReminderChecker()) {
            return;
        }

        requestNotificationPermission();
        document.removeEventListener("click", askPermission);
        document.removeEventListener("keydown", askPermission);
        document.removeEventListener("touchstart", askPermission);
    };

    document.addEventListener("click", askPermission, { once: true });
    document.addEventListener("keydown", askPermission, { once: true });
    document.addEventListener("touchstart", askPermission, { once: true });
}

function requestNotificationPermission() {
    if ("Notification" in window) {
        if (Notification.permission === "default") {
            Notification.requestPermission().then(permission => {
                console.log("Notification permission:", permission);
            });
        } else {
            console.log("Notification permission already:", Notification.permission);
        }
    } else {
        console.log("Browser notifications not supported");
    }
}

function startReminderCheck() {
    if (reminderInterval) {
        clearInterval(reminderInterval);
    }

    reminderInterval = setInterval(() => {
        if (document.visibilityState === "visible" && shouldRunReminderChecker()) {
            checkReminders();
        }
    }, 30000);

    setTimeout(() => {
        if (shouldRunReminderChecker()) {
            checkReminders();
        }
    }, 5000);

    console.log("Reminder checker started - checking every 30 seconds");
}

function scheduleReminderStartAfterGrace() {
    const now = Date.now();
    const graceUntil = getReminderGraceUntil();

    if (graceUntil > now) {
        const waitMs = graceUntil - now;
        console.log("Reminder checker delayed for", waitMs, "ms");

        setTimeout(() => {
            if (shouldRunReminderChecker()) {
                startReminderCheck();
            }
        }, waitMs);
        return;
    }

    if (shouldRunReminderChecker()) {
        startReminderCheck();
    } else {
        console.log("Reminder checker skipped on this page");
    }
}

function checkReminders() {
    fetch("/tasks/check-reminders/", {
        cache: "no-store",
        headers: {
            "X-Requested-With": "XMLHttpRequest"
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(data => {
            console.log("Reminder check response:", data);

            if (!data.reminders || !Array.isArray(data.reminders) || data.reminders.length === 0) {
                return;
            }

            data.reminders.forEach(reminder => {
                if (!reminder || !reminder.id || !reminder.title) {
                    return;
                }

                if (!notifiedTasks.has(reminder.id)) {
                    notifiedTasks.add(reminder.id);
                    sessionStorage.setItem(
                        "ddos_notified_tasks",
                        JSON.stringify(Array.from(notifiedTasks))
                    );
                    showReminderNotification(reminder);
                }
            });
        })
        .catch(error => console.error("Error checking reminders:", error));
}

function showReminderNotification(reminder) {
    console.log("Showing reminder for:", reminder.title);
    playAlarmSound();

    if ("Notification" in window && Notification.permission === "granted") {
        try {
            const notification = new Notification("⏰ Task Reminder", {
                body: `${reminder.title}${reminder.due_time ? " - " + reminder.due_time : ""}${reminder.notes ? "\n" + reminder.notes : ""}`,
                icon: "/static/icons/icon-192x192.png",
                badge: "/static/icons/icon-72x72.png",
                tag: "task-reminder-" + reminder.id,
                requireInteraction: true
            });

            notification.onclick = function () {
                window.focus();
                notification.close();
            };
        } catch (e) {
            console.error("Error showing notification:", e);
        }
    }

    const isMobile = window.innerWidth < 768;
    if (!isMobile) {
        setTimeout(() => {
            alert(`⏰ Task Reminder\n\n${reminder.title}${reminder.due_time ? "\nTime: " + reminder.due_time : ""}${reminder.notes ? "\n\n" + reminder.notes : ""}`);
        }, 100);
    }
}

function playAlarmSound() {
    if (!shouldRunReminderChecker()) {
        return;
    }

    try {
        const audio = document.getElementById("custom-alarm-audio");
        if (!audio) {
            console.error("Custom alarm audio element not found");
            return;
        }

        audio.pause();
        audio.currentTime = 0;
        audio.volume = 1.0;

        const playPromise = audio.play();
        if (playPromise !== undefined) {
            playPromise
                .then(() => {
                    console.log("Custom alarm sound played");
                })
                .catch((e) => {
                    console.error("Custom alarm play error:", e);
                });
        }
    } catch (e) {
        console.error("Alarm sound error:", e);
    }
}

// -----------------------------
// Auto-dismiss messages
// -----------------------------
function setupAutoDismissMessages() {
    const messages = document.querySelectorAll("[data-auto-dismiss]");
    messages.forEach((msg, index) => {
        setTimeout(() => {
            msg.style.opacity = "0";
            msg.style.transform = "translateX(100%)";
            setTimeout(() => msg.remove(), 300);
        }, 4000 + (index * 500));
    });
}

// -----------------------------
// Modal helpers
// -----------------------------
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove("hidden");
        modal.classList.add("flex");
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
    }
}

document.addEventListener("click", function (e) {
    if (e.target.dataset.modalBackdrop) {
        closeModal(e.target.id);
    }
});

// -----------------------------
// Init
// -----------------------------
document.addEventListener("DOMContentLoaded", function () {
    setupReminderGracePeriod();
    setupThemeToggle();
    setupNotificationDropdown();
    setupAudioUnlock();
    setupNotificationPermissionOnInteraction();
    setupAutoDismissMessages();
    setupIOSInstallOverlay();
    setupAndroidInstallFallback();
    scheduleReminderStartAfterGrace();
});

window.installPWA = installPWA;
window.openModal = openModal;
window.closeModal = closeModal;
window.loadNotifications = loadNotifications;
window.playAlarmSound = playAlarmSound;