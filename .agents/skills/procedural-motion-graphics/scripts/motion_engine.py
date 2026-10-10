"""Motion Graphics Engine in Pure Python (NumPy + Pillow).

A modular procedural motion design toolkit providing mathematical easing curves,
3D perspective projection, geometric morphing, track mattes, and post-processing
compositing passes (bloom, chromatic aberration, film grain, vignette, camera shake).
"""

import math
import random
from typing import List, Tuple, Union
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

# ==============================================================================
# 1. MATHEMATICAL EASING & INTERPOLATION
# ==============================================================================

def clamp(x: float, a: float = 0.0, b: float = 1.0) -> float:
    """Clamp value x between lower bound a and upper bound b."""
    return max(a, min(b, x))

def prog(t: float, a: float, b: float) -> float:
    """Calculate normalized progress of t across interval [a, b] in range [0, 1]."""
    if b == a:
        return 1.0 if t >= a else 0.0
    return clamp((t - a) / (b - a))

def ease_out_cubic(x: float) -> float:
    """Smooth deceleration cubic easing."""
    return 1.0 - (1.0 - x) ** 3

def ease_in_out_cubic(x: float) -> float:
    """Smooth acceleration then deceleration."""
    return 4.0 * x**3 if x < 0.5 else 1.0 - (-2.0 * x + 2.0)**3 / 2.0

def ease_in_expo(x: float) -> float:
    """Exponential explosive acceleration."""
    return 0.0 if x <= 0.0 else 2.0 ** (10.0 * x - 10.0)

def ease_out_expo(x: float) -> float:
    """Exponential fast-entry settling deceleration."""
    return 1.0 if x >= 1.0 else 1.0 - 2.0 ** (-10.0 * x)

def ease_out_back(x: float, s: float = 1.70158) -> float:
    """Deceleration overshoot curve (springs past target, settles back)."""
    c3 = s + 1.0
    return 1.0 + c3 * (x - 1.0)**3 + s * (x - 1.0)**2

def ease_out_elastic(x: float) -> float:
    """Damped harmonic oscillation (elastic bounce)."""
    if x in (0.0, 1.0):
        return x
    return 2.0 ** (-10.0 * x) * math.sin((x * 10.0 - 0.75) * (2.0 * math.pi / 3.0)) + 1.0

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between scalar values a and b."""
    return a + (b - a) * t

def lerpc(c1: Tuple[int, ...], c2: Tuple[int, ...], t: float) -> Tuple[int, ...]:
    """Linear interpolation between RGB or RGBA color tuples."""
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


# ==============================================================================
# 2. TYPOGRAPHY & FONT HELPERS
# ==============================================================================

def get_font(size: int, bold: bool = True) -> ImageFont.ImageFont:
    """Load standard system geometric font with automatic cross-platform fallbacks."""
    font_candidates = (
        ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",
         "/System/Library/Fonts/Helvetica.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        if bold else
        ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
         "/System/Library/Fonts/Helvetica.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    )
    for path in font_candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()

def text_center(draw: ImageDraw.ImageDraw, xy: Tuple[float, float], text: str,
                font: ImageFont.ImageFont, fill: Tuple[int, ...], anchor: str = "mm") -> None:
    """Render centered or anchored text cleanly on ImageDraw."""
    draw.text(xy, text, font=font, fill=fill, anchor=anchor)


# ==============================================================================
# 3. PROCEDURAL 2D GEOMETRY
# ==============================================================================

def rot_poly(cx: float, cy: float, r: float, n: int, ang: float) -> List[Tuple[float, float]]:
    """Generate vertices for a regular n-sided polygon rotated by ang radians."""
    return [
        (cx + r * math.cos(ang + i * 2.0 * math.pi / n),
         cy + r * math.sin(ang + i * 2.0 * math.pi / n))
        for i in range(n)
    ]


# ==============================================================================
# 4. 3D PERSPECTIVE PROJECTION & ROTATION
# ==============================================================================

def rotate_3d(x: float, y: float, z: float, rx: float = 0.0, ry: float = 0.0, rz: float = 0.0) -> Tuple[float, float, float]:
    """Rotate 3D coordinates around X, Y, and Z axes using Euler rotation matrices."""
    # X rotation
    if rx != 0.0:
        cos_x, sin_x = math.cos(rx), math.sin(rx)
        y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x
    # Y rotation
    if ry != 0.0:
        cos_y, sin_y = math.cos(ry), math.sin(ry)
        x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y
    # Z rotation
    if rz != 0.0:
        cos_z, sin_z = math.cos(rz), math.sin(rz)
        x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z
    return x, y, z

def project_3d(x: float, y: float, z: float, cx: float, cy: float,
               fov: float = 900.0, z_offset: float = 600.0) -> Tuple[float, float, float]:
    """Perspective divide projection of 3D point (x, y, z) into 2D canvas (px, py, scale)."""
    denom = fov + z + z_offset
    if denom <= 0:
        denom = 1.0
    scale = fov / denom
    return cx + x * scale, cy + y * scale, scale


# ==============================================================================
# 5. POST-PROCESSING COMPOSITING PASSES
# ==============================================================================

def apply_glow_bloom(img: np.ndarray, threshold: float = 90.0,
                     blur_radius: int = 8, intensity: float = 0.55) -> np.ndarray:
    """Downsampled Gaussian bloom: isolates bright highlights and blends additively."""
    H, W = img.shape[:2]
    small = Image.fromarray(img.clip(0, 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR)
    glow = np.asarray(small.filter(ImageFilter.GaussianBlur(blur_radius)).resize((W, H), Image.BILINEAR), np.float32)
    return img + np.maximum(glow - threshold, 0.0) * intensity

def apply_chromatic_aberration(img: np.ndarray, offset_px: int) -> np.ndarray:
    """Displace red and blue channels horizontally to simulate chromatic aberration."""
    if offset_px == 0:
        return img
    out = img.copy()
    out[..., 0] = np.roll(img[..., 0], offset_px, axis=1)
    out[..., 2] = np.roll(img[..., 2], -offset_px, axis=1)
    return out

def apply_camera(layer: Image.Image, zoom: float = 1.0, shake_px: float = 0.0,
                 width: int = 1920, height: int = 1080) -> Image.Image:
    """Apply virtual camera zoom about center and positional 2D shake."""
    out = layer
    if zoom != 1.0:
        nw, nh = int(width * zoom), int(height * zoom)
        out = out.resize((nw, nh), Image.BICUBIC).crop(
            ((nw - width) // 2, (nh - height) // 2, (nw - width) // 2 + width, (nh - height) // 2 + height)
        )
    if shake_px > 0:
        sx = int(random.uniform(-shake_px, shake_px))
        sy = int(random.uniform(-shake_px, shake_px))
        out = ImageChops.offset(out, sx, sy)
    return out

def precompute_vignette(width: int, height: int, falloff: float = 0.65) -> np.ndarray:
    """Generate radial vignette darkening mask."""
    yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
    cx, cy = width / 2.0, height / 2.0
    rr = np.sqrt((xx - cx)**2 + (yy - cy)**2) / math.hypot(cx, cy)
    return (1.0 - falloff * rr**2).clip(0.0, 1.0)[..., None]

def precompute_grain(width: int, height: int, num_plates: int = 6, sigma: float = 7.0) -> List[np.ndarray]:
    """Precompute cyclic Gaussian film grain plates for temporal texture and dithering."""
    return [np.random.normal(0, sigma, (height, width, 1)).astype(np.float32) for _ in range(num_plates)]

def lissajous_gradient_background(xx: np.ndarray, yy: np.ndarray, t: float,
                                  tint: Tuple[int, int, int], bg_base: Tuple[int, int, int] = (10, 10, 18),
                                  width: int = 1920, height: int = 1080) -> np.ndarray:
    """Generate dynamic dual radial gradient background moving along a Lissajous curve."""
    cx, cy = width / 2.0, height / 2.0
    ax = cx + math.cos(t * 0.7) * 500.0
    ay = cy + math.sin(t * 0.9) * 250.0
    dist = np.sqrt((xx - ax)**2 + (yy - ay)**2) / 1400.0
    g = np.exp(-dist * 3.0)[..., None]
    return np.array(bg_base, np.float32) + g * np.array(tint, np.float32) * 0.22
