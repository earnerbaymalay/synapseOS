#!/usr/bin/env python3
"""SynapseOS startup chime synthesiser (deterministic, no samples).

Three layers, ~2.8 s, 48 kHz stereo 16-bit:
  swell    — sub (D2) and fifth rising under the reveal
  strike   — inharmonic metallic bell on D5 / A5 / F#6, timed to the wordmark lock-in
  shimmer  — detuned high partials spread across the stereo field
A small multi-tap feedback delay adds space; peak is normalised to -4 dBFS.

Usage: render_chime.py OUT.wav
"""

import sys
import wave

import numpy as np

SR = 48000
DUR = 2.8
STRIKE = 0.42  # seconds into the chime


def env(t, attack, decay, start=0.0):
    x = t - start
    a = np.clip(x / attack, 0, 1) ** 2
    return np.where(x < 0, 0.0, a * np.exp(-np.clip(x - attack, 0, None) / decay))


def bell(t, f0, amp, start):
    # Struck-metal partial ratios with independent decays (higher dies faster).
    out = np.zeros_like(t)
    for ratio, a, dec in ((1.0, 1.0, 1.10), (2.0, 0.45, 0.70), (2.76, 0.30, 0.45),
                          (4.07, 0.16, 0.28), (5.40, 0.09, 0.18)):
        out += a * np.sin(2 * np.pi * f0 * ratio * (t - start)) * env(t, 0.004, dec, start)
    return out * amp


def main(path):
    t = np.arange(int(SR * DUR)) / SR
    rng = np.random.default_rng(7)

    swell = (np.sin(2 * np.pi * 73.42 * t) * 0.55 + np.sin(2 * np.pi * 110.0 * t) * 0.25)
    swell *= np.clip(t / 0.45, 0, 1) ** 1.5 * np.exp(-np.clip(t - 0.45, 0, None) / 0.9)

    strike = bell(t, 587.33, 0.55, STRIKE) + bell(t, 880.0, 0.35, STRIKE + 0.012) \
        + bell(t, 1479.98, 0.22, STRIKE + 0.024)

    left = np.zeros_like(t)
    right = np.zeros_like(t)
    for f in (2349.3, 2960.0, 3520.0, 4434.9):
        for side, det in ((left, 1.0 - 0.0025), (right, 1.0 + 0.0025)):
            ph = rng.uniform(0, 2 * np.pi)
            trem = 0.6 + 0.4 * np.sin(2 * np.pi * rng.uniform(3, 6) * t + ph)
            side += 0.05 * np.sin(2 * np.pi * f * det * t + ph) * trem * env(t, 0.25, 0.8, STRIKE + 0.05)

    left = swell + strike * 0.95 + left
    right = swell + strike * 1.0 + right

    # Multi-tap feedback delay ("space"), slightly different per channel.
    def space(x, taps):
        y = x.copy()
        for d, g in taps:
            n = int(d * SR)
            for k in range(1, 5):
                if n * k < len(x):
                    y[n * k:] += x[:-n * k] * g ** k
        return y

    left = space(left, ((0.083, 0.32), (0.127, 0.22)))
    right = space(right, ((0.097, 0.32), (0.141, 0.22)))

    st = np.stack([left, right], 1)
    st *= np.clip((DUR - t) / 0.6, 0, 1)[:, None]          # tail fade
    st *= 10 ** (-4 / 20) / np.abs(st).max()

    pcm = (st * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
