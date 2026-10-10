# Animation Mathematics & Easing Curves

Procedural motion design relies on deterministic mathematical functions mapping time $t \in \mathbb{R}$ to visual properties (position, scale, rotation, color, opacity). Linear motion feels robotic and unnatural; organic, broadcast-grade motion requires deliberate acceleration, anticipation, overshoot, and harmonic oscillation.

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

## 2. Easing Curves Reference

### 2.1 Cubic Easing (Fluid Motion)
Cubic easing mimics natural inertia with a constant third derivative.

- **Ease-Out Cubic** (Deceleration):
  $$\text{easeOutCubic}(x) = 1 - (1 - x)^3$$
  Used when elements enter the screen and smoothly glide to a halt.

- **Ease-In-Out Cubic** (Smooth S-Curve):
  $$\text{easeInOutCubic}(x) = \begin{cases} 4x^3 & x < 0.5 \\ 1 - \frac{(-2x + 2)^3}{2} & x \ge 0.5 \end{cases}$$
  Used for camera zooms, iris transitions, and looping geometric morphs.

### 2.2 Exponential Easing (High-Impact Snappiness)
Exponential curves create extreme velocity contrasts—nearly instantaneous transitions that feel crisp and punchy.

- **Ease-Out Expo** (Instant entrance, gradual settle):
  $$\text{easeOutExpo}(x) = \begin{cases} 1 & x = 1 \\ 1 - 2^{-10x} & x < 1 \end{cases}$$
  Used for snappy color wipe panels, shockwave ring expansion, and title fades.

- **Ease-In Expo** (Anticipation to explosive exit):
  $$\text{easeInExpo}(x) = \begin{cases} 0 & x = 0 \\ 2^{10x - 10} & x > 0 \end{cases}$$
  Used for exit flings, launching elements offscreen, and camera punch-ins.

### 2.3 Back Easing (Anticipation & Overshoot)
Simulates momentum overshooting the target and snapping back into position.

$$\text{easeOutBack}(x, s) = 1 + (s + 1)(x - 1)^3 + s(x - 1)^2$$
*(Default overshoot constant $s \approx 1.70158$, or $s = 2.2$ for aggressive stylized bounces).*

**Usage**: Kinetic typography drops, pop-in icons, dot pops, and UI cards.

### 2.4 Elastic Easing (Damped Harmonic Oscillator)
Models a physical spring attached to a mass settling under viscous damping:

$$\text{easeOutElastic}(x) = 2^{-10x} \sin\left(\left(10x - 0.75\right) \cdot \frac{2\pi}{3}\right) + 1$$

**Usage**: High-energy logo reveals, inner core explosions, and secondary accents.

---

## 3. Stagger & Delay Propagation

Motion graphics gain depth when elements react in sequence rather than simultaneously.

### 3.1 Linear Sequence Stagger
For words and lists, delay each item $i$ by a constant $\Delta$:

$$t_{\text{start}, i} = t_0 + i \cdot \Delta$$

```python
for i, char in enumerate(word):
    q = prog(t, t_start + i * 0.07, t_settle + i * 0.07)
    y = lerp(-250, cy, ease_out_back(q, 2.2))
```

### 3.2 Radial Distance Bloom Stagger
In a 2D matrix or particle cloud, elements trigger based on their Euclidean distance $d$ from an epicenter $(c_x, c_y)$:

$$d_{ij} = \sqrt{(i - c_x)^2 + (j - c_y)^2}$$
$$\text{delay}_{ij} = d_{ij} \cdot \kappa$$

```python
delay = math.hypot(col - center_col, row - center_row) * 0.06
scale = ease_out_back(prog(local_t, delay, delay + 0.5))
```

---

## 4. Harmonic Wave Motion

Combining sine waves with spatial offsets creates fluid organic ripple effects:

$$\text{wave}(t, d) = 0.5 + 0.5 \cdot \sin(\omega t - k \cdot d)$$

- $\omega$: Temporal angular frequency (speed of wave propagation)
- $k$: Spatial wave number (frequency of rings per unit distance)

---

## 5. Particle Physics & Velocity Trails

For explosions without full rigid-body physics, procedural ballistic equations suffice:

$$x(t) = c_x + \cos(\theta) \cdot v \cdot e(q) \cdot d_r$$
$$y(t) = c_y + \sin(\theta) \cdot v \cdot e(q) \cdot d_r + g \cdot q^2$$

- $\theta \sim \mathcal{U}(0, 2\pi)$: Radial launch angle
- $v$: Initial velocity
- $e(q) = \text{easeOutExpo}(q)$: Deceleration curve
- $d_r$: Individual drag coefficient
- $g \cdot q^2$: Quadratic gravity term

**Velocity Trails (Cheap Motion Blur)**:
Instead of expensive multi-frame temporal supersampling, draw a line from the particle's trailing position ($0.92 \cdot \text{dist}$) to its current position $(x, y)$ with decaying opacity.
