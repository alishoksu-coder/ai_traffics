// ═══════════════════════════════════════
// Traffic AI — Web Map Dashboard JS
// ═══════════════════════════════════════

// 1. INIT MAP (Leaflet)
const map = L.map('map', {
  zoomControl: false, // We use custom zoom controls
}).setView([51.128, 71.430], 13); // Astana center

// Add Light modern map tiles (CartoDB Positron is very clean)
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; OpenStreetMap & Traffic AI',
  subdomains: 'abcd',
  maxZoom: 19
}).addTo(map);

// Custom Controls
document.getElementById('btn-zoom-in').addEventListener('click', () => map.zoomIn());
document.getElementById('btn-zoom-out').addEventListener('click', () => map.zoomOut());
document.getElementById('btn-location').addEventListener('click', () => {
  map.setView([51.128, 71.430], 13);
});

// Layers
let trafficLayerGroup = L.layerGroup().addTo(map);
let arPointsLayerGroup = L.layerGroup().addTo(map);

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
