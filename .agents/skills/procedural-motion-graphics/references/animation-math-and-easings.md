# Animation Mathematics, Physics & Easing Curves

Procedural motion design relies on deterministic mathematical functions mapping time $t \in \mathbb{R}$ to visual properties (position, scale, rotation, color, opacity). Linear motion feels robotic and unnatural; broadcast-grade motion demands deliberate acceleration, anticipation, overshoot, harmonic oscillation, physical spring dynamics, and responsive UI micro-interactions.

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

## 2. Choosing Between Penner Curves and Spring Physics

| Context | Recommended Motion Model | Why |
| :--- | :--- | :--- |
| **App UI & Product Simulation (V3)** | **Classic Penner Cubic Curves** (`out_cubic`, `in_out`, `out_back`) | Digital interfaces feel fast, predictable, and responsive without prolonged oscillation. |
| **Vector Graphic Bounces (V2)** | **Damped Harmonic Springs** (`spring(x, k, w)`) | Organic physical objects benefit from lingering settling vibrations. |

### 2.1 Classic Penner Curves (UI Responsiveness)
- **Ease-Out Cubic** (Deceleration):
  $$\text{easeOutCubic}(x) = 1 - (1 - x)^3$$
  Used for text reveals, card slides, and button hover/morph states.
- **Ease-In-Out Cubic** (S-Curve):
  $$\text{easeInOutCubic}(x) = \begin{cases} 4x^3 & x < 0.5 \\ 1 - \frac{(-2x + 2)^3}{2} & x \ge 0.5 \end{cases}$$
  Used for app vertical push view transitions, cursor movement paths, and carousel autoscrolling.
- **Ease-Out Back** (Controlled UI Pop-In):
  $$\text{easeOutBack}(x, s) = 1 + (s + 1)(x - 1)^3 + s(x - 1)^2$$
  *(Typically $s = 1.8$ to $1.9$).* Used for album cover pop-ins and avatar badges.

### 2.2 Damped Harmonic Spring Physics
Models a physical mass on a spring subject to viscous damping:

$$f(x) = 1.0 - e^{-k x} \cos(\omega x) \quad (x \ge 0)$$

- $k$: Damping factor (e.g., $k = 7$). Controls how quickly oscillations settle.
- $\omega$: Angular frequency (e.g., $\omega = 14$). Controls the bounce rate.

---

## 3. UI Micro-Interaction Mathematics

Micro-interactions transform a passive motion graphic into a living, tactile software experience.

### 3.1 Button Click Depression (8% Tactile Scaleback)
When a user clicks a button, the element compresses downwards, then rebounds to full scale upon release:

```python
def button_click_press(t: float, t_click: float, press_dur: float = 0.15,
                       release_dur: float = 0.20, max_scale_reduction: float = 0.08) -> float:
    # Triangle pulse during click event
    press = prog(t, t_click, t_click + press_dur) - prog(t, t_click + press_dur, t_click + press_dur + release_dur)
    return 1.0 - max_scale_reduction * clamp(press, 0.0, 1.0)
```

### 3.2 Expanding Shockwave Ripple
At the moment of click, an expanding circular ripple dissipates radially outward:
- Radius: $r(t) = R_{\max} \cdot \text{easeOutCubic}(p)$
- Opacity / Color: Fades linearly from brand accent to background color over $0.65\text{s}$.

### 3.3 Mouse Cursor Trajectory
An OS mouse cursor does not move linearly; it accelerates gently, traverses the screen, and decelerates into the target button using cubic S-curve interpolation:

```python
cx = lerp(x_start, x_target, ease_in_out_cubic(prog(t, t_start, t_end)))
cy = lerp(y_start, y_target, ease_in_out_cubic(prog(t, t_start, t_end)))
```

---

## 4. Disney Animation Principles in Code

### 4.1 Squash & Stretch
When an animated shape bounces against a surface:

$$s_x = 1.0 + \kappa \cdot (1 - \text{bounce})^p, \quad s_y = 2.0 - s_x$$

### 4.2 Dynamic Contact Shadows
Shadow scale and opacity tied to ground distance:

$$\text{shadowScale} = 1.0 - (1.0 - s_{\min}) \cdot \text{bounce}$$

---

## 5. Beat Synchronization & Pulse Clocks

Tie motion frequencies to a musical tempo grid (e.g. 120 BPM = 0.5s per beat):

$$\text{beat}(t) = \exp\left(-\lambda \cdot (t \pmod{T_{\text{beat}}})\right)$$
