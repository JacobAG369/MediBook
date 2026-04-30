/* ===========================
   MediBook — Frontend Logic
   =========================== */

const API_BASE = '/api/v1';

// ---------- Auth Helpers ----------

function getToken() {
  return localStorage.getItem('medibook_token');
}

function getUser() {
  const raw = localStorage.getItem('medibook_user');
  return raw ? JSON.parse(raw) : null;
}

function logout() {
  localStorage.removeItem('medibook_token');
  localStorage.removeItem('medibook_user');
  window.location.href = '/web/login';
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = '/web/login';
    return false;
  }
  return true;
}

// ---------- API Fetch Wrapper ----------

async function apiFetch(endpoint, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const resp = await fetch(`${endpoint}`, { ...options, headers });

  if (resp.status === 401) {
    logout();
    throw new Error('Session expired');
  }

  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    throw new Error(body.detail || `Error ${resp.status}`);
  }

  return resp.json();
}

// ---------- Format Helpers ----------

function formatDate(isoString) {
  if (!isoString) return '—';
  const d = new Date(isoString);
  return d.toLocaleDateString('es-MX', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

// ---------- Sidebar User Info ----------

function renderSidebarUser() {
  const container = document.getElementById('sidebar-user');
  if (!container) return;

  const user = getUser();
  if (!user) return;

  const initials = user.username
    .split(/[._-]/)
    .map(w => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  container.innerHTML = `
    <div class="sidebar__user">
      <div class="sidebar__avatar">${initials}</div>
      <div class="sidebar__user-info">
        <div class="sidebar__user-name">${user.username}</div>
        <div class="sidebar__user-role">${user.role}</div>
      </div>
    </div>
    <button class="btn btn--ghost btn--sm" style="width:100%; margin-top:0.75rem;" onclick="logout()">
      Cerrar sesion
    </button>
  `;
}

// ---------- Init ----------

document.addEventListener('DOMContentLoaded', () => {
  renderSidebarUser();
});
