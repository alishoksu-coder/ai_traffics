# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Read presentation.html to find slides with images and content
with open('presentation.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Find all slide sections
slides = re.findall(r'<section[^>]*>(.*?)</section>', content, re.DOTALL)
print(f"Total slides found: {len(slides)}")

for i, slide in enumerate(slides):
    # Extract title if any
    title_match = re.search(r'<h[1-3][^>]*>(.*?)</h[1-3]>', slide, re.DOTALL)
    title = title_match.group(1) if title_match else "No title"
    # Clean HTML
    title = re.sub(r'<[^>]+>', '', title).strip()
    
    # Check for images
    images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', slide)
    
    # Check for figure captions 
    captions = re.findall(r'(?:Сурет|сурет|Figure)\s*\d+', slide)
    
    # Check for comparison tables
    tables = slide.count('<table')
    
    has_content = bool(images or tables or captions)
    
    if has_content or i < 5:
        print(f"\nSlide {i+1}: {title[:100]}")
        if images:
            print(f"  Images: {images}")
        if tables:
            print(f"  Tables: {tables}")
        if captions:
            print(f"  Captions: {captions}")
