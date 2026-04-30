/* MediBook — Frontend Logic */

const API_BASE = '/api/v1';

// ---------- Auth Helpers ----------

function getToken() { return localStorage.getItem('medibook_token'); }

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

// ---------- API Fetch ----------

async function apiFetch(endpoint, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const resp = await fetch(endpoint, { ...options, headers });

  if (resp.status === 401) {
    logout();
    throw new Error('Sesión expirada');
  }

  if (!resp.ok) {
    // Intentar leer el detalle de error; si no hay cuerpo se usa mensaje genérico
    const body = await resp.json().catch(() => ({}));
    throw new Error(body.detail || `Error ${resp.status}`);
  }

  // 204 No Content y respuestas sin cuerpo no tienen JSON que parsear
  if (resp.status === 204 || resp.headers.get('content-length') === '0') {
    return null;
  }
  const contentType = resp.headers.get('content-type') || '';
  if (!contentType.includes('application/json')) {
    return null;
  }

  return resp.json();
}

// ---------- Format Helpers ----------

function formatDate(isoString) {
  if (!isoString) return '—';
  const d = new Date(isoString);
  return d.toLocaleDateString('es-MX', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

function formatDateShort(isoString) {
  if (!isoString) return '—';
  const d = new Date(isoString);
  return d.toLocaleDateString('es-MX', { year: 'numeric', month: 'short', day: 'numeric' });
}

// ---------- Toast Notifications ----------

function showToast(message, type = 'info', duration = 4000) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const icons = {
    success: '<svg viewBox="0 0 24 24" style="width:16px;height:16px;stroke:#10b981;fill:none;stroke-width:2.5;flex-shrink:0"><polyline points="20 6 9 17 4 12"/></svg>',
    error:   '<svg viewBox="0 0 24 24" style="width:16px;height:16px;stroke:#ef4444;fill:none;stroke-width:2.5;flex-shrink:0"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    info:    '<svg viewBox="0 0 24 24" style="width:16px;height:16px;stroke:#0ea5e9;fill:none;stroke-width:2.5;flex-shrink:0"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
  };

  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;
  toast.innerHTML = `${icons[type] || ''}<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(16px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ---------- Sidebar User ----------

function renderSidebarUser() {
  const container = document.getElementById('sidebar-user');
  if (!container) return;

  const user = getUser();
  if (!user) {
    container.innerHTML = `<button class="btn btn--ghost btn--sm" style="width:100%;" onclick="logout()">Cerrar sesión</button>`;
    return;
  }

  const initials = (user.username || 'U')
    .split(/[._\-\s]/).map(w => w[0]).join('').toUpperCase().slice(0, 2) || 'U';

  const roleLabels = { ADMIN: 'Administrador', DOCTOR: 'Doctor', RECEPTIONIST: 'Recepcionista', PATIENT: 'Paciente' };

  container.innerHTML = `
    <div class="sidebar__user">
      <div class="sidebar__avatar">${initials}</div>
      <div class="sidebar__user-info">
        <div class="sidebar__user-name">${user.username}</div>
        <div class="sidebar__user-role">${roleLabels[user.role] || user.role || ''}</div>
      </div>
    </div>
    <button class="btn btn--ghost btn--sm" style="width:100%;margin-top:0.6rem;justify-content:center;" onclick="logout()">
      <svg viewBox="0 0 24 24" style="width:14px;height:14px;stroke:currentColor;fill:none;stroke-width:2;"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
      Cerrar sesión
    </button>
  `;
}

// ---------- Init ----------

document.addEventListener('DOMContentLoaded', () => {
  renderSidebarUser();
});
