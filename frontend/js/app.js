/**
 * COGNITIVE ASSISTANCE & INTERVIEW PREPARATION BOT
 * Global Application Core, Auth State & Navigation
 */

const API_BASE = '/api';

const AppState = {
  currentUser: null,
  token: localStorage.getItem('cognitive_token') || null,
  activeTab: 'interviewTab',
  authMode: 'login' // 'login' or 'register'
};

// -------------------------------------------------------------
// INITIALIZATION
// -------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  initNavigationTabs();
  checkAuthStatus();
  fetchSystemStats();
});

// -------------------------------------------------------------
// NAVIGATION TABS
// -------------------------------------------------------------
function initNavigationTabs() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTabId = btn.getAttribute('data-tab');
      switchTab(targetTabId);
    });
  });
}

function switchTab(tabId) {
  // Update Buttons
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-tab') === tabId);
  });

  // Update Panels
  document.querySelectorAll('.tab-panel').forEach(p => {
    p.classList.toggle('active', p.id === tabId);
  });

  AppState.activeTab = tabId;

  // Trigger tab-specific loads
  if (tabId === 'codingTab' && typeof loadCodingProblems === 'function') {
    loadCodingProblems();
  } else if (tabId === 'ragTab' && typeof loadIngestedDocuments === 'function') {
    loadIngestedDocuments();
  } else if (tabId === 'analyticsTab' && typeof loadUserPerformanceHistory === 'function') {
    loadUserPerformanceHistory();
  }
}

// -------------------------------------------------------------
// AUTHENTICATION & PROFILE
// -------------------------------------------------------------
async function checkAuthStatus() {
  if (!AppState.token) {
    renderAuthUI(null);
    return;
  }

  try {
    const res = await apiRequest('/auth/me');
    if (res && res.email) {
      AppState.currentUser = res;
      renderAuthUI(res);
    } else {
      logout();
    }
  } catch (err) {
    console.warn('Auth validation failed, falling back to guest mode:', err);
    logout();
  }
}

function renderAuthUI(user) {
  const container = document.getElementById('authBtnGroup');
  if (user) {
    container.innerHTML = `
      <div style="display: flex; align-items: center; gap: 0.6rem;">
        <span style="font-size: 0.82rem; font-weight: 600; color: #fff;">
          <i class="fa-solid fa-circle-user text-emerald"></i> ${user.full_name.split(' ')[0]}
        </span>
        <button class="btn btn-secondary btn-sm" onclick="logout()" title="Logout">
          <i class="fa-solid fa-arrow-right-from-bracket"></i>
        </button>
      </div>
    `;
  } else {
    container.innerHTML = `
      <button class="btn btn-secondary btn-sm" onclick="openAuthModal()">
        <i class="fa-solid fa-user"></i> Login / Register
      </button>
    `;
  }
}

function openAuthModal() {
  document.getElementById('authModal').classList.add('active');
}

function closeAuthModal() {
  document.getElementById('authModal').classList.remove('active');
}

function toggleAuthMode() {
  AppState.authMode = AppState.authMode === 'login' ? 'register' : 'login';
  const isRegister = AppState.authMode === 'register';

  document.getElementById('authModalTitle').innerText = isRegister ? 'Create Your Account' : 'Welcome to Cognitive Prep';
  document.getElementById('fullNameGroup').style.display = isRegister ? 'flex' : 'none';
  document.getElementById('authSubmitBtn').innerHTML = isRegister
    ? '<i class="fa-solid fa-user-plus"></i> Register'
    : '<i class="fa-solid fa-arrow-right-to-bracket"></i> Login';
  document.getElementById('authTogglePrompt').innerText = isRegister ? 'Already have an account?' : "Don't have an account?";
  document.getElementById('authToggleLink').innerText = isRegister ? 'Login' : 'Register';
}

async function handleAuthSubmit(e) {
  e.preventDefault();
  const email = document.getElementById('authEmail').value.trim();
  const password = document.getElementById('authPassword').value;
  const fullName = document.getElementById('authFullName').value.trim();

  const endpoint = AppState.authMode === 'register' ? '/auth/register' : '/auth/login';
  const payload = { email, password };
  if (AppState.authMode === 'register') {
    payload.full_name = fullName || 'Tech Candidate';
  }

  try {
    const data = await apiRequest(endpoint, 'POST', payload);
    if (data.access_token) {
      AppState.token = data.access_token;
      localStorage.setItem('cognitive_token', data.access_token);
      AppState.currentUser = data.user;
      renderAuthUI(data.user);
      closeAuthModal();
      showToast(`Welcome back, ${data.user.full_name}!`, 'success');
      fetchSystemStats();
    }
  } catch (err) {
    showToast(err.message || 'Authentication error', 'error');
  }
}

async function loginDemoProfile(email, password) {
  document.getElementById('authEmail').value = email;
  document.getElementById('authPassword').value = password;
  AppState.authMode = 'login';
  
  try {
    const data = await apiRequest('/auth/login', 'POST', { email, password });
    if (data.access_token) {
      AppState.token = data.access_token;
      localStorage.setItem('cognitive_token', data.access_token);
      AppState.currentUser = data.user;
      renderAuthUI(data.user);
      closeAuthModal();
      showToast(`Signed in as ${data.user.full_name}`, 'success');
      fetchSystemStats();
    }
  } catch (err) {
    showToast('Failed to sign in demo profile: ' + err.message, 'error');
  }
}

function logout() {
  AppState.token = null;
  AppState.currentUser = null;
  localStorage.removeItem('cognitive_token');
  renderAuthUI(null);
  showToast('Logged out successfully.', 'info');
}

// -------------------------------------------------------------
// GLOBAL API REQUEST WRAPPER
// -------------------------------------------------------------
async function apiRequest(endpoint, method = 'GET', body = null, isFormData = false) {
  const headers = {};
  if (!isFormData) {
    headers['Content-Type'] = 'application/json';
  }
  if (AppState.token) {
    headers['Authorization'] = `Bearer ${AppState.token}`;
  }

  const options = { method, headers };
  if (body) {
    options.body = isFormData ? body : JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE}${endpoint}`, options);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || data.message || `Request failed with status ${response.status}`);
  }

  return data;
}

// -------------------------------------------------------------
// SYSTEM STATS & METRICS
// -------------------------------------------------------------
async function fetchSystemStats() {
  try {
    const stats = await apiRequest('/stats');
    if (stats) {
      const chunkCountEl = document.getElementById('statVectorChunks');
      if (chunkCountEl) chunkCountEl.innerText = stats.vector_chunks || '12+';

      const interviewCountEl = document.getElementById('statTotalInterviews');
      if (interviewCountEl) interviewCountEl.innerText = stats.total_interviews_conducted || '0';

      const badge = document.getElementById('headerStatsBadge');
      if (badge) {
        badge.innerHTML = `<i class="fa-solid fa-database text-cyan"></i> <span>${stats.vector_chunks || 12} Chunks Indexed</span>`;
      }
    }
  } catch (err) {
    console.warn('Could not fetch system stats:', err);
  }
}

// -------------------------------------------------------------
// TOAST NOTIFICATIONS
// -------------------------------------------------------------
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = 'toast';

  let icon = 'fa-info-circle text-cyan';
  if (type === 'success') icon = 'fa-circle-check text-emerald';
  if (type === 'error') icon = 'fa-circle-exclamation text-rose';
  if (type === 'warning') icon = 'fa-triangle-exclamation text-amber';

  toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
