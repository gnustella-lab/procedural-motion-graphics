# App UI & Native Product Simulation Motion Graphics

"The Product IS the Video" represents the premier philosophy in procedural motion design. Rather than showing abstract geometric shapes or generic video templates, the animation faithfully simulates the interactive user interface of a modern digital application. Every native UI component is repurposed to tell a dynamic commercial or product story.

```mermaid
flowchart LR
    subgraph Vertical Mobile App Paradigm (V4 Desired)
        A[Status Bar & Timeline Feed] -->|Vertical Push| B[Interactive Media & Touch Gestures]
        B -->|Sheet Up Modal| C[QWERTY Keyboard & Typed Post]
        C -->|Post Action| D[Notification Toasts & Badge Ramp]
    end
    subgraph Horizontal Media Player Paradigm (V3)
        E[Karaoke Synced Lyrics] -->|Vertical Push| F[Playlist & Active EQ Bars]
        F -->|Vertical Push| G[Album Carousel]
        G -->|Vertical Push| H[Profile & Follow Click]
    end
```

---

## 1. The Two Simulation Paradigms

Depending on the distribution channel and aspect ratio:

### Paradigm 1: Full-HD Vertical Mobile Social Feed (V4 - Desired & Recommended)
- **Target Surfaces**: TikTok, Instagram Reels, YouTube Shorts, X Timeline.
- **Resolution**: $1080 \times 1920$ @ 30 FPS.
- **Key Mechanics**:
  - Top system status bar (`9:41`, cellular signal bars, battery outline).
  - Segmented timeline tabs with animated active indicator underline.
  - Custom procedural rich media cards (e.g. animated rocket launches, sports scoreboards with live confetti).
  - Finger touch indicators with pressure dip and radial shockwave ripples.
  - Slide-up bottom sheet modal (`sheet_up`) over dimmed background.
  - Full virtual QWERTY keyboard with active key magnification pop-ups.
  - Staggered incoming notification toasts sliding in from screen edge.
  - Notification badge counter dynamically climbing to "99+".

### Paradigm 2: Horizontal Streaming Media Player (V3)
- **Target Surfaces**: YouTube 16:9, Desktop Web, Portfolio Embeds.
- **Resolution**: $1280 \times 720$ or $1920 \times 1080$.
- **Key Mechanics**:
  - Synced karaoke lyrics with line-by-line autoscroll and background color crossfading.
  - Playlist tracklists with 3-bar animated green equalizer bars (`mini_eq_bars`) replacing track numbers on active rows.
  - Generative geometric album covers created without external assets.
  - Desktop mouse pointer arrow with 8% button click depression and outline-to-solid state morphing.

---

## 2. Touch Tap & Gesture Physics (Vertical Mobile)

Mobile interfaces feel authentic only when touch interactions exhibit physical mass and elasticity:

```python
def tap(c, x: float, y: float, t: float, t_tap: float,
        col=(255, 255, 255), ripple=(29, 155, 240)):
    # 1. Soft translucent finger contact pad
    a = min(prog(t, t_tap - 0.32, t_tap - 0.06), 1.0 - prog(t, t_tap + 0.12, t_tap + 0.42))
    if a > 0:
        press = clamp(prog(t, t_tap - 0.06, t_tap + 0.02) - prog(t, t_tap + 0.08, t_tap + 0.24))
        r = 46 * (1.0 - 0.22 * press)  # Tactile compression
        c.alpha_ell(x, y, r, col, 0.32 * a)
        c.alpha_ell(x, y, r, col, 0.55 * a, width=3)
    # 2. Expanding shockwave ripple
    if t_tap < t < t_tap + 0.6:
        p = prog(t, t_tap, t_tap + 0.6)
        c.alpha_ell(x, y, 40 + ease_out_cubic(p) * 120, ripple, 0.9 * (1.0 - p), width=5)
```

---

## 3. Modal Sheet Transitions (`sheet_up` and `sheet_down`)

To present composer windows, comment sections, or filter sheets:
1. Capture the previous frame (`prev`) and dim its luminance by 40-60%.
2. Render the modal card (`cur`) entering from below the screen:
   $$y_{\text{offset}} = (1 - \text{ease\_out\_cubic}(p)) \cdot (H - 100)$$
3. Keep the native status bar fixed at $(0, 0)$ across the transition.

```python
def transition_sheet_up(cur: Image.Image, prev: Image.Image, p: float) -> Image.Image:
    w, h = cur.size
    base = Image.blend(prev, Image.new("RGB", (w, h), (0, 0, 0)), clamp(0.6 * p))
    y_off = int((1.0 - ease_out_cubic(p)) * (h - 100))
    sheet = cur.crop((0, 100, w, h))
    base.paste(sheet, (0, 100 + y_off))
    return base
```

---

## 4. Keystroke Animation & Key Magnification

To simulate live typing:
1. Define a standard key bounding-box dictionary for rows `QWERTYUIOP`, `ASDFGHJKL`, `ZXCVBNM`, and spacebar.
2. Determine active character:
   ```python
   active_char = typed_string[int((lt - start_t) / dt)].upper()
   ```
3. Draw a raised bubble that overshoots vertically with `ease_out_back`:
   ```python
   s = ease_out_back(clamp(key_t / 0.05), 2.0)
   c.rect(x0 - 14 * s, y0 - 128 * s, x1 + 14 * s, y1, fill=(140, 140, 146), r=18)
   c.txt((x0 + x1)/2, y0 - 62 * s, active_char, 70 * s, (255, 255, 255), "mm")
   ```

---

## 5. Notification Toast Alerts

When a post receives engagement, trigger stacked sliding toasts:
- Compute entry via `ease_out_back(prog(lt, t_in, t_in + 0.40), 1.6)`.
- Offset horizontally: $x = (1 - e) \cdot 260\text{px}$.
- Include circular user avatar, action icon (heart, repost, follow), and bold participant name.
- Synchronize with a procedural harmonic chime ($659\text{Hz} - 880\text{Hz}$).
