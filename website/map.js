// ═══════════════════════════════════════
// Traffic AI — Web Map Dashboard JS
// ═══════════════════════════════════════

// 1. INIT MAP (Leaflet)
const map = L.map('map', {
  zoomControl: false, // We use custom zoom controls
}).setView([51.128, 71.430], 13); // Astana center

// Map Themes
const lightLayer = L.tileLayer('http://mt0.google.com/vt/lyrs=m&hl=kk&x={x}&y={y}&z={z}', {
  attribution: '&copy; Google Maps',
  maxZoom: 20
});

const darkLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; OpenStreetMap & CartoDB (Dark Theme)',
  maxZoom: 20
});

// Default is Light 
lightLayer.addTo(map);
let isDarkTheme = false;

document.getElementById('btn-theme').addEventListener('click', () => {
  isDarkTheme = !isDarkTheme;
  if (isDarkTheme) {
    map.removeLayer(lightLayer);
    darkLayer.addTo(map);
    document.body.classList.add('dark-theme');
  } else {
    map.removeLayer(darkLayer);
    lightLayer.addTo(map);
    document.body.classList.remove('dark-theme');
  }
});

// Custom Controls
document.getElementById('btn-zoom-in').addEventListener('click', () => map.zoomIn());
document.getElementById('btn-zoom-out').addEventListener('click', () => map.zoomOut());
document.getElementById('btn-location').addEventListener('click', () => {
  map.setView([51.128, 71.430], 13);
});

// Layers
let trafficLayerGroup = L.layerGroup().addTo(map);
let arPointsLayerGroup = L.layerGroup().addTo(map);
let vehiclesLayerGroup = L.layerGroup().addTo(map);
let eventsLayerGroup = L.layerGroup().addTo(map);

// Variables
const API_BASE = 'https://ai-traffics.onrender.com';
let currentHorizon = 0;

// 2. TAB SWITCHING
const tabs = document.querySelectorAll('.tab');
const panels = document.querySelectorAll('.tab-panel');

tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    // UI Update
    tabs.forEach(t => t.classList.remove('active'));
    panels.forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(`panel-${tab.dataset.tab}`).classList.add('active');

    // Logic update
    if (tab.dataset.tab === 'traffic') {
      currentHorizon = 0;
      fetchTrafficData(0);
      arPointsLayerGroup.clearLayers();
    } else if (tab.dataset.tab === 'ai') {
      const val = document.getElementById('horizon-slider').value;
      currentHorizon = parseInt(val);
      fetchTrafficData(currentHorizon);
    }
  });
});

// 3. HORIZON SLIDER (AI Tab)
const slider = document.getElementById('horizon-slider');
const horizonText = document.getElementById('selected-horizon');

slider.addEventListener('input', (e) => {
  const val = parseInt(e.target.value);
  currentHorizon = val;
  if (val === 0) horizonText.textContent = "Нақты уақыт";
  else horizonText.textContent = `+${val} минуттан кейін`;
});

slider.addEventListener('change', (e) => {
  const val = parseInt(e.target.value);
  fetchTrafficData(val);
});

// 4. FETCH AND RENDER TRAFFIC DATA
async function fetchTrafficData(horizon) {
  try {
    const res = await fetch(`${API_BASE}/roads/segments?horizon=${horizon}`);
    if (!res.ok) throw new Error("API Error");
    const data = await res.json();

    // Clear old lines
    trafficLayerGroup.clearLayers();

    let totalScore = 0;
    let count = 0;

    data.items.forEach(seg => {
      if (!seg.polyline || seg.polyline.length === 0) return;

      const v = seg.value; // 0 to 100
      totalScore += v;
      count++;

      // Determine color
      let color = '#10B981'; // Green
      let weight = 4;
      if (v > 50) { color = '#F59E0B'; weight = 5; } // Yellow
      if (v >= 80) { color = '#EF4444'; weight = 6; } // Red

      // Leaflet expects [lat, lng], backend gives [lat, lng]
      const poly = L.polyline(seg.polyline, {
        color: color,
        weight: weight,
        opacity: 0.8,
        lineCap: 'round'
      });

      // Tooltip
      poly.bindTooltip(`${seg.name}<br>Жүктелу: ${Math.round(v)}%`, {
        className: 'custom-tooltip', sticky: true
      });

      trafficLayerGroup.addLayer(poly);
    });

    // Update Score UI (0-10 scale)
    if (horizon === 0) {
      const elScore = document.getElementById('score-display');
      const elDesc = document.getElementById('score-desc');

      if (count > 0) {
        const avg = totalScore / count;
        const score10 = Math.ceil(avg / 10);
        elScore.textContent = score10;

        if (score10 <= 3) {
          elScore.style.color = '#10B981'; elScore.style.borderColor = '#10B981';
          elScore.style.background = 'rgba(16, 185, 129, 0.1)';
          elDesc.textContent = "Жолдар бос";
        } else if (score10 <= 6) {
          elScore.style.color = '#F59E0B'; elScore.style.borderColor = '#F59E0B';
          elScore.style.background = 'rgba(245, 158, 11, 0.1)';
          elDesc.textContent = "Қозғалыс тығыз";
        } else {
          elScore.style.color = '#EF4444'; elScore.style.borderColor = '#EF4444';
          elScore.style.background = 'rgba(239, 68, 68, 0.1)';
          elDesc.textContent = "Кептеліс";
        }
      }
    }
  } catch (error) {
    console.error("Traffic Data Error:", error);
    const elScore = document.getElementById('score-display');
    const elDesc = document.getElementById('score-desc');
    elScore.textContent = "!";
    elScore.style.color = '#EF4444';
    elScore.style.borderColor = '#EF4444';
    elDesc.textContent = "Деректер алынбады (Сервер қосылуда...)";
  }
}

// 5. FETCH AR POINTS (Street View)
document.getElementById('btn-ar-points').addEventListener('click', async () => {
  try {
    const res = await fetch(`${API_BASE}/traffic/ar_points?horizon=${currentHorizon}`);
    if (!res.ok) throw new Error("API Error");
    const data = await res.json();

    arPointsLayerGroup.clearLayers();
    const listContainer = document.getElementById('ar-points-list');
    listContainer.innerHTML = '';

    if (data.ar_points.length === 0) {
      listContainer.innerHTML = '<p style="color:#10B981; font-size:13px; font-weight:600;">Бұл уақытта проблемалы зоналар жоқ!</p>';
      return;
    }

    const aiIcon = L.divIcon({
      className: 'custom-div-icon',
      html: "<div style='background-color:#8B5CF6; width:16px; height:16px; border-radius:50%; border:3px solid white; box-shadow:0 2px 5px rgba(0,0,0,0.3);'></div>",
      iconSize: [22, 22],
      iconAnchor: [11, 11]
    });

    data.ar_points.forEach((pt, index) => {
      // Add marker to map
      const marker = L.marker([pt.lat, pt.lng], { icon: aiIcon })
        .bindTooltip(`<b>${pt.segment_name}</b><br>${pt.message}`, { className: 'custom-tooltip' });
      arPointsLayerGroup.addLayer(marker);

      // Add to Sidebar List
      const div = document.createElement('div');
      div.className = `ar-point-card ${pt.level}`;
      div.innerHTML = `
        <strong>${pt.segment_name}</strong>
        <div class="desc">${pt.message}</div>
        <button class="btn btn-primary" style="padding: 6px 12px; font-size: 12px; width: 100%;">
          Street View ашу
        </button>
      `;

      // Click to fly to point and open Street View (simulated in new tab)
      div.addEventListener('click', () => {
        map.flyTo([pt.lat, pt.lng], 16, { duration: 1.5 });
        setTimeout(() => {
          const url = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${pt.lat},${pt.lng}`;
          window.open(url, '_blank');
        }, 1500);
      });

      listContainer.appendChild(div);
    });

    // Fit bounds to show all markers
    if (data.ar_points.length > 0) {
      const group = L.featureGroup(arPointsLayerGroup.getLayers());
      map.fitBounds(group.getBounds(), { padding: [50, 50] });
    }

  } catch (error) {
    console.error("AR Data Error:", error);
  }
});

// INITIAL LOAD
fetchTrafficData(0);

// 5.1 FETCH VEHICLES (LIVE CARS & BUSES)
const carIcon = L.divIcon({
  className: 'custom-div-icon',
  html: "<div style='font-size:20px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.4));'>🚗</div>",
  iconSize: [24, 24],
  iconAnchor: [12, 12]
});

const busIcon = L.divIcon({
  className: 'custom-div-icon',
  html: "<div style='font-size:20px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.4));'>🚌</div>",
  iconSize: [24, 24],
  iconAnchor: [12, 12]
});

async function fetchVehicles() {
  try {
    const res = await fetch(`${API_BASE}/vehicles`);
    if (!res.ok) return;
    const data = await res.json();

    vehiclesLayerGroup.clearLayers();

    data.items.forEach(v => {
      const icon = v.type === 'bus' ? busIcon : carIcon;
      const marker = L.marker([v.lat, v.lon], { icon: icon });
      marker.bindTooltip(`<b>${v.type === 'bus' ? 'Автобус' : 'Көлік'}</b><br>${v.route_name}`, { className: 'custom-tooltip' });
      vehiclesLayerGroup.addLayer(marker);
    });
  } catch (error) {
    console.error("Vehicles Data Error:", error);
  }
}

fetchVehicles();
setInterval(fetchVehicles, 3000); // Update every 3 seconds

// 5.2 FETCH CROWDSOURCED EVENTS
const accidentIcon = L.divIcon({
  className: 'custom-div-icon',
  html: "<div style='font-size:24px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5)); background:rgba(239,68,68,0.2); border-radius:50%; padding:2px;'>💥</div>",
  iconSize: [32, 32],
  iconAnchor: [16, 16]
});

const repairIcon = L.divIcon({
  className: 'custom-div-icon',
  html: "<div style='font-size:24px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5)); background:rgba(245,158,11,0.2); border-radius:50%; padding:2px;'>🚧</div>",
  iconSize: [32, 32],
  iconAnchor: [16, 16]
});

const cameraIcon = L.divIcon({
  className: 'custom-div-icon',
  html: "<div style='font-size:24px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5)); background:rgba(100,116,139,0.2); border-radius:50%; padding:2px;'>📸</div>",
  iconSize: [32, 32],
  iconAnchor: [16, 16]
});

async function fetchEvents() {
  try {
    const res = await fetch(`${API_BASE}/events`);
    if (!res.ok) return;
    const data = await res.json();

    eventsLayerGroup.clearLayers();

    if (data.items) {
      data.items.forEach(e => {
        let icon = accidentIcon;
        let title = 'ДТП (Жол апаты)';
        if (e.event_type === 'repair') { icon = repairIcon; title = 'Ремонт (Жол жөндеу)'; }
        else if (e.event_type === 'camera') { icon = cameraIcon; title = 'Камера'; }

        const marker = L.marker([e.lat, e.lng], { icon: icon });

        const minsAgo = Math.floor((Date.now() / 1000 - e.created_at) / 60);
        let timeStr = minsAgo <= 0 ? 'Жаңа ғана' : `${minsAgo} мин бұрын`;

        marker.bindTooltip(`<b>${title}</b><br><span style="color:gray;font-size:11px;">${timeStr} добавлен</span>`, { className: 'custom-tooltip' });
        eventsLayerGroup.addLayer(marker);
      });
    }
  } catch (error) {
    console.error("Events Data Error:", error);
  }
}

fetchEvents();
setInterval(fetchEvents, 5000); // Poll every 5 seconds

// 5.5 SMART PARKING LOGIC
let parkingLayerGroup = L.layerGroup();
let isParkingVisible = false;

document.getElementById('btn-parking').addEventListener('click', async () => {
  if (isParkingVisible) {
    map.removeLayer(parkingLayerGroup);
    document.getElementById('btn-parking').style.background = 'white';
    isParkingVisible = false;
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/parking`);
    if (!res.ok) throw new Error("API Error");
    const data = await res.json();

    parkingLayerGroup.clearLayers();

    // Create Custom Parking Icon
    const parkingIcon = L.divIcon({
      className: 'custom-div-icon',
      html: "<div style='background-color:#3B82F6; color:white; font-weight:bold; width:24px; height:24px; border-radius:6px; display:flex; align-items:center; justify-content:center; border:2px solid white; box-shadow:0 2px 5px rgba(0,0,0,0.3);'>P</div>",
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });

    data.items.forEach(p => {
      const color = p.available > 20 ? '#10B981' : (p.available > 0 ? '#F59E0B' : '#EF4444');
      const marker = L.marker([p.lat, p.lng], { icon: parkingIcon }).addTo(parkingLayerGroup);

      const popupHtml = `
        <div style="font-family: 'Inter', sans-serif; min-width: 180px;">
          <h4 style="margin:0 0 8px 0; border-bottom:1px solid #eee; padding-bottom:4px;">${p.name}</h4>
          <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
            <span style="color:#64748b; font-size:12px;">Бос орындар:</span>
            <strong style="color:${color};">${p.available}</strong>
          </div>
          <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
            <span style="color:#64748b; font-size:12px;">Сиымдылығы:</span>
            <strong>${p.capacity}</strong>
          </div>
          <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span style="color:#64748b; font-size:12px;">Бағасы:</span>
            <strong>${p.price}</strong>
          </div>
          <button class="btn btn-primary" style="width:100%; padding:6px; font-size:12px;">Орынды брондау</button>
        </div>
      `;
      marker.bindPopup(popupHtml);
    });

    parkingLayerGroup.addTo(map);
    document.getElementById('btn-parking').style.background = '#e2e8f0';
    isParkingVisible = true;

  } catch (error) {
    console.error("Parking Fetch Error:", error);
    alert("Кешіріңіз, парковка деректері жүктелмеді.");
  }
});

// 6. SEARCH LOGIC (Nominatim OSM / 2GIS Style)
const searchInput = document.getElementById('search-input');
const clearBtn = document.getElementById('clear-search');
const searchResults = document.getElementById('search-results');
const mainTabs = document.getElementById('main-tabs');
const panelContent = document.querySelector('.panel-content');

let searchMarkerLayer = L.layerGroup().addTo(map);
let searchTimeout;

searchInput.addEventListener('input', (e) => {
  const query = e.target.value.trim();

  if (query.length > 0) {
    clearBtn.style.display = 'block';
  } else {
    clearBtn.style.display = 'none';
    closeSearch();
    return;
  }

  // Hide main panels and show search results container
  mainTabs.style.display = 'none';
  panelContent.style.display = 'none';
  searchResults.style.display = 'block';

  // Debounce search
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    if (query.length >= 2) performSearch(query);
  }, 500);
});

async function performSearch(query) {
  searchResults.innerHTML = '<div style="padding:20px; text-align:center; color:gray;">Ізделуде...</div>';

  try {
    // OpenStreetMap Nominatim request (Astana focus)
    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)} Astana&format=json&limit=15&viewbox=71.2,51.2,71.6,51.0&bounded=1`;
    const res = await fetch(url);
    const data = await res.json();

    searchResults.innerHTML = '';

    if (data.length === 0) {
      searchResults.innerHTML = '<div style="padding:20px; text-align:center; color:gray;">Ештеңе табылмады</div>';
      return;
    }

    data.forEach(item => {
      const div = document.createElement('div');
      div.className = 'search-result-item';

      // Parse Display Name
      const parts = item.display_name.split(', ');
      const title = parts[0];
      const subtitle = parts.slice(1).join(', ');

      div.innerHTML = `
        <div class="sr-icon">📍</div>
        <div class="sr-text">
          <h4>${title}</h4>
          <p>${subtitle}</p>
        </div>
      `;

      div.addEventListener('click', () => {
        // Clear old marker
        searchMarkerLayer.clearLayers();

        const lat = parseFloat(item.lat);
        const lon = parseFloat(item.lon);

        // Add new marker
        const marker = L.marker([lat, lon]).addTo(searchMarkerLayer);
        marker.bindPopup(`<b>${title}</b><br>${subtitle}`).openPopup();

        // Fly to location
        map.flyTo([lat, lon], 16, { duration: 1.5 });
      });

      searchResults.appendChild(div);
    });

  } catch (error) {
    searchResults.innerHTML = '<div style="padding:20px; text-align:center; color:red;">Іздеу қатесі...</div>';
  }
}

function closeSearch() {
  searchInput.value = '';
  clearBtn.style.display = 'none';
  searchResults.style.display = 'none';
  searchResults.innerHTML = '';
  mainTabs.style.display = 'flex';
  panelContent.style.display = 'block';
  searchMarkerLayer.clearLayers();

  // Return map to center
  map.flyTo([51.128, 71.430], 13);
}

clearBtn.addEventListener('click', closeSearch);

// 7. MAP CLICK REVERSE GEOCODING
map.on('click', async (e) => {
  const lat = e.latlng.lat;
  const lon = e.latlng.lng;

  // Кез-келген жерді басқанда ескі маркерлерді өшіреміз
  searchMarkerLayer.clearLayers();

  // Күту маркерін қоямыз
  const marker = L.marker([lat, lon]).addTo(searchMarkerLayer);
  marker.bindPopup("Ізделуде...").openPopup();

  try {
    // OpenStreetMap Nominatim арқылы координатты мекен-жайға айналдырамыз
    const url = `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json&accept-language=kk`;
    const res = await fetch(url);
    const data = await res.json();

    if (data && data.display_name) {
      const parts = data.display_name.split(', ');
      const title = parts[0];
      const subtitle = parts.length > 1 ? parts.slice(1).join(', ') : 'Астана';

      marker.setPopupContent(`<b>${title}</b><br><span style="font-size:12px;color:gray;">${subtitle}</span>`).openPopup();

      // Іздеу жолағына атын жазып қою
      searchInput.value = title;
      clearBtn.style.display = 'block';
    } else {
      marker.setPopupContent("Белгісіз аймақ").openPopup();
    }
  } catch (error) {
    marker.setPopupContent("Қателік орын алды").openPopup();
  }
});
