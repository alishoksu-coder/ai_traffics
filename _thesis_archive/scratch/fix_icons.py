import os

file_path = r"c:\Users\user\Downloads\ai_traffic_fullstack\presentation.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

old_block = """
                            <div
                                style="background: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; width: 40%;">
                                <div style="font-size: 2.5em;">💥</div>
                                <div style="font-weight: 700; margin-top: 10px; color: #ef4444;">Жол апаты</div>
                            </div>
                            <div
                                style="background: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; width: 40%;">
                                <div style="font-size: 2.5em;">🚧</div>
                                <div style="font-weight: 700; margin-top: 10px; color: #f59e0b;">Жол жөндеу</div>
                            </div>
                            <div
                                style="background: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; width: 40%;">
                                <div style="font-size: 2.5em;">📸</div>
                                <div style="font-weight: 700; margin-top: 10px; color: #64748b;">Камера</div>
                            </div>
"""

new_block = """
                            <div class="interactive-row" style="background: linear-gradient(145deg, #ffffff, #f1f5f9); padding: 20px; border-radius: 20px; box-shadow: 0 10px 20px rgba(239, 68, 68, 0.1), inset 0 2px 0 rgba(255,255,255,1); text-align: center; width: 45%; border: 1px solid rgba(239, 68, 68, 0.1);">
                                <div style="position: relative; display: inline-flex; justify-content: center; align-items: center; width: 70px; height: 70px; background: #fff1f2; border-radius: 50%; box-shadow: inset 0 4px 8px rgba(239,68,68,0.2), 0 8px 16px rgba(239,68,68,0.2); margin-bottom: 10px;">
                                    <div style="position: absolute; width: 100%; height: 100%; background: #ef4444; filter: blur(15px); opacity: 0.3; border-radius: 50%;"></div>
                                    <i class="fa-solid fa-car-burst" style="font-size: 2em; color: #ef4444; position: relative; z-index: 1; filter: drop-shadow(0 2px 4px rgba(239, 68, 68, 0.4));"></i>
                                </div>
                                <div style="font-weight: 800; margin-top: 5px; color: #b91c1c; font-size: 1.1em; letter-spacing: -0.5px;">Жол апаты</div>
                            </div>
                            <div class="interactive-row" style="background: linear-gradient(145deg, #ffffff, #f1f5f9); padding: 20px; border-radius: 20px; box-shadow: 0 10px 20px rgba(245, 158, 11, 0.1), inset 0 2px 0 rgba(255,255,255,1); text-align: center; width: 45%; border: 1px solid rgba(245, 158, 11, 0.1);">
                                <div style="position: relative; display: inline-flex; justify-content: center; align-items: center; width: 70px; height: 70px; background: #fffbeb; border-radius: 50%; box-shadow: inset 0 4px 8px rgba(245,158,11,0.2), 0 8px 16px rgba(245,158,11,0.2); margin-bottom: 10px;">
                                    <div style="position: absolute; width: 100%; height: 100%; background: #f59e0b; filter: blur(15px); opacity: 0.3; border-radius: 50%;"></div>
                                    <i class="fa-solid fa-person-digging" style="font-size: 2em; color: #f59e0b; position: relative; z-index: 1; filter: drop-shadow(0 2px 4px rgba(245, 158, 11, 0.4));"></i>
                                </div>
                                <div style="font-weight: 800; margin-top: 5px; color: #b45309; font-size: 1.1em; letter-spacing: -0.5px;">Жол жөндеу</div>
                            </div>
                            <div class="interactive-row" style="background: linear-gradient(145deg, #ffffff, #f1f5f9); padding: 20px; border-radius: 20px; box-shadow: 0 10px 20px rgba(100, 116, 139, 0.1), inset 0 2px 0 rgba(255,255,255,1); text-align: center; width: 45%; border: 1px solid rgba(100, 116, 139, 0.1);">
                                <div style="position: relative; display: inline-flex; justify-content: center; align-items: center; width: 70px; height: 70px; background: #f8fafc; border-radius: 50%; box-shadow: inset 0 4px 8px rgba(100,116,139,0.2), 0 8px 16px rgba(100,116,139,0.2); margin-bottom: 10px;">
                                    <div style="position: absolute; width: 100%; height: 100%; background: #64748b; filter: blur(15px); opacity: 0.3; border-radius: 50%;"></div>
                                    <i class="fa-solid fa-video" style="font-size: 2em; color: #64748b; position: relative; z-index: 1; filter: drop-shadow(0 2px 4px rgba(100, 116, 139, 0.4));"></i>
                                </div>
                                <div style="font-weight: 800; margin-top: 5px; color: #475569; font-size: 1.1em; letter-spacing: -0.5px;">Камера</div>
                            </div>
"""

# Try to replace it
if old_block.strip() in content:
    content = content.replace(old_block.strip(), new_block.strip())
else:
    # If indentation makes exact matching fail, let's use a simpler replace
    content = content.replace('<div style="font-size: 2.5em;">💥</div>', '<div style="position: relative; display: inline-flex; justify-content: center; align-items: center; width: 70px; height: 70px; background: #fff1f2; border-radius: 50%; box-shadow: inset 0 4px 8px rgba(239,68,68,0.2), 0 8px 16px rgba(239,68,68,0.2); margin-bottom: 10px;"><div style="position: absolute; width: 100%; height: 100%; background: #ef4444; filter: blur(15px); opacity: 0.3; border-radius: 50%;"></div><i class="fa-solid fa-car-burst" style="font-size: 2em; color: #ef4444; position: relative; z-index: 1; filter: drop-shadow(0 2px 4px rgba(239, 68, 68, 0.4));"></i></div>')
    content = content.replace('<div style="font-size: 2.5em;">🚧</div>', '<div style="position: relative; display: inline-flex; justify-content: center; align-items: center; width: 70px; height: 70px; background: #fffbeb; border-radius: 50%; box-shadow: inset 0 4px 8px rgba(245,158,11,0.2), 0 8px 16px rgba(245,158,11,0.2); margin-bottom: 10px;"><div style="position: absolute; width: 100%; height: 100%; background: #f59e0b; filter: blur(15px); opacity: 0.3; border-radius: 50%;"></div><i class="fa-solid fa-person-digging" style="font-size: 2em; color: #f59e0b; position: relative; z-index: 1; filter: drop-shadow(0 2px 4px rgba(245, 158, 11, 0.4));"></i></div>')
    content = content.replace('<div style="font-size: 2.5em;">📸</div>', '<div style="position: relative; display: inline-flex; justify-content: center; align-items: center; width: 70px; height: 70px; background: #f8fafc; border-radius: 50%; box-shadow: inset 0 4px 8px rgba(100,116,139,0.2), 0 8px 16px rgba(100,116,139,0.2); margin-bottom: 10px;"><div style="position: absolute; width: 100%; height: 100%; background: #64748b; filter: blur(15px); opacity: 0.3; border-radius: 50%;"></div><i class="fa-solid fa-video" style="font-size: 2em; color: #64748b; position: relative; z-index: 1; filter: drop-shadow(0 2px 4px rgba(100, 116, 139, 0.4));"></i></div>')

    content = content.replace('<div style="font-weight: 700; margin-top: 10px; color: #ef4444;">Жол апаты</div>', '<div style="font-weight: 800; margin-top: 5px; color: #b91c1c; font-size: 1.1em; letter-spacing: -0.5px;">Жол апаты</div>')
    content = content.replace('<div style="font-weight: 700; margin-top: 10px; color: #f59e0b;">Жол жөндеу</div>', '<div style="font-weight: 800; margin-top: 5px; color: #b45309; font-size: 1.1em; letter-spacing: -0.5px;">Жол жөндеу</div>')
    content = content.replace('<div style="font-weight: 700; margin-top: 10px; color: #64748b;">Камера</div>', '<div style="font-weight: 800; margin-top: 5px; color: #475569; font-size: 1.1em; letter-spacing: -0.5px;">Камера</div>')
    
with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Icons replaced successfully.")
