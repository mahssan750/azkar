"""Generate assets/sounds/knock.wav — a short synthesized "knock-knock".

License-free (synthesized), no dependencies. Run with the project's venv:
    python scripts/make_sound.py
"""
from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path

SR = 44100
ROOT = Path(__file__).resolve().parents[1]


def _knock(dur: float = 0.085) -> list[float]:
    """One knock: a low wooden thud with a sharp transient tap."""
    n = int(SR * dur)
    out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-t / 0.022)                       # fast wooden decay
        body = 0.6 * math.sin(2 * math.pi * 170 * t) + 0.4 * math.sin(2 * math.pi * 95 * t)
        tap = (random.random() * 2 - 1) * 0.5 * math.exp(-t / 0.005)  # initial click
        out.append((body + tap) * env)
    return out


def _silence(dur: float) -> list[float]:
    return [0.0] * int(SR * dur)


def build_wav(path: Path) -> None:
    random.seed(7)
    samples = _knock() + _silence(0.14) + _knock()
    peak = max(1e-9, max(abs(x) for x in samples))
    samples = [x / peak * 0.9 for x in samples]
    frames = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, x)) * 32767)) for x in samples)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(frames)


def main() -> None:
    out = ROOT / "assets" / "sounds" / "knock.wav"
    build_wav(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
