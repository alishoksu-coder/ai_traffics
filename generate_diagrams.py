import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_architecture():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Draw blocks
    blocks = [
        {"x": 10, "y": 70, "w": 25, "h": 15, "text": "Mobile Client\n(Flutter/Dart)\nGlassmorphism UI"},
        {"x": 10, "y": 40, "w": 25, "h": 15, "text": "Web Dashboard\n(HTML/CSS/JS)\nAdmin Panel"},
        {"x": 50, "y": 55, "w": 25, "h": 20, "text": "Backend Server\n(FastAPI / Python)\nREST API & Logic"},
        {"x": 85, "y": 75, "w": 15, "h": 15, "text": "Database\n(Supabase/\nPostgreSQL)"},
        {"x": 85, "y": 40, "w": 15, "h": 15, "text": "Local DB\n(SQLite)\nTraffic Data"},
        {"x": 50, "y": 20, "w": 25, "h": 15, "text": "AI Brain Engine\n(Scikit-Learn/LSTM)\nAnomaly Detection"}
    ]

    for b in blocks:
        rect = patches.Rectangle((b["x"], b["y"]), b["w"], b["h"], linewidth=2, edgecolor='black', facecolor='#e6f2ff')
        ax.add_patch(rect)
        ax.text(b["x"] + b["w"]/2, b["y"] + b["h"]/2, b["text"], ha='center', va='center', fontsize=9, fontweight='bold')

    # Arrows
    arrow_props = dict(facecolor='black', edgecolor='black', shrink=0.05, width=1.5, headwidth=6)
    ax.annotate('', xy=(50, 65), xytext=(35, 77), arrowprops=arrow_props)
    ax.annotate('', xy=(50, 60), xytext=(35, 47), arrowprops=arrow_props)
    
    ax.annotate('', xy=(85, 82), xytext=(75, 65), arrowprops=arrow_props)
    ax.annotate('', xy=(85, 47), xytext=(75, 55), arrowprops=arrow_props)
    
    ax.annotate('', xy=(62.5, 35), xytext=(62.5, 55), arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=8))
    
    plt.title("Рис. 1 - AI Traffic Client-Server Architecture", fontsize=14, fontweight='bold', y=1.05)
    plt.savefig('diag_architecture.png', bbox_inches='tight', dpi=300)
    print("diag_architecture.png generated")
    plt.close()

def draw_lstm():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    rect = patches.Rectangle((20, 20), 60, 60, linewidth=3, edgecolor='navy', facecolor='#f0f0f5', linestyle='--')
    ax.add_patch(rect)
    ax.text(50, 85, "LSTM Cell Architecture", ha='center', fontsize=12, fontweight='bold', color='navy')

    # Gates
    gates = [
        {"x": 25, "y": 40, "text": "Forget\nGate ($f_t$)"},
        {"x": 45, "y": 40, "text": "Input\nGate ($i_t$)"},
        {"x": 65, "y": 40, "text": "Output\nGate ($o_t$)"}
    ]
    for g in gates:
        circle = patches.Circle((g["x"]+5, g["y"]+5), 8, linewidth=2, edgecolor='darkred', facecolor='#ffcccc')
        ax.add_patch(circle)
        ax.text(g["x"]+5, g["y"]+5, g["text"], ha='center', va='center', fontsize=8, fontweight='bold')

    ax.annotate('', xy=(25, 45), xytext=(20, 10), arrowprops=dict(facecolor='black', shrink=0.01, width=1))
    ax.text(18, 5, "$X_t$ (Input)", fontsize=10)
    
    ax.annotate('', xy=(30, 48), xytext=(80, 48), arrowprops=dict(facecolor='black', shrink=0.01, width=2))
    ax.text(82, 48, "$C_t$\n(Cell State)", fontsize=10)

    plt.title("Рис. 2 - Математическая модель клетки LSTM", fontsize=14, fontweight='bold', y=1.05)
    plt.savefig('diag_lstm.png', bbox_inches='tight', dpi=300)
    print("diag_lstm.png generated")
    plt.close()

def draw_digital_twin():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    steps = [
        {"x": 5, "y": 40, "text": "Raw Data\n(10,000 Nodes)"},
        {"x": 35, "y": 40, "text": "Digital Twin\nInfrastructure\n(Ramps, Stairs)"},
        {"x": 65, "y": 40, "text": "A-Star AI\nBarrier Penalty"}
    ]
    for i, s in enumerate(steps):
        r = patches.Rectangle((s["x"], s["y"]), 20, 20, linewidth=2, edgecolor='green', facecolor='#e6ffe6')
        ax.add_patch(r)
        ax.text(s["x"]+10, s["y"]+10, s["text"], ha='center', va='center', fontsize=10, fontweight='bold')
        if i < 2:
            ax.annotate('', xy=(steps[i+1]["x"], 50), xytext=(s["x"]+20, 50), arrowprops=dict(facecolor='black', width=2))
            
    # Result
    r = patches.Rectangle((90, 45), 10, 10, edgecolor='red', facecolor='red')
    ax.add_patch(r)
    ax.annotate('', xy=(90, 50), xytext=(85, 50), arrowprops=dict(facecolor='black', width=2))
    ax.text(95, 50, "Safe\nRoute", ha='center', va='center', color='white', fontweight='bold')

    plt.title("Рис. 3 - Генерация Инклюзивного Маршрута (Кедергісіз)", fontsize=14, fontweight='bold', y=1.05)
    plt.savefig('diag_twin.png', bbox_inches='tight', dpi=300)
    print("diag_twin.png generated")
    plt.close()

if __name__ == "__main__":
    draw_architecture()
    draw_lstm()
    draw_digital_twin()
