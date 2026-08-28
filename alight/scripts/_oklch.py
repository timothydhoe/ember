"""
alight._oklch
~~~~~~~~~~~~~~
sRGB <-> OKLab <-> OKLCH conversions, using Bjorn Ottosson's published
matrices (https://bottosson.github.io/posts/oklab/)
"""

from __future__ import annotations

import math

# -- sRGB <-> linear RGB (same gamma curve as WCAG's own relative
# luminance -- see export_nvim.py's relative_luminance()) -----------


def srgb_to_linear(c: float) -> float:
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c: float) -> int:
    c = max(0.0, min(1.0, c))
    v = 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
    return round(v * 255)


# -- linear RGB <-> OKLab, Ottosson's matrices -----------------------

_RGB_TO_LMS = (
    (0.4122214708, 0.5363325363, 0.0514459929),
    (0.2119034982, 0.6806995451, 0.1073969566),
    (0.0883024619, 0.2817188376, 0.6299787005),
)
_LMS_TO_OKLAB = (
    (0.2104542553, 0.7936177850, -0.0040720468),
    (1.9779984951, -2.4285922050, 0.4505937099),
    (0.0259040371, 0.7827717662, -0.8086757660),
)
_OKLAB_TO_LMS = (
    (1.0, 0.3963377774, 0.2158037573),
    (1.0, -0.1055613458, -0.0638541728),
    (1.0, -0.0894841775, -1.2914855480),
)
_LMS_TO_RGB = (
    (4.0767416621, -3.3077115913, 0.2309699292),
    (-1.2684380046, 2.6097574011, -0.3413193965),
    (-0.0041960863, -0.7034186147, 1.7076147010),
)


def _matmul(m: tuple, v: tuple) -> tuple:
    return tuple(sum(row[i] * v[i] for i in range(3)) for row in m)


def hex_to_oklab(hex_color: str) -> tuple[float, float, float]:
    hex_color = hex_color.lstrip("#")
    r, g, b = (srgb_to_linear(int(hex_color[i : i + 2], 16)) for i in (0, 2, 4))
    l, m, s = _matmul(_RGB_TO_LMS, (r, g, b))
    l_, m_, s_ = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return _matmul(_LMS_TO_OKLAB, (l_, m_, s_))


def oklab_to_hex(lab: tuple[float, float, float]) -> str:
    l_, m_, s_ = _matmul(_OKLAB_TO_LMS, lab)
    l, m, s = (x**3 for x in (l_, m_, s_))
    r, g, b = _matmul(_LMS_TO_RGB, (l, m, s))
    return "#" + "".join(f"{linear_to_srgb(c):02X}" for c in (r, g, b))


def oklab_to_oklch(lab: tuple[float, float, float]) -> tuple[float, float, float]:
    L, a, b = lab
    c = math.hypot(a, b)
    h = math.degrees(math.atan2(b, a)) % 360
    return L, c, h


def oklch_to_oklab(lch: tuple[float, float, float]) -> tuple[float, float, float]:
    L, c, h = lch
    rad = math.radians(h)
    return L, c * math.cos(rad), c * math.sin(rad)


def hex_to_oklch(hex_color: str) -> tuple[float, float, float]:
    return oklab_to_oklch(hex_to_oklab(hex_color))


def oklch_to_hex(lch: tuple[float, float, float]) -> str:
    return oklab_to_hex(oklch_to_oklab(lch))


if __name__ == "__main__":
    import sys
    from pathlib import Path

    import yaml

    scheme_file = Path(__file__).parent.parent / "schemes" / "alight.yml"
    data = yaml.safe_load(scheme_file.read_text())

    print("Round-trip check: hex -> OKLCH -> hex, every named color")
    worst_delta = 0
    for name, hexv in data["named"].items():
        lch = hex_to_oklch(hexv)
        back = oklch_to_hex(lch)
        r1, g1, b1 = (int(hexv.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
        r2, g2, b2 = (int(back.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
        delta = max(abs(r1 - r2), abs(g1 - g2), abs(b1 - b2))
        worst_delta = max(worst_delta, delta)
        status = "OK" if delta <= 1 else f"DRIFT of {delta}"
        print(
            f"  {name:12s} {hexv} -> L={lch[0]:.3f} C={lch[1]:.3f} h={lch[2]:6.1f} -> {back}  [{status}]"
        )
    print(
        f"\nworst round-trip drift across all named colors: {worst_delta} (out of 255)"
    )

    print("\nThe HSL problem this replaces:")
    for label, hexv in [("pure yellow", "#CCCC00"), ("pure blue", "#0000CC")]:
        L, c, h = hex_to_oklch(hexv)
        print(f"  {label:12s} {hexv}  OKLCH lightness={L:.3f}  (both were HSL L=0.40)")

    raise SystemExit(0 if worst_delta <= 1 else 1)
