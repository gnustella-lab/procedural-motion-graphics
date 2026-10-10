"""Example 07: App UI & Native Product Simulation (Spotify App Direction).

Demonstrates:
1. 'The Resume is the App' product motion concept.
2. Time-stamped karaoke synced lyrics engine with autoscroll and color crossfade.
3. Native mobile/desktop vertical push (swipe) screen transitions.
4. Generative geometric album covers (zero external image assets).
5. Dynamic in-line audio equalizer bars replacing track numbers on active rows.
6. Interactive UI micro-interactions: OS cursor, button click depression (8%),
   expanding shockwave ripple, and outline-to-solid button state morphing.
"""

import math
import os
import sys
import numpy as np
from PIL import Image
import imageio.v2 as imageio

# Add root folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.motion_engine import (
    Pen, prog, lerp, lerpc, hexc,
    ease_out_cubic, ease_in_out_cubic, ease_out_back,
    vertical_push_transition, generative_cover, mini_eq_bars,
    draw_cursor, button_click_press, draw_click_ripple
)

W, H, FPS = 1280, 720, 30
DUR = 6.0  # 6 seconds showcase
TOTAL_FRAMES = int(FPS * DUR)

GREEN = hexc("#1ED760")
BG    = hexc("#121212")
CARD  = hexc("#1F1F1F")
GREY  = hexc("#A7A7A7")
WHITE = (255, 255, 255)
LYR   = [hexc("#E8115B"), hexc("#148A08"), hexc("#7358FF")]

LINES = ["Turning ideas", "into motion.", "Your next hire."]

def render_scene_lyrics(t: float) -> Image.Image:
    """Scene 1: Karaoke-style synced lyrics view."""
    words = [w for line in LINES for w in line.split()]
    wt = [0.2 + i * 0.35 for i in range(len(words))]
    line_of = [li for li, line in enumerate(LINES) for _ in line.split()]
    cur_line = max([line_of[i] for i, a in enumerate(wt) if t >= a] or [0])
    
    # Background color crossfade per line
    bgc = LYR[0]
    for li in range(1, len(LINES)):
        start_t = wt[line_of.index(li)] - 0.2
        bgc = lerpc(bgc, LYR[li % len(LYR)], ease_in_out_cubic(prog(t, start_t, start_t + 0.4)))
        
    pen = Pen(bgc, W, H, k=1.5)
    
    # Autoscroll calculation
    scroll = 0.0
    for li in range(1, len(LINES)):
        start_t = wt[line_of.index(li)] - 0.2
        scroll += ease_in_out_cubic(prog(t, start_t, start_t + 0.4)) * 90.0
        
    pen.txt(60, 55, "LYRICS", 20, lerpc(bgc, WHITE, 0.7))
    
    w_idx = 0
    for li, line in enumerate(LINES):
        y = 280 + li * 90 - scroll
        x = 60
        for w in line.split():
            k = ease_out_cubic(prog(t, wt[w_idx], wt[w_idx] + 0.15))
            dim_col = lerpc(bgc, (0, 0, 0), 0.45)
            col = lerpc(dim_col, WHITE, k) if li <= cur_line else dim_col
            pen.txt(x, y, w, 74, col)
            x += pen.tw(w + " ", 74)
            w_idx += 1
            
    # Audio progress bar
    pen.rect(60, 660, 1220, 664, lerpc(bgc, (0, 0, 0), 0.3), r=2)
    pen.rect(60, 660, lerp(60, 1220, t / 3.0), 664, WHITE, r=2)
    pen.ell(lerp(60, 1220, t / 3.0), 662, 7, WHITE)
    
    return pen.render()

TRACKS = [("Kinetic Typography", "Nova Agency", "3:12"),
          ("Brand Motion Systems", "Faixa Studio", "4:05"),
          ("3D & UI Interactions", "Independent", "2:48")]

def render_scene_playlist(t: float) -> Image.Image:
    """Scene 2: Playlist view with active equalizer track highlight."""
    pen = Pen(BG, W, H, k=1.5)
    
    # Header vertical bands gradient
    top_color = hexc("#5038A0")
    for i in range(35):
        pen.rect(0, i * 8, W, i * 8 + 8, lerpc(top_color, BG, i / 35.0))
        
    # Playlist Cover with pop-in overshoot
    k_cover = ease_out_back(prog(t, 0.0, 0.6), s=1.8)
    cs = 180 * k_cover
    if cs > 4:
        generative_cover(pen, 60 + (180 - cs) / 2, 50 + (180 - cs) / 2, cs, 7, GREEN)
        
    # Title slide-in
    tx = lerp(-300, 270, ease_out_cubic(prog(t, 0.1, 0.7)))
    pen.txt(tx, 80, "PLAYLIST", 18, WHITE)
    pen.txt(tx, 140, "Motion Resume", 76, WHITE)
    pen.txt(tx, 205, "Verified Creator  •  3 tracks  •  Pixel Perfect", 20, GREY, bold=False)
    
    # Tracklist rows
    active_row = min(2, int(max(0.0, t - 1.0) / 0.8))
    for i, (name, artist, dur) in enumerate(TRACKS):
        a = 0.4 + i * 0.12
        e = ease_out_cubic(prog(t, a, a + 0.45))
        y = 290 + i * 74 + (1.0 - e) * 50
        if e <= 0:
            continue
            
        is_active = (i == active_row and t > 1.0)
        if is_active:
            pen.rect(40, y - 28, 1240, y + 28, CARD, r=6)
            mini_eq_bars(pen, 64, y + 8, t, GREEN)
        else:
            pen.txt(72, y, str(i + 1), 20, GREY, "mm", bold=False)
            
        generative_cover(pen, 105, y - 22, 44, i * 5 + 1, LYR[i % 3])
        pen.txt(168, y - 10, name, 22, GREEN if is_active else WHITE)
        pen.txt(168, y + 14, artist, 16, GREY, bold=False)
        pen.txt(1210, y, dur, 18, GREY, "rm", bold=False)
        
    return pen.render()

def render_scene_profile(t: float) -> Image.Image:
    """Scene 3: Profile view with cursor click interaction and button state morph."""
    pen = Pen(BG, W, H, k=1.5)
    
    # Avatar disc with green status ring
    k_pop = ease_out_back(prog(t, 0.0, 0.6), s=1.8)
    pen.ell(640, 190, 110 * k_pop + 6, GREEN)
    pen.ell(640, 190, 110 * k_pop, hexc("#2A2A2A"))
    if k_pop > 0.2:
        pen.ell(640, 165, 38 * k_pop, GREY)
        pen.d.pieslice([(640 - 70 * k_pop) * pen.k, (230 - 35 * k_pop) * pen.k,
                        (640 + 70 * k_pop) * pen.k, (230 + 105 * k_pop) * pen.k],
                       180, 360, fill=GREY)
        
    e = ease_out_cubic(prog(t, 0.2, 0.8))
    pen.txt(640, 350 + (1.0 - e) * 30, "VERIFIED ARTIST", 16, lerpc(BG, GREEN, e), "mm")
    pen.txt(640, 405 + (1.0 - e) * 35, "Motion Designer", 64, lerpc(BG, WHITE, e), "mm")
    
    # Interactive Button: Click at t=1.2s
    t_click = 1.2
    scale = button_click_press(t, t_click, press_dur=0.15, release_dur=0.20, max_scale_reduction=0.08)
    is_clicked = (t > t_click + 0.15)
    
    # Morph button width from 200px to 320px
    morph_prog = ease_out_cubic(prog(t, t_click + 0.15, t_click + 0.55))
    bw = lerp(200, 320, morph_prog) * scale
    bh = 56 * scale
    by = 510
    
    if is_clicked:
        pen.rect(640 - bw / 2, by - bh / 2, 640 + bw / 2, by + bh / 2, GREEN, r=bh / 2)
        pen.txt(640, by, "LET'S WORK ✓", 22, BG, "mm")
    else:
        pen.rect(640 - bw / 2, by - bh / 2, 640 + bw / 2, by + bh / 2, WHITE, r=bh / 2)
        pen.rect(640 - bw / 2 + 2, by - bh / 2 + 2, 640 + bw / 2 - 2, by + bh / 2 - 2, BG, r=bh / 2)
        pen.txt(640, by, "FOLLOW", 22, WHITE, "mm")
        
    # Expanding shockwave ripple
    draw_click_ripple(pen, 640, by, t, t_click, duration=0.6, max_radius=110.0, outline_color=GREEN, bg_color=BG)
    
    # Mouse Cursor path
    cx = lerp(850, 660, ease_in_out_cubic(prog(t, 0.7, 1.2)))
    cy = lerp(660, by + 10, ease_in_out_cubic(prog(t, 0.7, 1.2)))
    if t < 2.0:
        draw_cursor(pen, cx, cy)
        
    pen.txt(640, 610, "portfolio.com  •  hello@motion.design", 18,
            lerpc(BG, GREY, ease_out_cubic(prog(t, 1.5, 2.0))), "mm", bold=False)
            
    return pen.render()

def main():
    output_path = "app_ui_simulation.mp4"
    print(f"Rendering {output_path} (1280x720 @ {FPS}fps)...")
    writer = imageio.get_writer(output_path, fps=FPS, codec="libx264", quality=8, pixelformat="yuv420p")
    
    scenes = [
        (0.0, 2.0, render_scene_lyrics),
        (2.0, 4.0, render_scene_playlist),
        (4.0, 6.0, render_scene_profile)
    ]
    transition_dur = 0.45
    
    for frame_idx in range(TOTAL_FRAMES):
        t = frame_idx / FPS
        # Determine active scene
        idx = max(n for n, s in enumerate(scenes) if t >= s[0])
        s_start, s_end, s_fn = scenes[idx]
        local_t = t - s_start
        curr_img = s_fn(local_t)
        
        # Apply vertical push transition
        if idx > 0 and local_t < transition_dur:
            prev_s_start, _, prev_fn = scenes[idx - 1]
            prev_img = prev_fn(t - prev_s_start)
            frame_img = vertical_push_transition(curr_img, prev_img, local_t / transition_dur)
        else:
            frame_img = curr_img
            
        writer.append_data(np.asarray(frame_img))
        if frame_idx % 30 == 0:
            print(f"  Frame {frame_idx}/{TOTAL_FRAMES} (t={t:.2f}s)")
            
    writer.close()
    print(f"Finished rendering {output_path} successfully!")

if __name__ == "__main__":
    main()
