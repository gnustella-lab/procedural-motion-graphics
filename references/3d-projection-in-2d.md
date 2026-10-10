# 3D Perspective Projection in Pure 2D Canvases

You don't need a heavy 3D engine (OpenGL, Three.js, Blender) to create captivating 3D orbital particle clouds and geometric forms. Pure vector mathematics projected onto Pillow canvases provides lightweight, zero-dependency 3D rendering.

---

## 1. 3D Coordinate System & Euler Rotations

Define points in world space as $(x, y, z)$. Rotate points around coordinate axes using standard 3D rotation matrices:

### Rotation around X-axis (Pitch / Tilt):
$$\begin{bmatrix} x' \\ y' \\ z' \end{bmatrix} = \begin{bmatrix} 1 & 0 & 0 \\ 0 & \cos\theta & -\sin\theta \\ 0 & \sin\theta & \cos\theta \end{bmatrix} \begin{bmatrix} x \\ y \\ z \end{bmatrix}$$

### Rotation around Y-axis (Yaw / Spin):
$$\begin{bmatrix} x' \\ y' \\ z' \end{bmatrix} = \begin{bmatrix} \cos\phi & 0 & \sin\phi \\ 0 & 1 & 0 \\ -\sin\phi & 0 & \cos\phi \end{bmatrix} \begin{bmatrix} x \\ y \\ z \end{bmatrix}$$

```python
def rotate_3d(x, y, z, rx=0.0, ry=0.0):
    # X-axis tilt
    y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
    # Y-axis spin
    x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
    return x, y, z
```

---

## 2. Perspective Projection (Pinhole Camera Model)

A point at distance $z$ scales inversely proportional to its distance from the virtual camera focal point:

$$s = \frac{\text{fov}}{\text{fov} + z + z_{\text{offset}}}$$
$$p_x = c_x + x \cdot s$$
$$p_y = c_y + y \cdot s$$

Where:
- $\text{fov} \approx 900$: Focal length / field of view
- $z_{\text{offset}} \approx 600$: Distance from camera origin to world origin

---

## 3. Painter's Algorithm (Depth Sorting)

Because 2D canvases lack hardware Z-buffers, elements must be rendered back-to-front:

```python
# Sort descending by Z (farthest elements first, closest elements last)
pts3.sort(key=lambda p: -p[2])
```

---

## 4. Atmospheric Perspective & Depth Cueing

Real optics cause distant objects to lose contrast and bleed into ambient background atmosphere:

```python
# Compute normalized depth factor (0.0 = deep background, 1.0 = foreground)
depth = clamp(1.0 - (z + 500) / 1000)

# Scale particle radius based on perspective
r = max(1, 9 * s)

# Blend color towards background dark navy
c_depth = lerpc(BG, c, 0.35 + 0.65 * depth)
```

---

## 5. Compound Sine Ribbons

3D ribbons can be emulated on the 2D plane by combining dual spatial frequencies:

$$y(x, t) = c_y + A(t) \cdot \sin(k_1 x + \omega_1 t) \cdot \sin(k_2 x + \omega_2 t)$$

The product of two sine waves acts as an amplitude modulator, creating organic twisting ribbon behavior.
