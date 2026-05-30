"""
Task 8: Generate UML Component Diagram and DFD Level-0 for diploma.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ===== 1. COMPONENT DIAGRAM =====
fig, ax = plt.subplots(1, 1, figsize=(16, 10))
ax.set_xlim(0, 16)
ax.set_ylim(0, 10)
ax.axis('off')
ax.set_title('AI Traffic жүйесінің компонент диаграммасы', fontsize=16, fontweight='bold', pad=20)

def draw_box(ax, x, y, w, h, text, color='#E3F2FD', edge='#1976D2', fontsize=9):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1", 
                          facecolor=color, edgecolor=edge, linewidth=2)
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fontsize, fontweight='bold')

def draw_arrow(ax, x1, y1, x2, y2, label=''):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#333', lw=1.5))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my+0.15, label, ha='center', fontsize=7, color='#555')

# Client Layer
draw_box(ax, 0.5, 8, 3.5, 1.2, 'Flutter Mobile App\n(Android/iOS)', '#E8F5E9', '#388E3C', 10)
draw_box(ax, 4.5, 8, 3.5, 1.2, 'Web Dashboard\n(HTML5/JS/Leaflet)', '#E8F5E9', '#388E3C', 10)
draw_box(ax, 8.5, 8, 3.5, 1.2, 'Admin Panel\n(admin.html)', '#E8F5E9', '#388E3C', 10)

# API Gateway
draw_box(ax, 3, 5.8, 6, 1.2, 'FastAPI Server (main.py)\nREST API Gateway', '#E3F2FD', '#1976D2', 11)

# Backend modules
draw_box(ax, 0.3, 3.5, 2.5, 1.2, 'Traffic Simulator\n(simulate.py)', '#FFF3E0', '#E65100', 9)
draw_box(ax, 3.2, 3.5, 2.5, 1.2, 'Prediction Engine\n(predict.py)', '#FFF3E0', '#E65100', 9)
draw_box(ax, 6.1, 3.5, 2.5, 1.2, 'AI Brain\n(ai_brain.py)', '#FFF3E0', '#E65100', 9)
draw_box(ax, 9, 3.5, 2.5, 1.2, 'Anomaly Detector\n(predict.py)', '#FFF3E0', '#E65100', 9)
draw_box(ax, 12, 3.5, 2.5, 1.2, 'Weather Service\n(weather.py)', '#FFF3E0', '#E65100', 9)

# Data Layer
draw_box(ax, 2, 1.2, 3, 1.2, 'SQLite / Supabase\nDeректер қоры', '#FCE4EC', '#C62828', 10)
draw_box(ax, 6, 1.2, 3, 1.2, 'OSRM Routing\nEngine', '#FCE4EC', '#C62828', 10)
draw_box(ax, 10, 1.2, 3, 1.2, 'External APIs\n(wttr.in, Google Maps)', '#FCE4EC', '#C62828', 10)

# Arrows: Client -> API
draw_arrow(ax, 2.25, 8, 5, 7, 'REST API')
draw_arrow(ax, 6.25, 8, 6, 7, 'HTTP/JSON')
draw_arrow(ax, 10.25, 8, 7, 7, 'REST API')

# Arrows: API -> Backend
draw_arrow(ax, 4.5, 5.8, 1.55, 4.7)
draw_arrow(ax, 5.5, 5.8, 4.45, 4.7)
draw_arrow(ax, 6.5, 5.8, 7.35, 4.7)
draw_arrow(ax, 7.5, 5.8, 10.25, 4.7)
draw_arrow(ax, 8, 5.8, 13.25, 4.7)

# Arrows: Backend -> Data
draw_arrow(ax, 1.55, 3.5, 3.5, 2.4)
draw_arrow(ax, 4.45, 3.5, 3.5, 2.4)
draw_arrow(ax, 7.35, 3.5, 7.5, 2.4)
draw_arrow(ax, 13.25, 3.5, 11.5, 2.4)

# Layer labels
ax.text(0.2, 9.4, 'Клиент қабаты (Client Layer)', fontsize=11, fontweight='bold', color='#388E3C')
ax.text(0.2, 7.2, 'Сервер қабаты (Server Layer)', fontsize=11, fontweight='bold', color='#1976D2')
ax.text(0.2, 5, 'Аналитикалық модульдер', fontsize=11, fontweight='bold', color='#E65100')
ax.text(0.2, 2.6, 'Деректер қабаты (Data Layer)', fontsize=11, fontweight='bold', color='#C62828')

plt.tight_layout()
plt.savefig('component_diagram.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("Component diagram saved: component_diagram.png")

# ===== 2. DFD LEVEL-0 =====
fig, ax = plt.subplots(1, 1, figsize=(14, 9))
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis('off')
ax.set_title('AI Traffic жүйесінің деректер ағыны диаграммасы (DFD Level-0)', fontsize=14, fontweight='bold', pad=20)

def draw_circle(ax, x, y, r, text, color='#E3F2FD', edge='#1976D2'):
    circle = plt.Circle((x, y), r, facecolor=color, edgecolor=edge, linewidth=2)
    ax.add_patch(circle)
    ax.text(x, y, text, ha='center', va='center', fontsize=9, fontweight='bold')

def draw_rect(ax, x, y, w, h, text, color='#FFF3E0', edge='#E65100'):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                           facecolor=color, edgecolor=edge, linewidth=2)
    ax.add_patch(rect)
    ax.text(x+w/2, y+h/2, text, ha='center', va='center', fontsize=9, fontweight='bold')

def draw_store(ax, x, y, w, h, text):
    ax.plot([x, x+w], [y+h, y+h], color='#333', linewidth=2)
    ax.plot([x, x+w], [y, y], color='#333', linewidth=2)
    ax.text(x+w/2, y+h/2, text, ha='center', va='center', fontsize=9, fontweight='bold')

# External entities (rectangles)
draw_rect(ax, 0.5, 7, 2.5, 1, 'Пайдаланушы\n(Жүргізуші)', '#E8F5E9', '#388E3C')
draw_rect(ax, 11, 7, 2.5, 1, 'Әкімші\n(Диспетчер)', '#E8F5E9', '#388E3C')
draw_rect(ax, 0.5, 1, 2.5, 1, 'Сыртқы API\n(wttr.in, OSRM)', '#FCE4EC', '#C62828')

# Processes (circles)
draw_circle(ax, 4.5, 5, 1.2, '1.0\nТрафикті\nсимуляциялау', '#E3F2FD', '#1976D2')
draw_circle(ax, 9.5, 5, 1.2, '2.0\nБолжам\nжасау', '#E3F2FD', '#1976D2')
draw_circle(ax, 7, 2.5, 1.2, '3.0\nАномалия\nанықтау', '#E3F2FD', '#1976D2')
draw_circle(ax, 11.5, 2.5, 1.2, '4.0\nНәтижелерді\nтарату', '#E3F2FD', '#1976D2')

# Data stores
draw_store(ax, 5.5, 7.2, 3, 0.6, 'D1: traffic_data')
draw_store(ax, 5.5, 0.5, 3, 0.6, 'D2: locations')

# Arrows with labels
draw_arrow(ax, 3, 7.2, 4, 6.2, 'GPS координаттар')
draw_arrow(ax, 4.8, 6.2, 5.5, 7.3, 'Жүктеме деректері')
draw_arrow(ax, 8.5, 7.2, 9, 6.2, '')
draw_arrow(ax, 5.7, 5, 8.3, 5, 'Тарихи деректер')
draw_arrow(ax, 9.5, 3.8, 9, 3.2, '')
draw_arrow(ax, 8.2, 2.5, 10.3, 2.5, 'Аномалия нәтижесі')
draw_arrow(ax, 11.5, 3.7, 11.5, 7, 'Ескертулер')
draw_arrow(ax, 3, 1.5, 5, 2, 'Ауа райы деректері')
draw_arrow(ax, 4.5, 3.8, 6, 1.1, '')
draw_arrow(ax, 12.7, 2.5, 12.5, 5, '')

ax.text(10, 6, 'Болжам\nнәтижелері', fontsize=7, color='#555')

plt.tight_layout()
plt.savefig('dfd_diagram.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("DFD diagram saved: dfd_diagram.png")

print("\nAll diagrams generated!")
