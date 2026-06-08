import os
import re

html_path = r"c:\Users\user\Downloads\ai_traffic_fullstack\presentation.html"
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# Split the document into head+start of slides, slides content, and end of document
slides_start = html.find('<div class="slides">') + len('<div class="slides">')
slides_end = html.rfind('<!-- Floating Toolbar -->')
if slides_end == -1:
    slides_end = html.rfind('</div>\n    </div>')

prefix = html[:slides_start]
slides_content = html[slides_start:slides_end]
suffix = html[slides_end:]

# Parse top-level <section> tags
slides = []
buffer = ""
depth = 0
in_tag = False

# We will just split by <section and </section> using regex and count depth
tokens = re.split(r'(</?section[^>]*>)', slides_content)

current_slide = ""
for token in tokens:
    if token.startswith('<section'):
        if depth == 0:
            current_slide += token
        else:
            current_slide += token
        depth += 1
    elif token.startswith('</section>'):
        depth -= 1
        current_slide += token
        if depth == 0:
            slides.append(current_slide)
            current_slide = ""
    else:
        current_slide += token

# Some tokens before the first <section> might be in current_slide, we should prepend them to the first slide
if current_slide.strip() and not slides:
    # No slides found?
    pass
elif current_slide.strip() and slides:
    # trailing whitespace
    pass

# We have our slides list. Let's filter them based on their content/comments.
# We want to keep slides that contain certain keywords indicating facts/features.

keep_keywords = [
    "1. Титульный слайд",
    "2. Актуальность темы",
    "NEW SLIDE: Specific Problems Solved (1.1)",
    "8. Жүйенің Контейнерлік Архитектурасы",
    "14. ML Алгоритм: LSTM Нейрондық Желісі",
    "17. Болжамдау Метрикалары",
    "11.5 Цифрлық егіз",
    "12. Аномалияларды анықтау",
    "13. Z-Score",
    "18. NLP",
    "19. Web Admin",
    "Финальный слайд"
]

filtered_slides = []
for idx, slide in enumerate(slides):
    # check if any keep_keyword is in the slide
    keep = False
    for kw in keep_keywords:
        if kw in slide:
            keep = True
            break
    
    # Also we might have lost the preceding comments because they were in `current_slide` before <section>.
    # Wait, my token parser appends non-section tokens to `current_slide`. So the comments BEFORE a <section> will be included in the SAME slide if they appeared after the PREVIOUS </section>.
    # EXCEPT for the first slide, where comments are at the start of `slides_content`.
    if keep:
        filtered_slides.append(slide)

# Write back
new_html = prefix + "".join(filtered_slides) + suffix

with open(html_path, "w", encoding="utf-8") as f:
    f.write(new_html)

print(f"Original slides: {len(slides)}")
print(f"Filtered slides: {len(filtered_slides)}")
