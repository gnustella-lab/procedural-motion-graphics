# Kinetic Typography & Track Mattes

High-impact motion design relies heavily on expressive kinetic typography. This document covers letter stagger, tracking measurements, 3D faux extrusions, and luminance track mattes.

---

## 1. Font Metrics & Kerning Preservation

When animating individual letters, you must preserve original kerning and proportional tracking:

```python
# Measure total phrase width
bbox = draw.textbbox((0, 0), word, font=font)
total_width = bbox[2] - bbox[0]
start_x = center_x - total_width / 2

accumulated_x = 0
for i, char in enumerate(word):
    char_width = draw.textlength(char, font=font)
    
    # Position letter accurately along baseline
    draw.text((start_x + accumulated_x, y), char, font=font, fill=color, anchor="lm")
    accumulated_x += char_width
```

---

## 2. Chromatic 3D Faux Extrusions

Instead of simple drop shadows, offset chromatic color layers behind the hero glyph:

```python
# 1. Back pink shadow shifted down-right (+8, +8)
draw.text((x + 8, y + 8), char, font=font, fill=PINK + (150,), anchor="mm")

# 2. Cyan accent shadow shifted up-left (-8, -4)
draw.text((x - 8, y - 4), char, font=font, fill=CYAN + (150,), anchor="mm")

# 3. Hero foreground glyph
draw.text((x, y), char, font=font, fill=WHITE, anchor="mm")
```

---

## 3. Luminance Track Mattes (Mask Reveals)

In After Effects, "Track Mattes" use the luminance or alpha of one layer to mask another. In Python with Pillow, this is achieved using `ImageChops.multiply`:

```python
# 1. Text luminance layer (white text on black canvas)
text_layer = Image.new("L", (W, H), 0)
text_draw = ImageDraw.Draw(text_layer)
text_draw.text((cx, cy), "SHAPE & RHYTHM", font=font, fill=255, anchor="mm")

# 2. Expanding wipe mask (white box expanding from center)
mask_layer = Image.new("L", (W, H), 0)
mask_draw = ImageDraw.Draw(mask_layer)
mask_draw.rectangle([cx - width / 2, cy - height, cx + width / 2, cy + height], fill=255)

# 3. Multiply mask with text to get final stencil
stencil = ImageChops.multiply(text_layer, mask_layer)

# 4. Fill colored layer through stencil
color_fill = Image.new("RGBA", (W, H), YELLOW + (255,))
foreground_layer.paste(color_fill, (0, 0), stencil)
```

---

## 4. Swiss HUD / Meta Data Typography

Pairing massive headline typography ($200\text{px}+$) with small, high-density HUD details ($30-45\text{px}$) creates visual hierarchy and professional polish:

- Scene counters: `"01 / 03"`
- Live frame counters: `f"FRAME {int(t * FPS):04d}"`
- Dynamic timeline progress line:
  ```python
  draw.line([(80, H - 120), (80 + (W - 160) * progress, H - 120)], fill=color, width=6)
  ```
