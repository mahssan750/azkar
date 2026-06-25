"""The app icon, drawn at runtime (no image file required).

A green rounded tile with a white crescent and a small star. Rendering at
runtime keeps the repo asset-free; ``scripts/make_icon.py`` reuses
``render_pixmap`` to also emit a real ``.ico`` for the packaged executable.
"""
from __future__ import annotations

import math
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QPainter,
    QPainterPath,
    QPixmap,
)

GREEN = QColor("#1f7a5a")
CREAM = QColor("#f7f4e9")


def _star_path(cx: float, cy: float, r_outer: float, r_inner: float, points: int = 5) -> QPainterPath:
    path = QPainterPath()
    for i in range(points * 2):
        r = r_outer if i % 2 == 0 else r_inner
        ang = -math.pi / 2 + i * math.pi / points
        pt = QPointF(cx + r * math.cos(ang), cy + r * math.sin(ang))
        if i == 0:
            path.moveTo(pt)
        else:
            path.lineTo(pt)
    path.closeSubpath()
    return path


def render_pixmap(size: int = 256) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)

    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.setPen(Qt.PenStyle.NoPen)

    # rounded green tile
    p.setBrush(QBrush(GREEN))
    radius = size * 0.22
    p.drawRoundedRect(QRectF(0, 0, size, size), radius, radius)

    # crescent = big circle minus an offset circle
    cx, cy, r = size * 0.50, size * 0.52, size * 0.30
    outer = QPainterPath()
    outer.addEllipse(QPointF(cx, cy), r, r)
    inner = QPainterPath()
    ir = r * 0.86
    inner.addEllipse(QPointF(cx + r * 0.46, cy - r * 0.05), ir, ir)
    p.setBrush(QBrush(CREAM))
    p.drawPath(outer.subtracted(inner))

    # small star tucked in the crescent's opening
    p.drawPath(_star_path(size * 0.70, size * 0.40, size * 0.10, size * 0.045))

    p.end()
    return pm


def make_icon() -> QIcon:
    icon = QIcon()
    for s in (16, 24, 32, 48, 64, 128, 256):
        icon.addPixmap(render_pixmap(s))
    return icon


def save_png(path: Path, size: int = 256) -> bool:
    """Render the icon to a PNG file (used as the toast logo). Best-effort."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        return bool(render_pixmap(size).save(str(path), "PNG"))
    except Exception:
        return False
