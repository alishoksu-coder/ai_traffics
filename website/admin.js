// admin.js
const API_BASE = 'https://ai-traffics.onrender.com';

const loginContainer = document.getElementById('login-container');
const dashboardContainer = document.getElementById('dashboard-container');
const loginForm = document.getElementById('login-form');
const errorMsg = document.getElementById('login-error');
const logoutBtn = document.getElementById('logout-btn');

// Initial auth check
function checkAuth() {
  const token = localStorage.getItem('admin_token');
  if (token) {
    showDashboard(token);
  } else {
    showLogin();
  }
}

function showLogin() {
  loginContainer.style.display = 'block';
  dashboardContainer.style.display = 'none';
  errorMsg.textContent = '';
}

async function showDashboard(token) {
  loginContainer.style.display = 'none';
  dashboardContainer.style.display = 'block';
  
  try {
    document.getElementById('admin-status').textContent = 'Синхронизация...';
    
    const res = await fetch(`${API_BASE}/admin/dashboard`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (res.status === 401) {
      localStorage.removeItem('admin_token');
      showLogin();
      errorMsg.textContent = 'Сессия ескірді. Қайта кіріңіз.';
      return;
    }

    if (!res.ok) throw new Error("API қатесі");

    const data = await res.json();
    
    // Fill stats
    document.getElementById('stat-locations').textContent = data.locations_count || 0;
    document.getElementById('stat-segments').textContent = data.segments_count || 0;
    document.getElementById('stat-friends').textContent = data.friends_count || 0;
    document.getElementById('stat-vehicles').textContent = data.vehicles_count || 0;
    
    const scoreEl = document.getElementById('stat-traffic-score');
    scoreEl.textContent = data.traffic_score || 0;
    if(data.traffic_score <= 3) {
      scoreEl.style.color = '#10B981'; // Green
    } else if(data.traffic_score <= 6) {
      scoreEl.style.color = '#F59E0B'; // Yellow
    } else {
      scoreEl.style.color = '#EF4444'; // Red
    }

    document.getElementById('stat-avg-traffic').textContent = (data.avg_traffic_value || 0).toFixed(1) + '%';
    
    const simEl = document.getElementById('stat-sim-running');
    if (data.sim_running) {
      simEl.textContent = 'ҚОСУЛЫ (On)';
      simEl.className = 'badge success';
    } else {
      simEl.textContent = 'ӨШІК (Off)';
      simEl.className = 'badge danger';
    }

    document.getElementById('stat-hotspots').textContent = data.hotspots || 0;
    
    document.getElementById('admin-status').textContent = 'Желіде (Online)';

  } catch (err) {
    document.getElementById('admin-status').textContent = 'Байланыс жоқ';
    console.error(err);
  }
}

// Login Submit Hook
loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const loginBtn = document.getElementById('login-btn');
  const loginVal = document.getElementById('login').value.trim();
  const passVal = document.getElementById('password').value;
  
  if (!loginVal || !passVal) return;

  try {
    loginBtn.disabled = true;
    loginBtn.textContent = 'Күте тұрыңыз...';
    errorMsg.textContent = '';

    const res = await fetch(`${API_BASE}/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ login: loginVal, password: passVal })
    });

    if (res.status === 401) {
      errorMsg.textContent = 'Қате логин немесе пароль';
      return;
    }

    if (!res.ok) throw new Error('Сервер қатесі');

    const data = await res.json();
    if(data.token) {
      localStorage.setItem('admin_token', data.token);
      showDashboard(data.token);
    }
  } catch (err) {
    errorMsg.textContent = 'Желіге қосылу қатесі';
  } finally {
    loginBtn.disabled = false;
    loginBtn.textContent = 'Кіру';
  }
});

// Logout
logoutBtn.addEventListener('click', () => {
  localStorage.removeItem('admin_token');
  showLogin();
});

// Init
checkAuth();
