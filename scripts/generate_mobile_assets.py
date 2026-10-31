"""
Generate the mobile app icon, splash screen, adaptive icon and favicon.

``apps/mobile/app.json`` has always referenced these files, but the assets
directory only ever contained ``.gitkeep`` — so ``expo start`` / ``eas build``
rendered the default Expo placeholder. This script draws the real brand assets
from the palette in ``app.json`` so they can be regenerated deterministically
instead of being opaque binaries nobody can reproduce.

Run: python scripts/generate_mobile_assets.py
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover - dependency guard
    print("Install Pillow first: pip install Pillow", file=sys.stderr)
    raise SystemExit(1)

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "apps" / "mobile" / "assets"

# Palette — mirrors app.json (primaryColor #7C3AED, splash background #09090B)
BRAND_LIGHT = (139, 92, 246)     # violet-500
BRAND = (124, 58, 237)           # violet-600
BRAND_DARK = (76, 29, 149)       # violet-900
BACKDROP = (9, 9, 11)            # #09090B
WHITE = (255, 255, 255)

FONT_CANDIDATES = [
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/segoeuib.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]


def _font(size: int) -> ImageFont.FreeTypeFont | None:
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                continue
    return None


def _gradient(size: int) -> Image.Image:
    """Smooth diagonal violet gradient from top-left to bottom-right."""
    try:
        import numpy as np
    except ImportError:  # pragma: no cover - numpy ships with most envs
        return Image.new("RGB", (size, size), BRAND)

    rows, cols = np.mgrid[0:size, 0:size]
    ratio = (rows + cols) / (2 * (size - 1))
    channels = [
        BRAND_LIGHT[i] + (BRAND_DARK[i] - BRAND_LIGHT[i]) * ratio for i in range(3)
    ]
    array = np.stack(channels, axis=-1)
    return Image.fromarray(array.astype("uint8"), mode="RGB")


def _draw_mark(canvas: Image.Image, box: tuple[int, int, int, int], colour) -> None:
    """Draw a rounded speech bubble with a smile inside ``box``."""
    draw = ImageDraw.Draw(canvas)
    left, top, right, bottom = box
    width = right - left
    height = bottom - top
    radius = int(width * 0.22)

    # Bubble body (the tail is carved out of the bottom edge so it reads as one shape)
    draw.rounded_rectangle(
        [left, top, right, int(bottom - height * 0.12)],
        radius=radius,
        fill=colour,
    )
    tail_w = int(width * 0.22)
    tail_x = left + int(width * 0.20)
    draw.polygon(
        [
            (tail_x, bottom - int(height * 0.18)),
            (tail_x + tail_w, bottom - int(height * 0.18)),
            (tail_x + int(tail_w * 0.25), bottom),
        ],
        fill=colour,
    )

    # Face — eyes and smile in the brand colour, punched through the bubble.
    eye_r = int(width * 0.055)
    eye_y = top + int(height * 0.34)
    for cx in (left + int(width * 0.34), left + int(width * 0.66)):
        draw.ellipse([cx - eye_r, eye_y - eye_r, cx + eye_r, eye_y + eye_r], fill=BRAND_DARK)

    smile_box = (
        left + int(width * 0.28),
        top + int(height * 0.34),
        right - int(width * 0.28),
        bottom - int(height * 0.30),
    )
    draw.arc(smile_box, start=20, end=160, fill=BRAND_DARK, width=max(2, int(width * 0.05)))


def _icon(size: int, supersample: int = 2) -> Image.Image:
    big = _gradient(size * supersample)
    inset = int(size * supersample * 0.20)
    _draw_mark(
        big,
        (inset, inset, size * supersample - inset, size * supersample - inset),
        WHITE,
    )
    return big.resize((size, size), Image.LANCZOS)


def _adaptive_icon(size: int, supersample: int = 2) -> Image.Image:
    """Transparent foreground; content stays inside Android's 66% safe zone."""
    canvas = Image.new("RGBA", (size * supersample, size * supersample), (0, 0, 0, 0))
    inset = int(size * supersample * 0.26)
    _draw_mark(
        canvas,
        (inset, inset, size * supersample - inset, size * supersample - inset),
        WHITE + (255,),
    )
    return canvas.resize((size, size), Image.LANCZOS)


def _splash(width: int = 1284, height: int = 2778) -> Image.Image:
    canvas = Image.new("RGB", (width, height), BACKDROP)
    mark_size = int(width * 0.34)
    mark = _icon(mark_size, supersample=2).convert("RGBA")

    # Round the icon corners so it sits on the dark splash like a badge.
    mask = Image.new("L", (mark_size, mark_size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, mark_size - 1, mark_size - 1], radius=int(mark_size * 0.22), fill=255
    )

    canvas.paste(mark, ((width - mark_size) // 2, (height - mark_size) // 2 - 60), mask)

    font = _font(int(width * 0.10))
    if font is not None:
        draw = ImageDraw.Draw(canvas)
        text = "MemeGPT"
        text_w = draw.textlength(text, font=font)
        draw.text(
            ((width - text_w) / 2, (height + mark_size) / 2 - 20),
            text,
            font=font,
            fill=WHITE,
        )
    return canvas


def _favicon(size: int = 48) -> Image.Image:
    return _icon(size, supersample=8)


def _notification_icon(size: int = 96) -> Image.Image:
    """Android status-bar icon: white silhouette on transparency, no gradient."""
    supersample = 8
    canvas = Image.new("RGBA", (size * supersample, size * supersample), (0, 0, 0, 0))
    inset = int(size * supersample * 0.08)
    _draw_mark(
        canvas,
        (inset, inset, size * supersample - inset, size * supersample - inset),
        WHITE + (255,),
    )
    return canvas.resize((size, size), Image.LANCZOS)


def main() -> int:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    targets = {
        "icon.png": _icon(1024),
        "adaptive-icon.png": _adaptive_icon(1024),
        "splash.png": _splash(),
        "favicon.png": _favicon(48),
        "notification-icon.png": _notification_icon(96),
    }

    for name, image in targets.items():
        path = ASSETS_DIR / name
        image.save(path, format="PNG", optimize=True)
        size_kb = path.stat().st_size / 1024
        print(f"[OK] {path.relative_to(ROOT_DIR)}  {image.size[0]}x{image.size[1]}  {size_kb:.1f} KB")

    keep = ASSETS_DIR / ".gitkeep"
    if keep.exists():
        keep.unlink()
    return 0


if __name__ == "__main__":
    sys.exit(main())
