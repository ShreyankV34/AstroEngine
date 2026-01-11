"""
Smartphone camera database for astrophotography.

Comprehensive specifications for popular smartphones with capable camera systems.
Focus on flagship models with large sensors, wide apertures, and good low-light performance.

Features:
- Main wide camera specs (primary sensor for astro)
- Computational photography capabilities
- Night mode / astrophotography mode support
- RAW capture capabilities
- Manual exposure controls

Note:
    Smartphones use computational photography (multi-frame stacking, AI processing)
    which can produce results exceeding raw sensor capabilities. Specs here are
    for the physical sensor; actual performance may be better in practice.
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class NightModeCapability(Enum):
    """Night mode capabilities."""
    NONE = "none"
    BASIC = "basic"  # Simple multi-frame stacking
    ADVANCED = "advanced"  # Dedicated night mode
    ASTRO = "astrophotography"  # Dedicated star/astro mode


@dataclass
class SmartphoneCamera:
    """Smartphone camera specifications."""

    # Device Info
    brand: str
    model: str
    year: int

    # Main Camera Sensor (wide)
    sensor_size_mm: tuple  # (width, height) in mm
    megapixels: float
    pixel_pitch_um: float
    aperture_fstop: float
    focal_length_mm: float  # 35mm equivalent often 24-28mm
    focal_length_equiv_35mm: int  # What it would be on full frame

    # Performance
    iso_range: tuple  # (min, max)
    max_exposure_time_sec: float  # In manual/pro mode
    read_noise_electrons: float  # Estimated

    # Features
    raw_capture: bool
    manual_controls: bool
    night_mode: NightModeCapability
    astrophoto_mode: bool  # Dedicated star mode

    # Computational
    multi_frame_stacking: bool
    ai_processing: bool

    # Recommendations
    astro_rating: float  # 1-10 scale
    best_for: List[str]  # Use cases
    notes: str


# ============================================================================
# Apple iPhone
# ============================================================================

IPHONE_15_PRO_MAX = SmartphoneCamera(
    brand="Apple",
    model="iPhone 15 Pro Max",
    year=2023,
    sensor_size_mm=(9.8, 7.3),  # 1/1.28" sensor
    megapixels=48.0,
    pixel_pitch_um=1.22,
    aperture_fstop=1.78,
    focal_length_mm=6.86,
    focal_length_equiv_35mm=24,
    iso_range=(25, 6400),
    max_exposure_time_sec=30.0,
    read_noise_electrons=2.5,
    raw_capture=True,
    manual_controls=True,  # Via third-party apps
    night_mode=NightModeCapability.ADVANCED,
    astrophoto_mode=False,  # No dedicated mode, but night mode works
    multi_frame_stacking=True,
    ai_processing=True,
    astro_rating=8.0,
    best_for=["Milky Way", "Wide-field star trails", "Meteor showers"],
    notes="Excellent night mode. Pixel binning to 12MP recommended for astro. Use ProRAW for maximum control."
)

IPHONE_14_PRO = SmartphoneCamera(
    brand="Apple",
    model="iPhone 14 Pro",
    year=2022,
    sensor_size_mm=(9.8, 7.3),
    megapixels=48.0,
    pixel_pitch_um=1.22,
    aperture_fstop=1.78,
    focal_length_mm=6.86,
    focal_length_equiv_35mm=24,
    iso_range=(25, 6400),
    max_exposure_time_sec=30.0,
    read_noise_electrons=2.8,
    raw_capture=True,
    manual_controls=True,
    night_mode=NightModeCapability.ADVANCED,
    astrophoto_mode=False,
    multi_frame_stacking=True,
    ai_processing=True,
    astro_rating=7.5,
    best_for=["Milky Way", "Bright constellations"],
    notes="Very similar to 15 Pro. ProRAW mode recommended."
)

# ============================================================================
# Samsung Galaxy
# ============================================================================

GALAXY_S24_ULTRA = SmartphoneCamera(
    brand="Samsung",
    model="Galaxy S24 Ultra",
    year=2024,
    sensor_size_mm=(11.1, 8.3),  # 1/1.3" sensor (larger than iPhone)
    megapixels=200.0,
    pixel_pitch_um=0.6,  # Tiny pixels, uses pixel binning
    aperture_fstop=1.7,
    focal_length_mm=6.4,
    focal_length_equiv_35mm=24,
    iso_range=(50, 3200),
    max_exposure_time_sec=30.0,
    read_noise_electrons=3.0,
    raw_capture=True,
    manual_controls=True,  # Excellent Pro mode
    night_mode=NightModeCapability.ADVANCED,
    astrophoto_mode=True,  # Hyperlapse mode can do stars
    multi_frame_stacking=True,
    ai_processing=True,
    astro_rating=8.5,
    best_for=["Milky Way", "Northern Lights", "Star trails"],
    notes="Best Android for astro. Use Expert RAW app. Pixel binning to 12MP or 50MP for low light."
)

GALAXY_S23_ULTRA = SmartphoneCamera(
    brand="Samsung",
    model="Galaxy S23 Ultra",
    year=2023,
    sensor_size_mm=(11.1, 8.3),
    megapixels=200.0,
    pixel_pitch_um=0.6,
    aperture_fstop=1.7,
    focal_length_mm=6.4,
    focal_length_equiv_35mm=24,
    iso_range=(50, 3200),
    max_exposure_time_sec=30.0,
    read_noise_electrons=3.2,
    raw_capture=True,
    manual_controls=True,
    night_mode=NightModeCapability.ADVANCED,
    astrophoto_mode=False,
    multi_frame_stacking=True,
    ai_processing=True,
    astro_rating=8.0,
    best_for=["Milky Way", "Constellations"],
    notes="Excellent sensor. Expert RAW recommended for full control."
)

# ============================================================================
# Google Pixel
# ============================================================================

PIXEL_8_PRO = SmartphoneCamera(
    brand="Google",
    model="Pixel 8 Pro",
    year=2023,
    sensor_size_mm=(10.5, 7.9),  # 1/1.31" sensor
    megapixels=50.0,
    pixel_pitch_um=1.2,
    aperture_fstop=1.68,
    focal_length_mm=6.9,
    focal_length_equiv_35mm=24,
    iso_range=(55, 6400),
    max_exposure_time_sec=256.0,  # Exceptional! Astrophotography mode
    read_noise_electrons=2.2,  # Excellent
    raw_capture=True,
    manual_controls=True,
    night_mode=NightModeCapability.ASTRO,  # Dedicated astrophotography mode!
    astrophoto_mode=True,  # Best-in-class astro mode
    multi_frame_stacking=True,
    ai_processing=True,
    astro_rating=9.5,  # Highest rated!
    best_for=["Milky Way", "Star fields", "Night sky timelapses", "Deep sky (yes, really!)"],
    notes="BEST smartphone for astrophotography. Dedicated 4-minute astro mode. Incredible computational photography."
)

PIXEL_7_PRO = SmartphoneCamera(
    brand="Google",
    model="Pixel 7 Pro",
    year=2022,
    sensor_size_mm=(10.5, 7.9),
    megapixels=50.0,
    pixel_pitch_um=1.2,
    aperture_fstop=1.85,
    focal_length_mm=6.81,
    focal_length_equiv_35mm=24,
    iso_range=(55, 6400),
    max_exposure_time_sec=256.0,
    read_noise_electrons=2.5,
    raw_capture=True,
    manual_controls=True,
    night_mode=NightModeCapability.ASTRO,
    astrophoto_mode=True,
    multi_frame_stacking=True,
    ai_processing=True,
    astro_rating=9.0,
    best_for=["Milky Way", "Astrophotography mode magic"],
    notes="Pioneered smartphone astrophotography mode. Still excellent."
)

# ============================================================================
# Database
# ============================================================================

SMARTPHONE_DATABASE = {
    # Apple
    "iPhone 15 Pro Max": IPHONE_15_PRO_MAX,
    "iPhone 14 Pro": IPHONE_14_PRO,

    # Samsung
    "Galaxy S24 Ultra": GALAXY_S24_ULTRA,
    "Galaxy S23 Ultra": GALAXY_S23_ULTRA,

    # Google
    "Pixel 8 Pro": PIXEL_8_PRO,
    "Pixel 7 Pro": PIXEL_7_PRO,
}


# ============================================================================
# Helper Functions
# ============================================================================

def get_smartphone(model: str) -> Optional[SmartphoneCamera]:
    """
    Retrieve smartphone camera specifications.

    Args:
        model: Model name (e.g., "Pixel 8 Pro")

    Returns:
        SmartphoneCamera object or None if not found

    Example:
        >>> phone = get_smartphone("Pixel 8 Pro")
        >>> phone.astro_rating
        9.5
    """
    return SMARTPHONE_DATABASE.get(model)


def list_smartphones() -> List[str]:
    """
    List all available smartphone models.

    Returns:
        List of model names

    Example:
        >>> phones = list_smartphones()
        >>> "Pixel 8 Pro" in phones
        True
    """
    return list(SMARTPHONE_DATABASE.keys())


def get_top_astro_phones(min_rating: float = 8.0) -> List[SmartphoneCamera]:
    """
    Get smartphones suitable for astrophotography.

    Args:
        min_rating: Minimum astro rating (default: 8.0)

    Returns:
        List of SmartphoneCamera objects sorted by rating

    Example:
        >>> top_phones = get_top_astro_phones(min_rating=9.0)
        >>> top_phones[0].model  # Should be Pixel 8 Pro
        'Pixel 8 Pro'
    """
    phones = [
        phone for phone in SMARTPHONE_DATABASE.values()
        if phone.astro_rating >= min_rating
    ]

    # Sort by rating (descending)
    phones.sort(key=lambda p: p.astro_rating, reverse=True)

    return phones


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Smartphone Astrophotography Database")
    print("=" * 60)

    # List all phones
    print(f"\nAvailable smartphones: {len(SMARTPHONE_DATABASE)}")
    for model in list_smartphones():
        phone = get_smartphone(model)
        print(f"  - {phone.brand} {phone.model} (Rating: {phone.astro_rating}/10)")

    # Top astro phones
    print("\n" + "=" * 60)
    print("Top Astrophotography Smartphones (Rating ≥ 8.5)")
    print("=" * 60)

    for phone in get_top_astro_phones(min_rating=8.5):
        print(f"\n{phone.brand} {phone.model} ({phone.year})")
        print(f"  Astro Rating: {phone.astro_rating}/10")
        print(f"  Sensor: {phone.megapixels}MP, {phone.pixel_pitch_um}μm pixels")
        print(f"  Aperture: f/{phone.aperture_fstop}")
        print(f"  Max Exposure: {phone.max_exposure_time_sec}s")
        print(f"  Night Mode: {phone.night_mode.value}")
        print(f"  Best For: {', '.join(phone.best_for)}")
        print(f"  Notes: {phone.notes}")

    print("\n" + "=" * 60)
