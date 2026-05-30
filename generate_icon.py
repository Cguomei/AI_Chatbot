"""
生成桌游排行应用图标 (.ico)
"""
from PIL import Image, ImageDraw, ImageFont

SIZE = 256

def create_icon():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # === 圆角方形背景 ===
    margin = 20
    r = 48
    # 渐变底色：紫色到靛蓝
    for i in range(SIZE):
        ratio = i / SIZE
        r_val = int(99 - ratio * 30)
        g_val = int(102 - ratio * 20)
        b_val = int(241 - ratio * 40)
        draw.rounded_rectangle([margin, i, SIZE - margin, i + 1], 
                              radius=0, 
                              fill=(r_val, g_val, b_val, 255))
    # 整体圆角裁剪
    mask = Image.new("L", (SIZE, SIZE), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([margin, margin, SIZE - margin, SIZE - margin], 
                                 radius=r, fill=255)
    img.putalpha(mask)

    # === 重新创建带渐变背景的图 ===
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 绘制渐变圆角背景
    for y in range(margin, SIZE - margin):
        ratio = (y - margin) / (SIZE - 2 * margin)
        r_val = int(67 - ratio * 25)   # 上浅下深
        g_val = int(70 - ratio * 20)
        b_val = int(230 - ratio * 50)
        draw.line([(margin, y), (SIZE - margin, y)], fill=(r_val, g_val, b_val, 255))

    # 圆角裁剪
    mask2 = Image.new("L", (SIZE, SIZE), 0)
    mask_d2 = ImageDraw.Draw(mask2)
    mask_d2.rounded_rectangle([margin, margin, SIZE - margin, SIZE - margin], 
                               radius=r, fill=255)
    img.putalpha(mask2)

    # === 绘制奖杯图标 ===
    cx, cy = SIZE // 2, SIZE // 2 - 10
    gold = (255, 215, 0, 255)
    gold_dark = (218, 165, 32, 255)
    gold_light = (255, 235, 150, 255)
    white_semi = (255, 255, 255, 180)

    draw = ImageDraw.Draw(img)

    # 奖杯杯身 (梯形)
    body_top = cy - 55
    body_bot = cy + 30
    body_w_top = 44
    body_w_bot = 30
    draw.polygon([
        (cx - body_w_top, body_top),
        (cx + body_w_top, body_top),
        (cx + body_w_bot, body_bot),
        (cx - body_w_bot, body_bot),
    ], fill=gold)

    # 杯身高光
    draw.polygon([
        (cx - body_w_top, body_top),
        (cx - body_w_top + 20, body_top + 10),
        (cx - body_w_bot + 10, body_bot),
        (cx - body_w_bot, body_bot),
    ], fill=gold_light)

    # 奖杯把手
    handle_w = 18
    handle_h = 45
    draw.arc([cx - body_w_top - handle_w, body_top + 8, 
              cx - body_w_top + handle_w, body_top + 8 + handle_h],
             start=270, end=90, fill=gold_dark, width=10)
    draw.arc([cx + body_w_top - handle_w, body_top + 8,
              cx + body_w_top + handle_w, body_top + 8 + handle_h],
             start=270, end=90, fill=gold_dark, width=10)

    # 奖杯底座
    base_w = 50
    base_h = 14
    draw.rounded_rectangle([cx - base_w, body_bot - 4, cx + base_w, body_bot + base_h],
                            radius=6, fill=gold_dark)
    # 底座高光
    draw.rounded_rectangle([cx - base_w + 4, body_bot - 2, cx + base_w - 4, body_bot + base_h - 6],
                            radius=4, fill=gold_light)

    # 顶部星星
    star_size = 16
    star_y = body_top - 18
    star_pts = [
        (cx, star_y - star_size),
        (cx + star_size // 3, star_y - 2),
        (cx + star_size + 6, star_y),
        (cx + star_size // 3, star_y + 4),
        (cx + star_size // 2 + 5, star_y + 16),
        (cx, star_y + 8),
        (cx - star_size // 2 - 5, star_y + 16),
        (cx - star_size // 3, star_y + 4),
        (cx - star_size - 6, star_y),
        (cx - star_size // 3, star_y - 2),
    ]
    draw.polygon(star_pts, fill=(255, 255, 255, 240))

    # === 保存多尺寸 ICO ===
    sizes = [256, 128, 64, 48, 32, 16]
    icons = []
    for s in sizes:
        resized = img.resize((s, s), Image.LANCZOS)
        icons.append(resized)

    icons[0].save("icon.ico", format="ICO", sizes=[(s, s) for s in sizes], append_images=icons[1:])
    print("icon.ico generated (256/128/64/48/32/16)")

if __name__ == "__main__":
    try:
        from PIL import Image, ImageDraw
        create_icon()
    except ImportError:
        print("⚠️  需要 Pillow 库: pip install Pillow")
        import sys
        sys.exit(1)
