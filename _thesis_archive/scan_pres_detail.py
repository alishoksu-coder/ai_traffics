# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import re

with open('presentation.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all slide sections with class info
slides = re.findall(r'<section[^>]*>(.*?)</section>', content, re.DOTALL)

for i, slide in enumerate(slides):
    # Extract title
    title_match = re.search(r'<h[1-3][^>]*>(.*?)</h[1-3]>', slide, re.DOTALL)
    title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip() if title_match else "No title"
    title = ' '.join(title.split())[:120]
    
    # Extract key text points
    items = re.findall(r'<li[^>]*>(.*?)</li>', slide, re.DOTALL)
    clean_items = [re.sub(r'<[^>]+>', '', item).strip()[:100] for item in items[:5]]
    
    # Check for tables, images, diagrams
    has_table = '<table' in slide
    has_img = '<img' in slide
    has_svg = '<svg' in slide or 'diagram' in slide.lower()
    has_chart = 'chart' in slide.lower() or 'график' in slide.lower()
    has_compare = 'салыстыр' in slide.lower() or 'compare' in slide.lower()
    
    markers = []
    if has_table: markers.append('TABLE')
    if has_img: markers.append('IMAGE')
    if has_svg: markers.append('SVG/DIAGRAM')
    if has_chart: markers.append('CHART')
    if has_compare: markers.append('COMPARE')
    
    print(f"\n--- Slide {i+1}: {title}")
    if markers:
        print(f"    Content: {', '.join(markers)}")
    if clean_items:
        for item in clean_items:
            print(f"    • {item}")
