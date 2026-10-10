# Animation Mathematics, Physics & Easing Curves

Procedural motion design relies on deterministic mathematical functions mapping time $t \in \mathbb{R}$ to visual properties (position, scale, rotation, color, opacity). Linear motion feels robotic and unnatural; broadcast-grade motion demands deliberate acceleration, anticipation, overshoot, harmonic oscillation, and physical spring dynamics.

---

## 1. Time Normalization & Progress

To decouple animation timing from raw seconds or frame numbers, normalize time into interval progress $p \in [0, 1]$:

```python
def clamp(x: float, a: float = 0.0, b: float = 1.0) -> float:
    return max(a, min(b, x))

def prog(t: float, start: float, end: float) -> float:
    """Normalized progress in [0, 1] across [start, end]."""
    if end == start:
        return 1.0 if t >= start else 0.0
    return clamp((t - start) / (end - start))
```

---

## 2. Spring Physics vs. Canned Easings

While classical Bézier curves (cubic, expo) work well for UI glides, **physically grounded damped spring physics** produces vastly superior, tactile motion for typography and vector objects.

### 2.1 Damped Harmonic Spring Physics (Recommended)
Models a physical mass on a spring subject to viscous damping:

$$f(x) = 1.0 - e^{-k x} \cos(\omega x) \quad (x \ge 0)$$

- $k$: Damping factor (e.g., $k = 7$). Controls how quickly oscillations settle.
- $\omega$: Angular frequency (e.g., $\omega = 14$). Controls the bounce rate.

```python
def spring(x: float, k: float = 7.0, w: float = 14.0) -> float:
    """Natural, organic overshoot and settling vibration."""
    if x <= 0.0:
        return 0.0
    return 1.0 - math.exp(-k * x) * math.cos(w * x)
```

**Why Springs Beat Static Easings:**
1. **Dynamic Realism**: Unlike static `easeOutBack`, a spring continues settling with microscopic natural reverberation.
2. **Organic Weight**: Adjusting $k$ and $\omega$ simulates heavy massive blocks ($k=10, \omega=10$) versus light bouncy pills ($k=5, \omega=18$).

### 2.2 Hermite Smoothstep (Fills & Reveals)
The standard cubic polynomial S-curve with zero first derivatives at $x=0$ and $x=1$:

$$\text{smoothstep}(x) = 3x^2 - 2x^3 \quad (x \in [0, 1])$$

```python
def smoothstep(x: float) -> float:
    x = clamp(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)
```
Ideal for linear wipes, percentage progress bar fills, and iris transitions.

---

## 3. Classic Easing Curves Reference

### 3.1 Cubic Easing
- **Ease-Out Cubic** (Deceleration):
  $$\text{easeOutCubic}(x) = 1 - (1 - x)^3$$
- **Ease-In-Out Cubic** (Smooth S-Curve):
  $$\text{easeInOutCubic}(x) = \begin{cases} 4x^3 & x < 0.5 \\ 1 - \frac{(-2x + 2)^3}{2} & x \ge 0.5 \end{cases}$$

### 3.2 Exponential Easing (High-Impact Snappiness)
- **Ease-Out Expo** (Instant entrance, gradual settle):
  $$\text{easeOutExpo}(x) = \begin{cases} 1 & x = 1 \\ 1 - 2^{-10x} & x < 1 \end{cases}$$
- **Ease-In Expo** (Anticipation to explosive exit):
  $$\text{easeInExpo}(x) = \begin{cases} 0 & x = 0 \\ 2^{10x - 10} & x > 0 \end{cases}$$

### 3.3 Back Easing (Anticipation & Overshoot)
$$\text{easeOutBack}(x, s) = 1 + (s + 1)(x - 1)^3 + s(x - 1)^2$$
*(Default $s \approx 1.70158$, or $s = 2.2$ for aggressive stylized bounces).*

---

## 4. Disney Animation Principles in Code

### 4.1 Squash & Stretch
When an animated shape bounces against a surface, volume preservation requires horizontal expansion when compressed vertically:

$$s_x = 1.0 + \kappa \cdot (1 - \text{bounce})^p$$
$$s_y = 2.0 - s_x$$

- $\text{bounce} = |\sin(\pi \cdot \phi)| \in [0, 1]$: Current height off the ground.
- $\kappa$: Squash intensity (typically $0.3 - 0.4$).
- $p$: Exponent (e.g., $p = 6$). Confines the deformation strictly to the moment of surface contact.

```python
def squash_and_stretch(bounce: float, intensity: float = 0.35, power: float = 6.0, is_landing: bool = True) -> Tuple[float, float]:
    sx = 1.0 + intensity * ((1.0 - bounce) ** power) * (1.0 if is_landing else 0.0)
    sy = 2.0 - sx
    return sx, sy
```

### 4.2 Dynamic Contact Shadows
Ground shadows give floating/bouncing elements tactile anchoring in the 2D plane:
1. **Scale**: Contracts as the object rises, expands as it impacts the floor.
2. **Opacity / Tint**: Fades as the object gains altitude.

$$\text{shadowScale} = 1.0 - (1.0 - s_{\min}) \cdot \text{bounce}$$

```python
# Shadow expands and darkens on ground contact
p.ellipse([cx - r * shadow_scale, floor_y - 10, cx + r * shadow_scale, floor_y + 10], fill=shadow_col)
```

---

## 5. Stagger & Delay Propagation

Motion graphics gain depth when elements react in sequence rather than simultaneously.

### 5.1 Linear Sequence Stagger
For typography and ranked lists, delay each item $i$ by a constant $\Delta$:

$$t_{\text{start}, i} = t_0 + i \cdot \Delta$$

```python
for i, item in enumerate(items):
    delay = i * 0.08
    q = spring(prog(t, t_start + delay, t_end + delay))
    x = lerp(1400, 70, q)
```

### 5.2 Radial Distance Bloom Stagger
Elements trigger based on their Euclidean distance $d$ from an epicenter $(c_x, c_y)$:

$$d_{ij} = \sqrt{(i - c_x)^2 + (j - c_y)^2}$$
$$\text{delay}_{ij} = d_{ij} \cdot \kappa$$

---

## 6. Beat Synchronization & Pulse Clocks

Tie motion frequencies to a musical tempo grid (e.g. 120 BPM = 0.5s per beat):

$$\text{beat}(t) = \exp\left(-\lambda \cdot (t \pmod{T_{\text{beat}}})\right)$$

```python
def beat(t: float, bpm: float = 120.0) -> float:
    beat_dur = 60.0 / bpm
    return math.exp(-6.0 * (t % beat_dur))
```
Multiply this pulse against scale, shadow radii, and accent amplitudes to create rhythmic visual resonance.
