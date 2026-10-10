"""Procedural 15-second motion graphics showreel.
Renders 1920x1080 @ 30fps entirely in code (Pillow + NumPy), encodes H.264 via imageio-ffmpeg.
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import imageio.v2 as imageio

W, H, FPS, DUR = 1920, 1080, 30, 15.0
N = int(FPS * DUR)
SS = 1  # supersample factor for shapes layer
random.seed(7); np.random.seed(7)

# ---------- palette ----------
BG = (10, 10, 18)
PINK = (255, 46, 136)
CYAN = (0, 229, 255)
YEL = (255, 214, 0)
WHITE = (245, 245, 250)
VIO = (124, 77, 255)
PAL = [PINK, CYAN, YEL, VIO, WHITE]

def font(size, bold=True):
    for f in (["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"] if bold
              else ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]):
        try: return ImageFont.truetype(f, size)
        except OSError: pass
    return ImageFont.load_default()

# ---------- easing ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, a, b): return clamp((t - a) / (b - a))
def ease_out_cubic(x): return 1 - (1 - x) ** 3
def ease_in_out_cubic(x): return 4*x**3 if x < .5 else 1 - (-2*x + 2)**3 / 2
def ease_in_expo(x): return 0 if x == 0 else 2 ** (10*x - 10)
def ease_out_expo(x): return 1 if x == 1 else 1 - 2 ** (-10*x)
def ease_out_back(x, s=1.70158):
    c3 = s + 1; return 1 + c3*(x-1)**3 + s*(x-1)**2
def ease_out_elastic(x):
    if x in (0, 1): return x
    return 2 ** (-10*x) * math.sin((x*10 - .75) * (2*math.pi/3)) + 1
def lerp(a, b, t): return a + (b - a) * t
def lerpc(c1, c2, t): return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))

# ---------- precomputed background ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
cx, cy = W/2, H/2
rr = np.sqrt((xx-cx)**2 + (yy-cy)**2) / math.hypot(cx, cy)
VIGNETTE = (1 - 0.65 * rr**2).clip(0, 1)[..., None]
GRAIN = [np.random.normal(0, 7, (H, W, 1)).astype(np.float32) for _ in range(6)]

def background(t, tint):
    # slow moving dual radial gradient
    ax = cx + math.cos(t*0.7) * 500; ay = cy + math.sin(t*0.9) * 250
    d = np.sqrt((xx-ax)**2 + (yy-ay)**2) / 1400
    g = np.exp(-d*3)[..., None]
    base = np.array(BG, np.float32) + g * np.array(tint, np.float32) * 0.22
    return base

# ---------- particles ----------
class P:
    def __init__(s):
        s.a = random.uniform(0, 2*math.pi); s.sp = random.uniform(300, 1400)
        s.r = random.uniform(2, 7); s.c = random.choice(PAL); s.dr = random.uniform(0.6, 1.3)
BURST = [P() for _ in range(220)]
STARS = [(random.uniform(0, W), random.uniform(0, H), random.uniform(.2, 1), random.choice(PAL)) for _ in range(160)]

def text_center(d, xy, s, f, fill, anchor="mm"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)

def rot_poly(cx, cy, r, n, ang):
    return [(cx + r*math.cos(ang + i*2*math.pi/n), cy + r*math.sin(ang + i*2*math.pi/n)) for i in range(n)]

# ================= SCENES =================
# Each scene draws onto RGBA layer `L` (ImageDraw d). Returns (tint color, camera shake, zoom).

def scene_intro(t, L, d):
    """0-2.4s: dot -> elastic ring burst -> kinetic letter drop 'MOTION'."""
    # dot pop
    p = prog(t, 0, .35)
    r = 18 * ease_out_back(p) if t < .55 else 18 * (1 - ease_in_expo(prog(t, .45, .55)))
    if r > 0: d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=WHITE)
    # shockwave rings
    for i, c in enumerate([PINK, CYAN, YEL]):
        q = prog(t, .55 + i*.07, 1.5 + i*.07)
        if 0 < q < 1:
            R = ease_out_expo(q) * (900 - i*150); w = max(1, int(40 * (1-q)))
            d.ellipse([cx-R, cy-R, cx+R, cy+R], outline=c + (int(255*(1-q)),), width=w)
    # particle burst with drag
    q = prog(t, .55, 2.4)
    if 0 < q < 1:
        e = ease_out_expo(q)
        for b in BURST:
            dist = b.sp * e * b.dr
            x = cx + math.cos(b.a)*dist; y = cy + math.sin(b.a)*dist + 200*q*q
            rr_ = b.r * (1-q)
            # streak = motion trail
            tx = cx + math.cos(b.a)*dist*0.92; ty = cy + math.sin(b.a)*dist*0.92 + 200*q*q
            d.line([tx, ty, x, y], fill=b.c + (int(200*(1-q)),), width=max(1, int(rr_)))
            d.ellipse([x-rr_, y-rr_, x+rr_, y+rr_], fill=b.c)
    # staggered letter drop
    word = "MOTION"; f = font(260); sp = 205
    x0 = cx - sp*(len(word)-1)/2
    for i, ch in enumerate(word):
        q = prog(t, .8 + i*.07, 1.45 + i*.07)
        out = prog(t, 2.05 + i*.03, 2.4)
        if q <= 0: continue
        y = lerp(-250, cy, ease_out_back(q, 2.2)) - ease_in_expo(out) * 900
        col = PAL[i % 3] if q < 1 and int(t*30) % 2 else WHITE
        # chromatic offset shadow
        text_center(d, (x0+i*sp+8, y+8), ch, f, PINK + (150,))
        text_center(d, (x0+i*sp-8, y-4), ch, f, CYAN + (150,))
        text_center(d, (x0+i*sp, y), ch, f, col)
    shake = 14 * max(0, 1 - prog(t, .55, .9)) if t > .55 else 0
    return PINK, shake, 1 + 0.04*t

def scene_grid(t, L, d):
    """2.4-5.2s: staggered wave grid of shapes morphing triangle->square->hex->circle."""
    lt = t - 2.4
    cols, rows, s = 16, 9, 120
    ox, oy = (W - cols*s)/2 + s/2, (H - rows*s)/2 + s/2
    intro = ease_out_cubic(prog(lt, 0, .3))
    for j in range(rows):
        for i in range(cols):
            x, y = ox + i*s, oy + j*s
            dist = math.hypot(i - cols/2, j - rows/2)
            delay = dist * .06
            a = ease_out_back(prog(lt, delay, delay + .5))
            o = ease_in_expo(prog(lt, 2.3 + (cols - i)*0.02, 2.8))
            sc = a * (1 - o)
            if sc <= 0: continue
            wave = .5 + .5*math.sin(lt*5 - dist*.8)
            r = s*.38*sc*(.55 + .45*wave)
            n = [3, 4, 6, 40][int((lt*1.6 + dist*.15)) % 4]
            ang = lt*2 + dist*.3
            c = lerpc(PINK, CYAN, wave) if (i+j) % 2 else lerpc(VIO, YEL, wave)
            if (i*7 + j*3) % 5 == 0:
                d.polygon(rot_poly(x, y, r, n, ang), outline=c, width=5)
            else:
                d.polygon(rot_poly(x, y, r, n, ang), fill=c)
    # sweeping label with mask wipe
    f = font(120)
    q = ease_out_expo(prog(lt, .5, 1.1)); qo = ease_in_expo(prog(lt, 2.0, 2.4))
    bw = 1150 * q * (1 - qo)
    if bw > 2:
        d.rectangle([cx - bw/2, cy-85, cx + bw/2, cy+85], fill=BG + (235,))
        tl = Image.new("L", (W, H), 0); td = ImageDraw.Draw(tl)
        td.text((cx, cy), "SHAPE & RHYTHM", font=f, fill=255, anchor="mm")
        m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rectangle([cx-bw/2, cy-85, cx+bw/2, cy+85], fill=255)
        L.paste(Image.new("RGBA", (W, H), YEL + (255,)), (0, 0), ImageChops.multiply(tl, m))
    return CYAN, 0, 1.0 + .06*ease_in_out_cubic(prog(lt, 0, 2.8))

def scene_type(t, L, d):
    """5.2-8.4s: kinetic typography with slide wipes, counters and stroke reveals."""
    lt = t - 5.2
    words = [("DESIGN", PINK), ("ANIMATE", CYAN), ("TELL STORIES", YEL)]
    seg = 1.05
    k = min(2, int(lt // seg)); st = lt - k*seg
    w, c = words[k]
    # full-screen color wipe panel
    pin = ease_out_expo(prog(st, 0, .35)); pout = ease_in_expo(prog(st, .75, seg))
    x1 = lerp(-W, 0, pin) + lerp(0, W, pout)
    d.polygon([(x1-200, 0), (x1+W+200, 0), (x1+W, H), (x1-400, H)], fill=c + (255,))
    # big type slides with per-letter stagger, cut by panel
    f = font(230 if k < 2 else 180)
    tx = cx; total = len(w)
    bbox = d.textbbox((0, 0), w, font=f); tw = bbox[2] - bbox[0]
    xs = cx - tw/2
    acc = 0
    for i, ch in enumerate(w):
        cw = d.textlength(ch, font=f)
        q = ease_out_back(prog(st, .08 + i*.025, .5 + i*.025), 1.4)
        o = ease_in_expo(prog(st, .7 + i*.015, .95 + i*.015))
        y = cy + lerp(180, 0, q) - o*260
        a = int(255 * clamp(q*2) * (1-o))
        d.text((xs + acc, y), ch, font=f, fill=BG + (a,), anchor="lm")
        acc += cw
    # counter / small HUD
    fs = font(36, False)
    d.text((80, 80), f"0{k+1} / 03", font=font(44), fill=BG)
    d.text((80, H-80), f"FRAME {int(t*FPS):04d}", font=fs, fill=BG, anchor="lm")
    d.line([(80, H-120), (80 + (W-160)*prog(lt, 0, 3.2), H-120)], fill=BG, width=6)
    return c, 0, 1 + .03*math.sin(st*3)

def scene_orbit(t, L, d):
    """8.4-11.2s: 3D-projected orbital particle system + sine-wave ribbons."""
    lt = t - 8.4
    intro = ease_out_expo(prog(lt, 0, .8)); outro = ease_in_expo(prog(lt, 2.3, 2.8))
    # sine ribbons
    for k, c in enumerate([PINK, CYAN, VIO]):
        pts = []
        for x in range(0, W+1, 16):
            amp = 160 * intro * (1-outro)
            y = cy + amp*math.sin(x*.006 + lt*3 + k*1.3) * math.sin(x*.0015 + lt)
            pts.append((x, y + (k-1)*30))
        d.line(pts, fill=c + (170,), width=4, joint="curve")
    # 3D rings of particles (perspective projection, depth sorted)
    pts3 = []
    for ring in range(3):
        n = 60; R = 380 + ring*90
        tilt = .9 + ring*.35 + lt*.3
        for i in range(n):
            a = i/n*2*math.pi + lt*(1.2 - ring*.3)
            x, y, z = R*math.cos(a), 0, R*math.sin(a)
            y, z = y*math.cos(tilt) - z*math.sin(tilt), y*math.sin(tilt) + z*math.cos(tilt)
            ry = lt*.8 + ring
            x, z = x*math.cos(ry) + z*math.sin(ry), -x*math.sin(ry) + z*math.cos(ry)
            pts3.append((x, y, z, PAL[ring]))
    pts3.sort(key=lambda p: -p[2])
    fov = 900
    for x, y, z, c in pts3:
        s = fov / (fov + z + 600) * intro * (1 - outro) * 1.6
        px, py = cx + x*s, cy + y*s
        r = max(1, 9*s)
        depth = clamp(1 - (z + 500)/1000)
        d.ellipse([px-r, py-r, px+r, py+r], fill=lerpc(BG, c, .35 + .65*depth))
    # core
    cr = 90 * ease_out_elastic(prog(lt, .1, 1.2)) * (1 - outro)
    if cr > 0:
        for i in range(4):
            rr_ = cr*(1 + i*.18)
            d.ellipse([cx-rr_, cy-rr_, cx+rr_, cy+rr_], outline=WHITE + (int(220/(i+1)),), width=3)
        d.ellipse([cx-cr*.6, cy-cr*.6, cx+cr*.6, cy+cr*.6], fill=WHITE)
    d.text((cx, H-110), "SYSTEMS  ·  PHYSICS  ·  DEPTH", font=font(48), fill=WHITE + (int(255*intro*(1-outro)),), anchor="mm")
    return VIO, 0, 1 + .15*ease_in_expo(prog(lt, 2.0, 2.8))

def scene_cuts(t, L, d):
    """11.2-13.2s: hyper-fast rhythmic cuts (one per 4 frames), radial speed lines, strobing type."""
    lt = t - 11.2
    beat = int(lt * FPS / 4)
    c = PAL[beat % 4]; c2 = PAL[(beat+2) % 4]
    random.seed(beat)
    d.rectangle([0, 0, W, H], fill=c + (255,))
    mode = beat % 3
    if mode == 0:  # radial speed lines
        for i in range(70):
            a = random.uniform(0, 2*math.pi); r0 = random.uniform(150, 400)
            d.line([cx+math.cos(a)*r0, cy+math.sin(a)*r0, cx+math.cos(a)*2000, cy+math.sin(a)*2000], fill=c2, width=random.randint(2, 14))
    elif mode == 1:  # stripes
        off = (lt*1500) % 160
        for x in range(-400, W+400, 160):
            d.polygon([(x+off, 0), (x+off+70, 0), (x+off-330, H), (x+off-400, H)], fill=c2)
    else:  # concentric squares spin
        for i in range(12, 0, -1):
            d.polygon(rot_poly(cx, cy, i*90, 4, lt*3 + i*.15), fill=c2 if i % 2 else c)
    wordz = ["BOLD", "FAST", "LOUD", "SHARP", "CLEAN", "PUNCH", "FLOW", "IMPACT"]
    wd = wordz[beat % len(wordz)]
    local = (lt*FPS % 4) / 4
    f = font(int(lerp(300, 340, local)))
    d.text((cx+10, cy+10), wd, font=f, fill=BG + (255,), anchor="mm")
    d.text((cx, cy), wd, font=f, fill=WHITE, anchor="mm")
    return c, 10, 1 + .05*local

def scene_logo(t, L, d):
    """13.2-15s: iris close, logo build with line-draw, title reveal, end hold."""
    lt = t - 13.2
    # iris: big circle shrinking from cuts colour into dark
    q = ease_in_out_cubic(prog(lt, 0, .45))
    R = lerp(1300, 0, q)
    if R > 0:
        d.rectangle([0, 0, W, H], fill=YEL)
        d.ellipse([cx-(1300-R)*1.0, cy-(1300-R), cx+(1300-R), cy+(1300-R)], fill=BG)
    # logo mark: hexagon line-draw + inner triangle pop
    p = ease_in_out_cubic(prog(lt, .35, 1.0))
    hexp = rot_poly(cx, cy-90, 130, 6, -math.pi/2) + [rot_poly(cx, cy-90, 130, 6, -math.pi/2)[0]]
    segs = p * 6
    for i in range(int(segs) + 1):
        if i >= 6: break
        f_ = clamp(segs - i)
        a, b = hexp[i], hexp[i+1]
        d.line([a, (lerp(a[0], b[0], f_), lerp(a[1], b[1], f_))], fill=CYAN, width=12)
    tri = ease_out_elastic(prog(lt, .8, 1.6))
    if tri > 0:
        d.polygon(rot_poly(cx, cy-90, 70*tri, 3, -math.pi/2 + (1-tri)*2), fill=PINK)
    # title reveal: letters rise through a mask line
    f = font(110); title = "MOTION DESIGN"
    tw = d.textlength(title, font=f); x = cx - tw/2
    for i, ch in enumerate(title):
        qq = ease_out_expo(prog(lt, .9 + i*.025, 1.4 + i*.025))
        if qq <= 0: x += d.textlength(ch, font=f); continue
        d.text((x, cy + 150 + (1-qq)*80), ch, font=f, fill=WHITE + (int(255*qq),), anchor="ls")
        x += d.textlength(ch, font=f)
    ul = ease_out_expo(prog(lt, 1.2, 1.7))
    d.rectangle([cx - 380*ul, cy+180, cx + 380*ul, cy+186], fill=YEL)
    sub = ease_out_cubic(prog(lt, 1.35, 1.75))
    d.text((cx, cy + 235), "SHOWREEL  2026", font=font(42, False), fill=WHITE + (int(220*sub),), anchor="mm")
    return CYAN, 0, 1 + .03*prog(lt, .4, 1.8)

SCENES = [(0, 2.4, scene_intro), (2.4, 5.2, scene_grid), (5.2, 8.4, scene_type),
          (8.4, 11.2, scene_orbit), (11.2, 13.2, scene_cuts), (13.2, 15.01, scene_logo)]

def render_layer(t):
    for a, b, fn in SCENES:
        if a <= t < b:
            L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
            tint, shake, zoom = fn(t, L, d)
            return L, tint, shake, zoom, a
    raise ValueError(t)

def frame(i):
    t = i / FPS
    L, tint, shake, zoom, a = render_layer(t)
    # camera: zoom about centre + shake
    if zoom != 1:
        nw, nh = int(W*zoom), int(H*zoom)
        L = L.resize((nw, nh), Image.BICUBIC).crop(((nw-W)//2, (nh-H)//2, (nw-W)//2 + W, (nh-H)//2 + H))
    if shake:
        L = ImageChops.offset(L, int(random.uniform(-shake, shake)), int(random.uniform(-shake, shake)))
    bg = background(t, tint)
    rgb = np.asarray(L, np.float32)
    al = rgb[..., 3:4] / 255
    img = bg*(1-al) + rgb[..., :3]*al
    # glow (bloom) pass: blur bright parts and add
    small = Image.fromarray(img.clip(0, 255).astype(np.uint8)).resize((W//4, H//4), Image.BILINEAR)
    glow = np.asarray(small.filter(ImageFilter.GaussianBlur(8)).resize((W, H), Image.BILINEAR), np.float32)
    img = img + np.maximum(glow - 90, 0) * 0.55
    # chromatic aberration (horizontal RGB split) stronger at scene cuts
    since = t - a
    ca = 2 + int(14 * max(0, 1 - since/0.2))
    img[..., 0] = np.roll(img[..., 0], ca, axis=1)
    img[..., 2] = np.roll(img[..., 2], -ca, axis=1)
    # white flash frame on cuts
    if a > 0 and since < 2/FPS:
        img = img*0.4 + 255*0.6
    # vignette + film grain + letterbox-free output
    img = img * VIGNETTE + GRAIN[i % len(GRAIN)]
    # final fade
    img *= clamp((DUR - t) / 0.25) if t > DUR - 0.25 else 1
    img *= clamp(t / 0.15) if t < 0.15 else 1
    return img.clip(0, 255).astype(np.uint8)

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "showreel.mp4"
    w = imageio.get_writer(out, fps=FPS, codec="libx264", quality=9, pixelformat="yuv420p", macro_block_size=8)
    for i in range(N):
        random.seed(1000 + i)
        w.append_data(frame(i))
        if i % 30 == 0: print(f"frame {i}/{N}", flush=True)
    w.close()
    print("done", out)
