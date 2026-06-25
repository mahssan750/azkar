"""Generate assets/icons/azkar.ico from the runtime icon renderer.

Produces a multi-size PNG-based .ico (read by Windows Vista+). Run with the
project's venv:  python scripts/make_icon.py
"""
from __future__ import annotations

import os
import struct
import sys
from pathlib import Path

# Render off-screen so no window flashes.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QBuffer, QByteArray, QIODevice  # noqa: E402
from PySide6.QtGui import QGuiApplication  # noqa: E402


def _png_bytes(size: int) -> bytes:
    from azkar.ui.icon import render_pixmap

    ba = QByteArray()
    buf = QBuffer(ba)
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    render_pixmap(size).save(buf, "PNG")
    buf.close()
    return bytes(ba)


def build_ico(path: Path, sizes=(16, 24, 32, 48, 64, 128, 256)) -> None:
    images = [(s, _png_bytes(s)) for s in sizes]
    out = bytearray(struct.pack("<HHH", 0, 1, len(images)))  # ICONDIR
    offset = 6 + 16 * len(images)
    entries, data = bytearray(), bytearray()
    for size, png in images:
        dim = 0 if size >= 256 else size  # 0 means 256 in the ICO format
        entries += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(png), offset)
        data += png
        offset += len(png)
    out += entries + data
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(out)


def main() -> None:
    QGuiApplication(sys.argv)  # required before constructing QPixmap
    out = ROOT / "assets" / "icons" / "azkar.ico"
    build_ico(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
