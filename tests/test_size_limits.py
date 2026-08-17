"""gpt-image-2 output-size constraints, verified against OpenAI's docs 2026-08-17.

Regression guard for a real defect: the shipped limits claimed total pixels
262,144-5,529,600, which both contradicted the official 655,360-8,294,400 and
the same file's own "max 3840x2160" note (4K is 8,294,400 px).
"""
import pytest

from renderers import GPT_IMAGE_2_LIMITS as L
from renderers import validate_gpt_image_2_size as check


@pytest.mark.parametrize("w,h", [
    (1024, 1024),    # square preset
    (1536, 1024),    # landscape preset
    (1024, 1536),    # portrait preset
    (2560, 1440),    # 2K, the documented reliability boundary
    (3824, 2144),    # 4K rounded to keep the edge under 3840
])
def test_documented_sizes_are_valid(w, h):
    assert check(w, h) == [], f"{w}x{h} should be legal"


def test_official_pixel_bounds():
    assert L["min_pixels"] == 655_360
    assert L["max_pixels"] == 8_294_400


def test_4k_is_within_the_pixel_ceiling():
    """The old 5,529,600 cap wrongly excluded 4K."""
    assert 3840 * 2160 <= L["max_pixels"]


def test_edges_must_be_multiples_of_16():
    assert any("multiple" in p for p in check(1000, 1024))


def test_edge_must_be_under_3840():
    assert any("under 3840" in p for p in check(3840, 2160))


def test_below_minimum_pixels_rejected():
    """512x512 = 262,144 px -- allowed by the old wrong minimum, actually too small."""
    assert any("below minimum" in p for p in check(512, 512))


def test_ratio_beyond_3to1_rejected():
    assert any("aspect ratio" in p for p in check(3072, 512))


def test_valid_size_reports_no_problems():
    assert check(1536, 1024) == []
