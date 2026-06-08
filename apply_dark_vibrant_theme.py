import re

def apply_theme():
    # Read the current presentation
    with open('presentation.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Define the new vibrant CSS block
    new_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;900&family=Inter:wght@400;500;700;900&family=JetBrains+Mono&display=swap');

        :root {
            --bg: #020817;
            --p: #0f172a;
            --primary-text: #e5edf8;
            --secondary-text: #94a3b8;
            --accent-blue: #22d3ee;
            --accent-purple: #8b5cf6;
            --accent-green: #34d399;
            --accent-yellow: #fbbf24;
            --accent-red: #fb7185;
            --card-bg: rgba(15, 23, 42, 0.85);
            --surface-bg: rgba(2, 8, 23, 0.7);
            --border-color: rgba(51, 65, 85, 0.6);
            --glow-color: rgba(34, 211, 238, 0.15);
            --accent-gradient: linear-gradient(90deg, #fff, var(--accent-blue), var(--accent-purple));
            --shadow-lg: 0 24px 90px rgba(0, 0, 0, 0.4);
            --radius-lg: 32px;
            --radius-md: 20px;
        }

        .reveal .reveal-viewport,
        .reveal {
            background: var(--bg);
            background-image:
                radial-gradient(circle at 10% 0%, rgba(22, 78, 99, 0.13), transparent 30%),
                radial-gradient(circle at 90% 20%, rgba(109, 40, 217, 0.13), transparent 35%);
            background-color: var(--bg);
        }

        .reveal .slides {
            font-family: 'Inter', sans-serif;
            color: var(--primary-text);
        }

        .reveal h1,
        .reveal h2,
        .reveal h3,
        .reveal h4 {
            font-family: 'Outfit', sans-serif;
            text-transform: none;
            color: var(--primary-text);
            font-weight: 700;
            margin-bottom: 20px;
            letter-spacing: -0.01em;
        }

        .reveal h1 {
            font-size: 3em;
            line-height: 1.1;
            font-weight: 900;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .reveal h2 {
            font-size: 2.4em;
            margin-bottom: 40px;
            position: relative;
            display: inline-block;
        }

        .reveal h2::after {
            content: '';
            position: absolute;
            bottom: -12px;
            left: 0;
            width: 80px;
            height: 6px;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
            border-radius: 10px;
        }

        .reveal p,
        .reveal ul,
        .reveal ol {
            font-size: 1.15em;
            line-height: 1.6;
            color: var(--secondary-text);
            text-align: left;
        }

        .reveal strong {
            color: var(--primary-text);
            font-weight: 600;
        }

        .reveal ul {
            list-style: none;
            padding-left: 0;
        }

        .reveal ul li {
            position: relative;
            padding-left: 40px;
            margin-bottom: 18px;
        }

        .reveal ul li::before {
            content: '\\f00c';
            font-family: 'Font Awesome 6 Free';
            font-weight: 900;
            position: absolute;
            left: 0;
            top: 4px;
            font-size: 0.7em;
            color: #020817;
            background: var(--accent-blue);
            width: 26px;
            height: 26px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            box-shadow: 0 4px 15px rgba(34, 211, 238, 0.4);
        }

        .slide-card {
            background: linear-gradient(180deg, rgba(15,23,42,0.8), rgba(15,23,42,0.5)) !important;
            backdrop-filter: blur(25px) !important;
            -webkit-backdrop-filter: blur(25px) !important;
            border: 1px solid var(--border-color) !important;
            box-shadow: var(--shadow-lg), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
            border-radius: var(--radius-lg);
            padding: 60px;
            width: 95%;
            margin: 0 auto;
            position: relative;
            overflow: hidden;
            color: var(--primary-text);
        }

        .info-box {
            background: var(--card-bg) !important;
            backdrop-filter: blur(10px);
            border: 1px solid var(--border-color) !important;
            border-radius: var(--radius-md);
            padding: 24px;
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05);
            color: var(--primary-text) !important;
        }

        .info-box:hover {
            border-color: var(--accent-blue) !important;
            transform: translateY(-5px);
            box-shadow: 0 0 40px rgba(34, 211, 238, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }

        .glow {
            border-color: rgba(34, 211, 238, 0.4) !important;
            box-shadow: 0 0 60px rgba(34, 211, 238, 0.15) !important;
        }

        .badge {
            display: inline-block;
            padding: 8px 16px;
            background: rgba(34, 211, 238, 0.1) !important;
            color: var(--accent-blue) !important;
            border-radius: 30px;
            font-weight: 600;
            font-size: 0.75em;
            border: 1px solid rgba(34, 211, 238, 0.2) !important;
            text-shadow: 0 0 10px rgba(34, 211, 238, 0.3);
        }

        .modern-table td {
            background: rgba(15, 23, 42, 0.6) !important;
            padding: 18px;
            border: 1px solid var(--border-color) !important;
            color: var(--secondary-text);
        }

        .modern-table tr td:first-child {
            color: var(--primary-text);
            font-weight: 700;
        }

        .reveal .progress {
            height: 4px;
            background: rgba(255, 255, 255, 0.05);
            z-index: 6;
        }

        .reveal .progress span {
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple), #f472b6);
            box-shadow: 0 0 10px var(--accent-blue);
        }
        
        .grad {
            background: linear-gradient(90deg, #fff, var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            color: transparent;
        }
        
        /* Interactive Arch components */
        .arch-box {
            background: rgba(15, 23, 42, 0.8) !important;
            border-color: var(--border-color) !important;
            color: var(--primary-text) !important;
        }
        
        .arch-box i {
            background: var(--accent-gradient) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
        }
        
        .arch-title {
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple)) !important;
            color: #fff !important;
        }
        
        /* Map dots adjustments */
        .traffic-map-overlay .dot {
            box-shadow: 0 0 15px currentColor !important;
        }

        /* SVG Overrides */
        svg text {
            fill: var(--secondary-text) !important;
        }
        svg path, svg line, svg polyline {
            stroke: var(--accent-blue) !important;
        }

    </style>
    """

    # Replace the <style> block
    # Finding the exact style tags
    start_style = html.find('<style>')
    end_style = html.find('</style>') + len('</style>')
    
    if start_style != -1 and end_style != -1:
        html = html[:start_style] + new_css.strip() + html[end_style:]

    # Text replacements to remove hardcoded light colors and backgrounds
    replacements = [
        ("background: white;", ""),
        ("background: #ffffff;", ""),
        ("background: #f8fafc;", ""),
        ("background: #f1f5f9;", ""),
        ("background: #eff6ff;", ""),
        ("background: rgba(255, 255, 255, 0.95);", ""),
        ("background: rgba(255, 255, 255, 0.85);", ""),
        ("background: rgba(255, 255, 255, 0.03);", ""),
        ("background: rgba(255, 255, 255, 0.02);", ""),
        ("color: #0f172a;", ""),
        ("color: var(--primary-text);", ""),
        ("border: 1px solid #f1f5f9;", ""),
        ("border: 1px solid #e2e8f0;", ""),
        ("border-top: 1px solid #f1f5f9;", ""),
        ("border: 1px solid rgba(15, 23, 42, 0.05);", ""),
        ("box-shadow: 0 10px 30px rgba(0,0,0,0.08);", "box-shadow: var(--shadow-lg);"),
        ("color: #64748b;", "color: var(--secondary-text);"),
        ("color: #020617;", "color: var(--primary-text);"),
        ("color: #334155;", "color: var(--secondary-text);"),
        ("color: #475569;", "color: var(--secondary-text);"),
        ("color: #0f172a;", "color: var(--primary-text);"),
        ("background: #e2e8f0;", "background: rgba(255,255,255,0.1);"),
        ("background: #cbd5e1;", "background: rgba(255,255,255,0.2);"),
        ("border-left: 5px solid #ef4444;", "border-left: 5px solid var(--accent-red);"),
        ("border-left: 5px solid #f59e0b;", "border-left: 5px solid var(--accent-yellow);"),
        ("border-left: 5px solid #3b82f6;", "border-left: 5px solid var(--accent-blue);"),
        ("border-left: 5px solid #10b981;", "border-left: 5px solid var(--accent-green);"),
        ("color: #b91c1c;", "color: var(--accent-red);"),
        ("color: #b45309;", "color: var(--accent-yellow);"),
        ("color: #1d4ed8;", "color: var(--accent-blue);"),
        ("color: #047857;", "color: var(--accent-green);"),
        ("color: #2563eb;", "color: var(--accent-blue);"),
        ("color: #7c3aed;", "color: var(--accent-purple);"),
        ("color: #10b981;", "color: var(--accent-green);"),
        ("color: #ef4444;", "color: var(--accent-red);"),
        ("color: #f59e0b;", "color: var(--accent-yellow);"),
    ]

    for old, new in replacements:
        html = html.replace(old, new)
        
    # Also adjust QR code container style if needed
    html = html.replace('style="margin: 0; width: 150px; height: 150px; display: block;"', 'style="margin: 0; width: 150px; height: 150px; display: block; filter: invert(1) hue-rotate(180deg); opacity: 0.8;"')

    with open('presentation_vibrant.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    print("Successfully created presentation_vibrant.html")

if __name__ == "__main__":
    apply_theme()
