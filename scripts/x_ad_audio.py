"""Procedural soundtrack for the X 15s ad (V4 Golden Standard).

120 BPM, A minor (Am - F - C - G). Every sound is synthesized with NumPy/SciPy:
kick, clap, hats, sub bass, pad, pluck arp, risers, whooshes and UI SFX
(taps, like pop, typing ticks, notification chimes, logo impact).
Timings mirror the scene timeline in x_ad.py.
"""

import wave
import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
DUR = 15.0
N = int(SR * DUR)
BEAT = 0.5
OFF = 0.05            # beat grid offset (first kinetic word lands at 0.05s)

# Scene starts (keep in sync with visual timeline)
S_FEED, S_COMPOSE, S_REACT, S_END = 3.05, 7.55, 10.05, 12.05

rng = np.random.default_rng(7)


def tt(sec):
    return np.arange(int(sec * SR)) / SR


def noise(sec):
    return rng.standard_normal(int(sec * SR))


def filt(x, kind, f):
    sos = butter(2, f, btype=kind, fs=SR, output="sos")
    return sosfilt(sos, x)


def add(buf, sig, t0, gain=1.0, pan=0.0):
    i0 = int(round(t0 * SR))
    if i0 >= N or i0 < 0:
        return
    sig = sig[: N - i0]
    th = (pan + 1.0) * np.pi / 4.0
    buf[i0:i0 + len(sig), 0] += sig * gain * np.cos(th) * np.sqrt(2)
    buf[i0:i0 + len(sig), 1] += sig * gain * np.sin(th) * np.sqrt(2)


def saw(f, t, harmonics=10):
    out = np.zeros_like(t)
    for k in range(1, harmonics + 1):
        if f * k > 9000:
            break
        out += np.sin(2 * np.pi * f * k * t) / k
    return out * 0.6


# ---------------------------------------------------------------- instruments
def kick(big=False):
    t = tt(0.9 if big else 0.45)
    f = 44 + (150 if big else 115) * np.exp(-t * 26)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * (3.5 if big else 7.5))
    click = filt(noise(len(t) / SR), "highpass", 2500) * np.exp(-t * 400) * 0.25
    return np.tanh((body + click) * 1.6) * 0.9


def clap():
    t = tt(0.35)
    n = filt(noise(0.35), "bandpass", [900, 6000])
    env = np.zeros_like(t)
    for d in (0.0, 0.011, 0.023):
        env += np.where(t >= d, np.exp(-(t - d) * 55), 0) * 0.5
    env += np.exp(-t * 14) * 0.6
    body = np.sin(2 * np.pi * 185 * t) * np.exp(-t * 35) * 0.3
    return (n * env * 0.35 + body)


def hat(open_=False):
    t = tt(0.25 if open_ else 0.07)
    n = filt(noise(len(t) / SR), "highpass", 7500)
    return n * np.exp(-t * (14 if open_ else 70)) * 0.35


def bass_note(f, dur):
    t = tt(dur)
    env = np.minimum(1, t / 0.006) * np.exp(-t * 4.0)
    sig = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t) + 0.1 * saw(f, t, 6)
    return np.tanh(sig * env * 1.2) * 0.55


def pad_chord(freqs, dur, cutoff):
    t = tt(dur)
    sig = np.zeros_like(t)
    for f in freqs:
        for det in (-0.12, 0.0, 0.11):
            sig += saw(f * 2 ** (det / 12), t, 12)
    sig = filt(sig, "lowpass", cutoff)
    env = np.minimum(1, t / 0.25) * np.minimum(1, (dur - t) / 0.25)
    return sig * env * 0.07


def pluck(f, dur=0.25):
    t = tt(dur)
    sig = filt(saw(f, t, 14), "lowpass", 3800)
    return sig * np.exp(-t * 11) * np.minimum(1, t / 0.002) * 0.35


def riser(dur):
    t = tt(dur)
    x = t / dur
    n = filt(noise(dur), "bandpass", [600, 7000]) * x ** 2.2 * 0.35
    f = 220 + 1200 * x ** 2
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * x ** 2 * 0.08
    return n + tone


def whoosh(dur=0.45, lo=300, hi=5000):
    t = tt(dur)
    x = t / dur
    n = noise(dur)
    a = filt(n, "bandpass", [lo, hi * 0.4])
    b = filt(n, "bandpass", [lo * 3, hi])
    sig = a * (1 - x) + b * x
    return sig * np.sin(np.pi * x) ** 2 * 0.45


def tap_sfx():
    t = tt(0.06)
    s = np.sin(2 * np.pi * 1900 * t) * np.exp(-t * 90) * 0.35
    c = filt(noise(0.06), "highpass", 3000) * np.exp(-t * 300) * 0.25
    return s + c


def pop_sfx():
    t = tt(0.16)
    f = 520 + 1100 * np.minimum(1, t / 0.05)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 26) * 0.45


def tick_sfx():
    t = tt(0.03)
    return filt(noise(0.03), "bandpass", [1800, 7000]) * np.exp(-t * 220) * 0.22


def chime(f, dur=0.9):
    t = tt(dur)
    sig = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t)
           + 0.12 * np.sin(2 * np.pi * 3.01 * f * t))
    return sig * np.exp(-t * 5.5) * np.minimum(1, t / 0.003) * 0.22


def send_sfx():
    t = tt(0.3)
    f = 400 + 1800 * (t / 0.3) ** 1.5
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 0.25
    return tone + whoosh(0.3, 800, 8000) * 0.5


def impact():
    t = tt(2.6)
    sub = np.sin(2 * np.pi * 48 * t) * np.exp(-t * 2.2) * 0.6
    crash = filt(noise(2.6), "highpass", 3500) * np.exp(-t * 2.4) * 0.22
    body = filt(noise(2.6), "lowpass", 900) * np.exp(-t * 7) * 0.35
    return sub + crash + body


# ---------------------------------------------------------------- arrangement
NOTE = {"A2": 110.0, "F2": 87.31, "C3": 130.81, "G2": 98.0}
PROG = [  # (bass root, pad chord, arp tones)
    (110.0, [220.0, 261.63, 329.63], [440.0, 523.25, 659.25, 880.0]),
    (87.31, [174.61, 220.0, 261.63], [349.23, 440.0, 523.25, 698.46]),
    (130.81, [261.63, 329.63, 392.0], [523.25, 659.25, 783.99, 1046.5]),
    (98.0, [196.0, 246.94, 293.66], [392.0, 493.88, 587.33, 783.99]),
]


def chord_at(t):
    return PROG[int(max(0.0, t - OFF) // 2.0) % 4]


def build():
    music = np.zeros((N, 2))
    drums = np.zeros((N, 2))
    sfx = np.zeros((N, 2))

    # Pad: dark/filtered in hook, open in body, sustained in end card
    bar_t = OFF
    while bar_t < S_END:
        _, chord, _ = chord_at(bar_t + 0.01)
        cutoff = 700 if bar_t < S_FEED - 0.5 else 2400
        add(music, pad_chord(chord, 2.1, cutoff), bar_t, 1.0)
        bar_t += 2.0
    add(music, pad_chord([220.0, 261.63, 329.63, 440.0], DUR - S_END, 2000), S_END, 1.15)

    # Kicks on every beat until end card, side-chain envelope collected
    kick_times = [OFF + k * BEAT for k in range(40) if OFF + k * BEAT < S_END - 0.01]
    for kt in kick_times:
        add(drums, kick(), kt, 0.95)

    # Body groove
    k = 0
    while True:
        bt = OFF + k * BEAT
        if bt >= S_END - 0.01:
            break
        if bt >= S_FEED - 0.01:
            if k % 2 == 1:
                add(drums, clap(), bt, 0.8)
            add(drums, hat(), bt + 0.25, 0.7, 0.25)
            if bt >= S_COMPOSE - 0.01:
                add(drums, hat(), bt + 0.125, 0.3, -0.3)
                add(drums, hat(), bt + 0.375, 0.3, -0.3)
            root, _, arp = chord_at(bt + 0.01)
            for e in range(2):  # 8th-note bass
                add(music, bass_note(root * (1 if e == 0 else 2), 0.24), bt + e * 0.25, 0.9)
            if bt >= S_COMPOSE - 0.01:  # 16th-note pluck arp
                for s in range(4):
                    add(music, pluck(arp[(k * 4 + s) % 4]), bt + s * 0.125, 0.55,
                        -0.5 if s % 2 == 0 else 0.5)
        k += 1

    # Hook accents: word slams + riser into the drop
    for wt in (0.05, 0.55, 1.05, 1.55):
        add(sfx, tick_sfx() * 2.5, wt, 0.8)
    add(drums, clap(), 2.05, 0.9)
    add(drums, hat(True), 2.05, 0.8)
    add(sfx, riser(S_FEED - 2.05), 2.05, 0.9)
    add(drums, hat(True), S_FEED, 0.7)

    # Transition whooshes
    add(sfx, whoosh(0.45), S_FEED - 0.08, 0.9)
    add(sfx, whoosh(0.4, 500, 6000), S_COMPOSE - 0.05, 0.8)
    add(sfx, whoosh(0.4, 200, 3000), S_REACT - 0.05, 0.7)

    # Feed: like tap + FAB tap
    add(sfx, tap_sfx(), S_FEED + 1.95, 1.0)
    add(sfx, pop_sfx(), S_FEED + 1.98, 1.0)
    add(sfx, tap_sfx(), S_FEED + 3.85, 1.0)

    # Compose: typing + send
    typed = "Hello, X. What's everyone talking about?"
    t0, t1 = 0.45, 1.75
    dt = (t1 - t0) / len(typed)
    for i in range(len(typed)):
        add(sfx, tick_sfx(), S_COMPOSE + t0 + i * dt, 0.5 + 0.3 * rng.random(), rng.uniform(-0.3, 0.3))
    add(sfx, tap_sfx(), S_COMPOSE + 2.1, 1.0)
    add(sfx, send_sfx(), S_COMPOSE + 2.12, 0.9)

    # Reaction: notification chimes
    for dt_, f in ((0.35, 659.25), (0.65, 783.99), (0.95, 880.0)):
        add(sfx, chime(f), S_REACT + dt_, 1.0)
        add(sfx, chime(f * 2), S_REACT + dt_ + 0.06, 0.35)

    # End card: impact + logo sting + CTA tap
    add(drums, kick(big=True), S_END, 1.0)
    add(sfx, impact(), S_END, 1.0)
    for dt_, f in ((0.0, 440.0), (0.18, 659.25), (0.36, 880.0)):
        add(music, pluck(f, 0.8), S_END + dt_, 0.9)
    add(sfx, tap_sfx(), S_END + 1.7, 1.0)
    add(sfx, chime(880.0, 1.2), S_END + 1.72, 1.0)
    add(sfx, chime(1318.5, 1.2), S_END + 1.78, 0.6)

    # Side-chain ducking of music by kicks
    t = np.arange(N) / SR
    duck = np.ones(N)
    for kt in kick_times:
        m = t >= kt
        duck[m] = np.minimum(duck[m], 1 - 0.55 * np.exp(-(t[m] - kt) * 9))
    music *= duck[:, None]

    mix = music * 0.9 + drums * 0.8 + sfx * 0.9
    mix = np.tanh(mix * 1.3) / np.tanh(1.3)
    mix /= np.max(np.abs(mix)) + 1e-9
    mix *= 0.89  # ~ -1 dBFS
    fade = np.ones(N)
    fade[:441] = np.linspace(0, 1, 441)
    fo = int(0.5 * SR)
    fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
    return mix * fade[:, None]


def write_wav(path="x_ad_audio.wav"):
    mix = build()
    pcm = (mix * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return path


if __name__ == "__main__":
    print("Wrote", write_wav())
