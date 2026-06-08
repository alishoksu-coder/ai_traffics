import re

def scan_html():
    with open('presentation.html', 'r', encoding='utf-8') as f:
        content = f.read()

    sections = re.findall(r'<section>(.*?)</section>', content, re.DOTALL)
    
    with open('slide_titles.txt', 'w', encoding='utf-8') as out:
        out.write(f"Total sections found: {len(sections)}\n\n")
        
        for i, sec in enumerate(sections):
            header_match = re.search(r'<h[1-6][^>]*>(.*?)</h[1-6]>', sec, re.DOTALL | re.IGNORECASE)
            if header_match:
                title = re.sub(r'<[^>]+>', '', header_match.group(1)).strip()
                title = re.sub(r'\s+', ' ', title)
            else:
                title = "[No explicit header found]"
                
            out.write(f"Slide {i+1}: {title}\n")

if __name__ == '__main__':
    scan_html()
