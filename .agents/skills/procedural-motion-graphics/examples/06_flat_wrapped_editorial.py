"""Example 06: Flat 'Wrapped' Editorial Motion Graphics.

Demonstrates:
1. Super-Sampled Anti-Aliasing (SSAA) drawing via Pen (1.5x downsampled via Lanczos).
2. Damped harmonic spring physics (spring) for tactile entrances.
3. 2D Polar radius shape morphing (Circle -> Square -> Triangle -> Star).
4. Squash & stretch with reactive contact shadows.
5. Sliding mask typography reveal.
6. Seamless iris wipe scene transition.
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
    Pen, spring, smoothstep, prog, lerp, lerpc, hexc,
    squash_and_stretch, contact_shadow_scale,
    morph_polar_shapes, polar_to_cartesian, iris_wipe
)

W, H, FPS = 1280, 720, 30
DUR = 4.0  # 4 seconds
TOTAL_FRAMES = int(W and (FPS * DUR))

GREEN  = hexc("#1ED760")
BLACK  = hexc("#121212")
WHITE  = (255, 255, 255)
PURPLE = hexc("#8B3DFF")
ORANGE = hexc("#FF6437")
YELLOW = hexc("#F5E050")

def render_scene_intro(t: float) -> Image.Image:
    """Scene 1: Saturated Green, sunburst, spring typography with hard offset shadow."""
    pen = Pen(GREEN, W, H, k=1.5)
    dark_tint = lerpc(GREEN, BLACK, 0.12)
    
    # 1. Rotating sunburst rays
    for i in range(12):
        a0 = t * 0.5 + i * math.pi / 6.0
        a1 = a0 + math.pi / 12.0
        r = 1400
        pen.poly([(640, 360),
                  (640 + r * math.cos(a0), 360 + r * math.sin(a0)),
                  (640 + r * math.cos(a1), 360 + r * math.sin(a1))], dark_tint)
    
    # 2. Hero typography slamming in with damped spring physics
    # Left entry: "FLAT & BOLD"
    p1 = spring(prog(t, 0.1, 0.9), k=7, w=14)
    off1 = (1.0 - p1) * -1200
    pen.txt(640 + off1 + 8, 270 + 8, "FLAT & BOLD", 160, BLACK)
    pen.txt(640 + off1, 270, "FLAT & BOLD", 160, WHITE)
    
    # Right entry: "SPRING MOTION"
    p2 = spring(prog(t, 0.35, 1.15), k=7, w=14)
    off2 = (1.0 - p2) * 1200
    pen.txt(640 + off2 + 8, 440 + 8, "SPRING MOTION", 130, BLACK)
    pen.txt(640 + off2, 440, "SPRING MOTION", 130, YELLOW)
    
    # 3. Expanding pill badge
    q = spring(prog(t, 0.8, 1.5))
    pen.rect(640 - 180 * q, 80, 640 + 180 * q, 140, BLACK, r=30)
    if q > 0.85:
        pen.txt(640, 110, "SUPER-SAMPLED VECTOR GRAPHICS", 18, GREEN)
        
    return pen.render()

def render_scene_morph(t: float) -> Image.Image:
    """Scene 2: Orange background, polar shape morph with squash & stretch and contact shadows."""
    pen = Pen(ORANGE, W, H, k=1.5)
    floor_y = 540
    pen.rect(0, floor_y, W, H, lerpc(ORANGE, BLACK, 0.18))
    
    # Bouncing and morphing shapes
    shapes_colors = [BLACK, WHITE, YELLOW, GREEN]
    for i in range(4):
        cx = 280 + i * 240
        tt = t * 2.2 - i * 0.25
        phase = tt % 1.0
        cycle = int(math.floor(tt))
        cur_shape = (cycle + i) % 4
        next_shape = (cycle + i + 1) % 4
        
        morph_prog = smoothstep(prog(phase, 0.5, 0.95))
        bounce_height = abs(math.sin(math.pi * phase))
        
        # Physics: Squash & stretch + contact shadow
        sx, sy = squash_and_stretch(bounce_height, intensity=0.4, power=6.0, is_landing=(phase < 0.5))
        y = (floor_y - 35) - 220 * bounce_height
        
        # Draw shadow
        shadow_scale = contact_shadow_scale(bounce_height, min_scale=0.5)
        pen.ell(cx, floor_y + 40, 65 * shadow_scale, fill=lerpc(ORANGE, BLACK, 0.35))
        
        # Morph vertices in polar space & project to Cartesian
        raw_pts = morph_polar_shapes(cur_shape, next_shape, morph_prog, num_samples=72)
        poly_pts = polar_to_cartesian(cx, y, raw_pts, scale=75, scale_x=sx, scale_y=sy)
        pen.poly(poly_pts, shapes_colors[i])
        
    # Headline with sliding mask reveal
    headline = "POLAR MORPHING."
    k_wipe = smoothstep(prog(t, 0.2, 0.9))
    pen.txt(70, 130, headline, 86, WHITE, anchor="lm")
    w = pen.tw(headline, 86)
    # Mask block sliding to right
    pen.rect(70 + w * k_wipe - 2, 80, 70 + w + 20, 180, ORANGE)
    
    return pen.render()

def main():
    output_path = "flat_wrapped_editorial.mp4"
    print(f"Rendering {output_path} (1280x720 @ {FPS}fps, SSAA 1.5x)...")
    writer = imageio.get_writer(output_path, fps=FPS, codec="libx264", quality=8, pixelformat="yuv420p")
    
    split_time = 2.0
    iris_duration = 0.5
    
    for frame_idx in range(TOTAL_FRAMES):
        t = frame_idx / FPS
        if t < split_time:
            frame_img = render_scene_intro(t)
        else:
            local_t = t - split_time
            curr_img = render_scene_morph(local_t)
            if local_t < iris_duration:
                prev_img = render_scene_intro(t)
                k_iris = local_t / iris_duration
                frame_img = iris_wipe(curr_img, prev_img, k_iris)
            else:
                frame_img = curr_img
                
        writer.append_data(np.asarray(frame_img))
        if frame_idx % 30 == 0:
            print(f"  Frame {frame_idx}/{TOTAL_FRAMES} (t={t:.2f}s)")
            
    writer.close()
    print(f"Finished rendering {output_path} successfully!")

if __name__ == "__main__":
    main()
