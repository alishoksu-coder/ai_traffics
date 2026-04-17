// admin.js
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
  ? 'http://127.0.0.1:8000' 
  : 'https://ai-traffics.onrender.com';

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
    
    // Set admin name
    const adminNameEl = document.getElementById('admin-name-display');
    if (adminNameEl) adminNameEl.textContent = data.admin_name || 'Админ';

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

    // --- Weather Widget ---
    try {
      const weatherRes = await fetch(`${API_BASE}/weather`);
      const weatherData = await weatherRes.json();
      let impactHtml = '';
      if (weatherData.traffic_factor > 1.0) {
          const percent = Math.round((weatherData.traffic_factor - 1.0) * 100);
          impactHtml = `<span style="color: #EF4444; font-weight: bold;">+${percent}%</span> (замедление)`;
      } else {
          impactHtml = `<span style="color: #10B981; font-weight: bold;">0%</span> (в норме)`;
      }
      document.getElementById('stat-weather').innerHTML = `<strong style="font-size: 24px;">${weatherData.temp}°C</strong><br><span style="font-size: 15px;">${weatherData.description}</span><br><small style="color: #6B7280; margin-top: 6px; display: inline-block; font-size: 13px;">Коэфф. замедления: ${impactHtml}</small>`;
    } catch(e) {
      document.getElementById('stat-weather').textContent = 'Мәлімет жоқ';
    }

    // --- Chart.js Rendering ---
    try {
      const histRes = await fetch(`${API_BASE}/traffic/history?minutes=120`);
      const histData = await histRes.json();
      
      // Group by timestamp to calculate average traffic across all segments
      const timeGroups = {};
      histData.items.forEach(item => {
        const t = item[1]; // ts
        const v = item[3]; // value
        if(!timeGroups[t]) timeGroups[t] = [];
        timeGroups[t].push(v);
      });

      const labels = [];
      const dataPoints = [];
      
      Object.keys(timeGroups).sort().forEach(ts => {
        const date = new Date(parseInt(ts) * 1000);
        labels.push(`${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`);
        const avg = timeGroups[ts].reduce((a, b) => a + b, 0) / timeGroups[ts].length;
        dataPoints.push(avg.toFixed(1));
      });

      renderChart(labels, dataPoints);
    } catch(e) {
      console.error("График қатесі:", e);
    }

  } catch (err) {
    document.getElementById('admin-status').textContent = 'Байланыс жоқ';
    console.error(err);
  }
}

let trafficChartInstance = null;
function renderChart(labels, data) {
  const ctx = document.getElementById('trafficChart').getContext('2d');
  if(trafficChartInstance) {
    trafficChartInstance.destroy();
  }
  trafficChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Орташа трафик деңгейі (%)',
        data: data,
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.2)',
        borderWidth: 2,
        tension: 0.4,
        fill: true,
        pointRadius: 2
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 100
        }
      }
    }
  });
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
    loginBtn.textContent = 'Кіру (Войти)';
  }
});

// Tab Switching
const tabLogin = document.getElementById('tab-login');
const tabRegister = document.getElementById('tab-register');
const registerForm = document.getElementById('register-form');
const registerErrorMsg = document.getElementById('register-error');

tabLogin.addEventListener('click', () => {
    tabLogin.classList.add('active');
    tabRegister.classList.remove('active');
    loginForm.style.display = 'block';
    registerForm.style.display = 'none';
});

tabRegister.addEventListener('click', () => {
    tabRegister.classList.add('active');
    tabLogin.classList.remove('active');
    registerForm.style.display = 'block';
    loginForm.style.display = 'none';
});

// Register Submit Hook
registerForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const regBtn = document.getElementById('register-btn');
  const loginVal = document.getElementById('reg-login').value.trim();
  const passVal = document.getElementById('reg-password').value;
  
  if (!loginVal || !passVal) return;

  try {
    regBtn.disabled = true;
    regBtn.textContent = 'Тіркелуде...';
    registerErrorMsg.textContent = '';

    const res = await fetch(`${API_BASE}/admin/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ login: loginVal, password: passVal })
    });

    if (res.status === 400) {
      registerErrorMsg.textContent = 'Бұл логин бос емес (Логин занят)';
      return;
    }

    if (!res.ok) throw new Error('Сервер қатесі');

    const data = await res.json();
    if(data.token) {
      localStorage.setItem('admin_token', data.token);
      showDashboard(data.token);
    }
  } catch (err) {
    registerErrorMsg.textContent = 'Қате: сервермен байланыс жоқ';
  } finally {
    regBtn.disabled = false;
    regBtn.textContent = 'Тіркелу (Регистрация)';
  }
});

// Logout
logoutBtn.addEventListener('click', () => {
  localStorage.removeItem('admin_token');
  showLogin();
});

// Init
checkAuth();
