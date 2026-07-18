const API_BASE_URL = "http://127.0.0.1:8000";
const TOKEN_KEY = "student_predictor_token";

function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
}

function requireAuth() {
    if (!getToken()) {
        window.location.href = "login.html";
    }
}

function redirectIfLoggedIn() {
    if (getToken()) {
        window.location.href = "dashboard.html";
    }
}

function showAlert(elementId, message, type = "danger") {
    const alert = document.getElementById(elementId);
    if (!alert) return;
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `<i class="bi ${type === "success" ? "bi-check-circle" : "bi-exclamation-circle"} me-2"></i>${escapeHtml(message)}`;
    alert.classList.remove("d-none");
}

function hideAlert(elementId) {
    const alert = document.getElementById(elementId);
    if (!alert) return;
    alert.classList.add("d-none");
    alert.textContent = "";
}

function setLoading(isLoading) {
    const overlay = document.getElementById("loadingOverlay");
    if (!overlay) return;
    overlay.classList.toggle("show", isLoading);
}

function showToast(message, type = "success") {
    let container = document.getElementById("toastContainer");
    if (!container) {
        container = document.createElement("div");
        container.id = "toastContainer";
        container.className = "toast-container position-fixed top-0 end-0 p-3";
        document.body.appendChild(container);
    }

    const toastId = `toast-${Date.now()}`;
    const icon = type === "success" ? "bi-check-circle text-success" : "bi-exclamation-triangle text-danger";
    container.insertAdjacentHTML("beforeend", `
        <div id="${toastId}" class="toast premium-toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-body d-flex align-items-center gap-2">
                <i class="bi ${icon}"></i>
                <span>${escapeHtml(message)}</span>
                <button type="button" class="btn-close ms-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `);

    const toastElement = document.getElementById(toastId);
    const toast = bootstrap.Toast.getOrCreateInstance(toastElement, { delay: 2600 });
    toastElement.addEventListener("hidden.bs.toast", () => toastElement.remove());
    toast.show();
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

async function apiRequest(path, options = {}) {
    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {}),
    };

    const token = getToken();
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        headers,
    });

    let data = null;
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
        data = await response.json();
    }

    if (!response.ok) {
        if (response.status === 401) {
            clearToken();
            window.location.href = "login.html";
        }
        const detail = data && data.detail ? data.detail : "Something went wrong.";
        throw new Error(Array.isArray(detail) ? detail[0].msg : detail);
    }

    return data;
}

function setupLogout() {
    const logoutButton = document.getElementById("logoutButton");
    if (!logoutButton) return;

    logoutButton.addEventListener("click", async () => {
        try {
            await apiRequest("/auth/logout", { method: "POST" });
        } catch (error) {
            // Logout remains client-side even if the optional API call fails.
        }
        clearToken();
        window.location.href = "login.html";
    });
}

function formatDate(value) {
    return new Date(value).toLocaleString();
}

function statusBadge(status) {
    const badgeClass = status === "Pass" ? "badge-pass" : "badge-fail";
    const icon = status === "Pass" ? "bi-check-circle" : "bi-x-circle";
    return `<span class="badge ${badgeClass}"><i class="bi ${icon} me-1"></i>${status}</span>`;
}

function gradeBadge(grade) {
    return `<span class="badge badge-grade">${escapeHtml(grade)}</span>`;
}

function renderEmptyState(colspan, icon, message) {
    return `<tr><td colspan="${colspan}" class="empty-state"><i class="bi ${icon}"></i>${message}</td></tr>`;
}

function animateCounter(elementId, value, decimals = 0) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const numericValue = Number(value) || 0;
    const duration = 700;
    const startTime = performance.now();

    function update(now) {
        const progress = Math.min((now - startTime) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = numericValue * eased;
        element.textContent = current.toFixed(decimals);
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

function createConfirmModal({
    modalId,
    title,
    message,
    confirmText,
    confirmClass = "btn-primary",
}) {
    return `
        <div class="modal fade" id="${modalId}" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2 class="modal-title h5"><i class="bi bi-shield-check me-2 text-primary"></i>${title}</h2>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p class="mb-0">${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" id="${modalId}Confirm" class="btn ${confirmClass}">${confirmText}</button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function showConfirmModal(modalId, onConfirm) {
    const modalElement = document.getElementById(modalId);
    const confirmButton = document.getElementById(`${modalId}Confirm`);
    if (!modalElement || !confirmButton) return;

    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
    confirmButton.onclick = async () => {
        confirmButton.disabled = true;
        try {
            await onConfirm();
            modal.hide();
        } finally {
            confirmButton.disabled = false;
        }
    };
    modal.show();
}

async function loadCurrentUser() {
    return apiRequest("/users/me");
}

function setupButtonRipples() {
    document.addEventListener("click", (event) => {
        const button = event.target.closest(".btn");
        if (!button) return;

        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const ripple = document.createElement("span");
        ripple.className = "ripple";
        ripple.style.width = `${size}px`;
        ripple.style.height = `${size}px`;
        ripple.style.left = `${event.clientX - rect.left - size / 2}px`;
        ripple.style.top = `${event.clientY - rect.top - size / 2}px`;
        button.appendChild(ripple);
        ripple.addEventListener("animationend", () => ripple.remove());
    });
}

document.addEventListener("DOMContentLoaded", () => {
    setupLogout();
    setupButtonRipples();
});
