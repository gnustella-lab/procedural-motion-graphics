"""Motion Graphics Engine in Pure Python (NumPy + Pillow).

A modular procedural motion design toolkit providing mathematical easing curves,
spring physics, Super-Sampled Anti-Aliasing (SSAA), 2D polar geometric morphing,
3D perspective projection, track mattes, transitions (iris wipes, vertical app pushes),
app UI simulation tools (generative covers, synced lyrics, micro-interactions), and
post-processing compositing passes (bloom, chromatic aberration, film grain, vignette).
"""

import math
import random
from typing import List, Tuple, Union
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

# ==============================================================================
# 1. MATHEMATICAL EASING, SPRINGS & INTERPOLATION
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
    """Smooth deceleration cubic easing (Penner)."""
    x = clamp(x, 0.0, 1.0)
    return 1.0 - (1.0 - x) ** 3

def ease_in_out_cubic(x: float) -> float:
    """Smooth acceleration then deceleration (Penner S-curve)."""
    x = clamp(x, 0.0, 1.0)
    return 4.0 * x**3 if x < 0.5 else 1.0 - (-2.0 * x + 2.0)**3 / 2.0

def ease_in_expo(x: float) -> float:
    """Exponential explosive acceleration."""
    return 0.0 if x <= 0.0 else 2.0 ** (10.0 * x - 10.0)

def ease_out_expo(x: float) -> float:
    """Exponential fast-entry settling deceleration."""
    return 1.0 if x >= 1.0 else 1.0 - 2.0 ** (-10.0 * x)

def ease_out_back(x: float, s: float = 1.70158) -> float:
    """Deceleration overshoot curve (springs past target, settles back)."""
    x = clamp(x, 0.0, 1.0)
    c3 = s + 1.0
    return 1.0 + c3 * (x - 1.0)**3 + s * (x - 1.0)**2

def ease_out_elastic(x: float) -> float:
    """Damped harmonic oscillation (elastic bounce)."""
    if x in (0.0, 1.0):
        return x
    return 2.0 ** (-10.0 * x) * math.sin((x * 10.0 - 0.75) * (2.0 * math.pi / 3.0)) + 1.0

def spring(x: float, k: float = 7.0, w: float = 14.0) -> float:
    """Damped harmonic spring oscillation: 1 - e^(-kx) * cos(wx).
    
    Provides natural, physically grounded overshoot and settling vibrations.
    Parameters:
        x: Normalized progress (x >= 0).
        k: Damping coefficient (higher = quicker settling, e.g. 7).
        w: Angular frequency (higher = more oscillations, e.g. 14).
    """
    if x <= 0.0:
        return 0.0
    return 1.0 - math.exp(-k * x) * math.cos(w * x)

def smoothstep(x: float) -> float:
    """Hermite smoothstep interpolation (3x^2 - 2x^3) clamped in [0, 1]."""
    x = clamp(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)

def smooth(x: float) -> float:
    """Alias for smoothstep."""
    return smoothstep(x)

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between scalar values a and b."""
    return a + (b - a) * t

def lerpc(c1: Tuple[int, ...], c2: Tuple[int, ...], t: float) -> Tuple[int, ...]:
    """Linear interpolation between RGB or RGBA color tuples."""
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))

def squash_and_stretch(bounce: float, intensity: float = 0.35, power: float = 6.0, is_landing: bool = True) -> Tuple[float, float]:
    """Calculate (sx, sy) scale factors for classic squash and stretch on ground contact.
    
    Args:
        bounce: Normalized bounce height (0.0 at floor impact, 1.0 at peak arc).
        intensity: Maximum squash amount (e.g. 0.35 for 35% wider).
        power: Exponent controlling sharpness of ground impact zone.
        is_landing: True if phase corresponds to descending/landing half of cycle.
    """
    sx = 1.0 + intensity * ((1.0 - bounce) ** power) * (1.0 if is_landing else 0.0)
    sy = 2.0 - sx
    return sx, sy

def contact_shadow_scale(bounce: float, min_scale: float = 0.55) -> float:
    """Calculate contact shadow scale factor based on distance from ground."""
    return 1.0 - (1.0 - min_scale) * bounce


# ==============================================================================
# 2. TYPOGRAPHY & COLOR HELPERS
# ==============================================================================

def hexc(hex_str: str) -> Tuple[int, int, int]:
    """Parse hex color '#RRGGBB' to an (R, G, B) tuple."""
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def get_font(size: int, bold: bool = True) -> ImageFont.ImageFont:
    """Load standard system geometric font with automatic cross-platform fallbacks."""
    font_candidates = (
        ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf",
         "/System/Library/Fonts/Helvetica.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        if bold else
        ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf",
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
# 3. PROCEDURAL 2D GEOMETRY & POLAR SHAPE MORPHING
# ==============================================================================

def rot_poly(cx: float, cy: float, r: float, n: int, ang: float) -> List[Tuple[float, float]]:
    """Generate vertices for a regular n-sided polygon rotated by ang radians."""
    return [
        (cx + r * math.cos(ang + i * 2.0 * math.pi / n),
         cy + r * math.sin(ang + i * 2.0 * math.pi / n))
        for i in range(n)
    ]

def polar_radius(shape_type: int, theta: float) -> float:
    """Calculate normalized polar radius r(theta) for 2D geometric shapes:
    0 = Circle
    1 = Rounded Square / Box
    2 = Equilateral Triangle
    3 = 5-Point Star
    """
    if shape_type == 0:  # Circle
        return 1.0
    elif shape_type == 1:  # Square
        cos_t = max(1e-5, abs(math.cos(theta)))
        sin_t = max(1e-5, abs(math.sin(theta)))
        return 0.86 / max(cos_t, sin_t)
    elif shape_type == 2:  # Triangle
        m = (theta + math.pi / 2.0) % (2.0 * math.pi / 3.0)
        return 0.5 * 1.15 / max(0.1, math.cos(m - math.pi / 3.0))
    elif shape_type == 3:  # 5-Point Star
        return 0.62 + 0.38 * (math.cos(5.0 * theta) ** 2) + 0.05
    return 1.0

def morph_polar_shapes(shape_a: int, shape_b: int, progress: float, num_samples: int = 72) -> List[Tuple[float, float]]:
    """Generate interpolated (theta, radius) points between shape_a and shape_b across num_samples."""
    progress = clamp(progress, 0.0, 1.0)
    points = []
    for i in range(num_samples):
        th = i / num_samples * 2.0 * math.pi
        r_a = min(polar_radius(shape_a, th), 1.5)
        r_b = min(polar_radius(shape_b, th), 1.5)
        r = lerp(r_a, r_b, progress)
        points.append((th, r))
    return points

def polar_to_cartesian(cx: float, cy: float, points: List[Tuple[float, float]],
                       scale: float = 1.0, scale_x: float = 1.0, scale_y: float = 1.0) -> List[Tuple[float, float]]:
    """Convert a list of (theta, radius) points into Cartesian (x, y) coordinates with scaling."""
    return [
        (cx + math.cos(th) * r * scale * scale_x,
         cy + math.sin(th) * r * scale * scale_y)
        for th, r in points
    ]


# ==============================================================================
# 4. SUPER-SAMPLED ANTI-ALIASING (SSAA) DRAWING CANVAS (PEN)
# ==============================================================================

class Pen:
    """Super-Sampled Anti-Aliasing (SSAA) drawing canvas.
    
    Draws onto a virtual canvas multiplied by scale factor K (default 1.5x) and
    downsamples with Lanczos filtering upon export. This achieves razor-sharp vector
    rendering without jagged edges or GPU dependencies.
    """
    def __init__(self, bg: Union[Tuple[int, int, int], str], width: int = 1280, height: int = 720, k: float = 1.5):
        self.width = width
        self.height = height
        self.k = k
        if isinstance(bg, str):
            bg = hexc(bg)
        self.im = Image.new("RGB", (int(width * k), int(height * k)), bg)
        self.d = ImageDraw.Draw(self.im)
        self._font_cache = {}

    def font(self, size: float, bold: bool = True) -> ImageFont.ImageFont:
        scaled_size = max(1, int(size * self.k))
        key = (scaled_size, bold)
        if key not in self._font_cache:
            self._font_cache[key] = get_font(scaled_size, bold=bold)
        return self._font_cache[key]

    def rect(self, x0: float, y0: float, x1: float, y1: float, fill, r: float = 0.0) -> None:
        """Draw rectangle or rounded rectangle in base coordinates."""
        b = [x0 * self.k, y0 * self.k, x1 * self.k, y1 * self.k]
        if r > 0.0:
            self.d.rounded_rectangle(b, r * self.k, fill=fill)
        else:
            self.d.rectangle(b, fill=fill)

    def ell(self, cx: float, cy: float, r: float, fill=None, outline=None, width: float = 1.0) -> None:
        """Draw circle/ellipse in base coordinates."""
        b = [(cx - r) * self.k, (cy - r) * self.k, (cx + r) * self.k, (cy + r) * self.k]
        self.d.ellipse(b, fill=fill, outline=outline, width=max(1, int(width * self.k)))

    def poly(self, pts: List[Tuple[float, float]], fill) -> None:
        """Draw polygon with list of (x, y) vertices in base coordinates."""
        scaled_pts = [(x * self.k, y * self.k) for x, y in pts]
        self.d.polygon(scaled_pts, fill=fill)

    def line(self, pts: List[Tuple[float, float]], fill, width: float = 1.0) -> None:
        """Draw polyline in base coordinates."""
        scaled_pts = [(x * self.k, y * self.k) for x, y in pts]
        self.d.line(scaled_pts, fill=fill, width=max(1, int(width * self.k)))

    def txt(self, x: float, y: float, s: str, size: float, fill, anchor: str = "lm", bold: bool = True) -> None:
        """Draw text string in base coordinates."""
        self.d.text((x * self.k, y * self.k), s, font=self.font(size, bold=bold), fill=fill, anchor=anchor)

    def tw(self, s: str, size: float, bold: bool = True) -> float:
        """Measure text advance width in unscaled base coordinates."""
        return self.d.textlength(s, font=self.font(size, bold=bold)) / self.k

    def render(self) -> Image.Image:
        """Downsample the super-sampled buffer back to native target resolution via Lanczos."""
        if self.k == 1.0:
            return self.im
        return self.im.resize((self.width, self.height), Image.LANCZOS)


# ==============================================================================
# 5. 3D PERSPECTIVE PROJECTION & ROTATION
# ==============================================================================

def rotate_3d(x: float, y: float, z: float, rx: float = 0.0, ry: float = 0.0, rz: float = 0.0) -> Tuple[float, float, float]:
    """Rotate 3D coordinates around X, Y, and Z axes using Euler rotation matrices."""
    if rx != 0.0:
        cos_x, sin_x = math.cos(rx), math.sin(rx)
        y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x
    if ry != 0.0:
        cos_y, sin_y = math.cos(ry), math.sin(ry)
        x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y
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
# 6. SCENE TRANSITIONS & POST-PROCESSING
# ==============================================================================

def iris_wipe(img_curr: Image.Image, img_prev: Image.Image, progress: float, max_radius: float = None) -> Image.Image:
    """Seamless circular iris reveal transition from img_prev to img_curr."""
    if progress <= 0.0:
        return img_prev
    if progress >= 1.0:
        return img_curr
    w, h = img_curr.size
    if max_radius is None:
        max_radius = math.hypot(w / 2.0, h / 2.0)
    r = smoothstep(progress) * max_radius
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse(
        [w / 2.0 - r, h / 2.0 - r, w / 2.0 + r, h / 2.0 + r],
        fill=255
    )
    return Image.composite(img_curr, img_prev, mask)

def vertical_push_transition(img_curr: Image.Image, img_prev: Image.Image, progress: float) -> Image.Image:
    """Vertical push/swipe transition where incoming screen pushes outgoing screen upward.
    
    Mirrors native mobile/desktop app screen navigation.
    """
    progress = clamp(progress, 0.0, 1.0)
    k = ease_in_out_cubic(progress)
    off = int(k * img_curr.height)
    canvas = Image.new("RGB", img_curr.size)
    canvas.paste(img_prev, (0, -off))
    canvas.paste(img_curr, (0, img_curr.height - off))
    return canvas

def horizontal_push_transition(img_curr: Image.Image, img_prev: Image.Image, progress: float) -> Image.Image:
    """Horizontal push/swipe transition where incoming screen pushes outgoing screen sideways."""
    progress = clamp(progress, 0.0, 1.0)
    k = ease_in_out_cubic(progress)
    off = int(k * img_curr.width)
    canvas = Image.new("RGB", img_curr.size)
    canvas.paste(img_prev, (-off, 0))
    canvas.paste(img_curr, (img_curr.width - off, 0))
    return canvas

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


# ==============================================================================
# 7. APP UI & PRODUCT SIMULATION HELPERS (VERSION 3)
# ==============================================================================

def generative_cover(pen: Pen, x: float, y: float, size: float, seed: int,
                     base_color: Tuple[int, int, int], radius: float = 6.0) -> None:
    """Generate procedural geometric album cover art with seeded variations (no external images).
    
    Kind 0: Overlapping translucent bubbles/dots.
    Kind 1: Horizontal graphic bars.
    Kind 2: Bold geometric triangle.
    """
    pen.rect(x, y, x + size, y + size, base_color, r=radius)
    dark_tint = lerpc(base_color, (0, 0, 0), 0.35)
    rng = np.random.RandomState(seed)
    kind = seed % 3
    if kind == 0:
        for _ in range(4):
            pen.ell(x + size * rng.uniform(0.2, 0.8),
                    y + size * rng.uniform(0.2, 0.8),
                    size * rng.uniform(0.1, 0.25), dark_tint)
    elif kind == 1:
        for i in range(5):
            pen.rect(x + size * 0.1, y + size * (0.12 + i * 0.16),
                     x + size * rng.uniform(0.3, 0.9), y + size * (0.20 + i * 0.16),
                     dark_tint)
    else:
        pen.poly([
            (x + size * 0.50, y + size * 0.15),
            (x + size * 0.88, y + size * 0.85),
            (x + size * 0.12, y + size * 0.85)
        ], dark_tint)

def mini_eq_bars(pen: Pen, x: float, y: float, t: float, color: Tuple[int, int, int], count: int = 3) -> None:
    """Render miniature animated audio equalizer bars (used in active playlist rows)."""
    for i in range(count):
        h = 6 + 12 * abs(math.sin(t * (7.0 + i * 2.3) + i))
        pen.rect(x + i * 7, y - h, x + i * 7 + 4, y, color)

def draw_cursor(pen: Pen, x: float, y: float, fill: Tuple[int, int, int] = (255, 255, 255)) -> None:
    """Render vector OS mouse pointer arrow for interactive UI micro-interactions."""
    pen.poly([(x, y), (x, y + 30), (x + 8, y + 22), (x + 20, y + 22)], fill)

def button_click_press(t: float, t_click: float, press_dur: float = 0.15,
                       release_dur: float = 0.20, max_scale_reduction: float = 0.08) -> float:
    """Calculate button scale factor (1.0 - 0.08 * press) simulating tactile UI click depression."""
    press = prog(t, t_click, t_click + press_dur) - prog(t, t_click + press_dur, t_click + press_dur + release_dur)
    return 1.0 - max_scale_reduction * clamp(press, 0.0, 1.0)

def draw_click_ripple(pen: Pen, cx: float, cy: float, t: float, t_click: float,
                      duration: float = 0.65, max_radius: float = 120.0,
                      outline_color: Tuple[int, int, int] = (30, 215, 96),
                      bg_color: Tuple[int, int, int] = (18, 18, 18)) -> None:
    """Render expanding and fading circular shockwave ripple on button click."""
    if t_click < t < t_click + duration:
        p = prog(t, t_click, t_click + duration)
        r = ease_out_cubic(p) * max_radius
        col = lerpc(outline_color, bg_color, p)
        pen.ell(cx, cy, r, outline=col, width=3.0)
