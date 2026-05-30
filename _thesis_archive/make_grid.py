import os
from PIL import Image, ImageDraw, ImageFont

media_dir = "temp_word_extract/word/media"
images = [f for f in os.listdir(media_dir) if os.path.getsize(os.path.join(media_dir, f)) < 10000]

# sort images logically
images.sort(key=lambda x: int(x.replace('image', '').split('.')[0]))

grid_w, grid_h = 1000, 2000
grid = Image.new('RGB', (grid_w, grid_h), color=(255, 255, 255))
draw = ImageDraw.Draw(grid)

x, y = 10, 10
max_h = 0
for img_name in images:
    img_path = os.path.join(media_dir, img_name)
    try:
        img = Image.open(img_path)
        img.thumbnail((300, 300))
        
        # draw text label
        draw.text((x, y), img_name, fill=(0,0,0))
        y += 15
        
        grid.paste(img, (x, y))
        w, h = img.size
        
        y += h + 20
        if y > grid_h - 200:
            y = 10
            x += 350
    except Exception as e:
        print(f"Error with {img_name}: {e}")

grid.save("formula_grid.png")
print("Saved formula_grid.png")
