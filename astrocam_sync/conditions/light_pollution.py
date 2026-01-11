"""
Light pollution assessment and Bortle scale implementation.

Provides sky quality metrics for astrophotography planning:
- Bortle Dark Sky Scale (1-9)
- Sky brightness in mag/arcsec²
- Naked-eye limiting magnitude (NELM)
- Visibility predictions for different target types
- Light pollution impact on exposures

References:
    Bortle, J. E. (2001). "Introducing the Bortle Dark-Sky Scale". Sky & Telescope.
    Cinzano, P., et al. (2001). "The first World Atlas of artificial night sky brightness".
"""

from dataclasses import dataclass
from enum import Enum
from typing import Tuple, List, Optional
import math


class BortleClass(Enum):
    """
    Bortle Dark Sky Scale classification.

    Scale from 1 (pristine dark sky) to 9 (inner-city sky).
    """
    CLASS_1 = 1  # Excellent dark-sky site
    CLASS_2 = 2  # Typical truly dark site
    CLASS_3 = 3  # Rural sky
    CLASS_4 = 4  # Rural/suburban transition
    CLASS_5 = 5  # Suburban sky
    CLASS_6 = 6  # Bright suburban sky
    CLASS_7 = 7  # Suburban/urban transition
    CLASS_8 = 8  # City sky
    CLASS_9 = 9  # Inner-city sky


@dataclass
class SkyQuality:
    """Sky quality metrics."""

    bortle_class: BortleClass
    sky_brightness_mag: float  # mag/arcsec² (SQM reading)
    nelm: float  # Naked-eye limiting magnitude
    milky_way_visible: bool
    airglow_visible: bool
    zodiacal_light_visible: bool
    m31_visible: bool  # Andromeda naked eye
    description: str
    best_targets: List[str]
    exposure_multiplier: float  # Compared to Bortle 1


# ============================================================================
# Bortle Scale Database
# ============================================================================

BORTLE_SCALE = {
    BortleClass.CLASS_1: SkyQuality(
        bortle_class=BortleClass.CLASS_1,
        sky_brightness_mag=22.0,  # Darkest possible
        nelm=7.6,  # Can see to magnitude 7.6+
        milky_way_visible=True,
        airglow_visible=True,
        zodiacal_light_visible=True,
        m31_visible=True,
        description="Excellent dark-sky site. Airglow visible. Milky Way casts shadows. "
                   "Zodiacal light striking. M33 easy. Scorpius/Sagittarius region casts obvious shadows.",
        best_targets=["Faint nebulae", "Galaxies", "IFN (integrated flux nebulae)", "Zodiacal light"],
        exposure_multiplier=1.0
    ),

    BortleClass.CLASS_2: SkyQuality(
        bortle_class=BortleClass.CLASS_2,
        sky_brightness_mag=21.7,
        nelm=7.1,
        milky_way_visible=True,
        airglow_visible=True,
        zodiacal_light_visible=True,
        m31_visible=True,
        description="Typical truly dark site. Milky Way highly structured. Zodiacal light obvious. "
                   "M33 easy with averted vision. Summer Milky Way rich with detail.",
        best_targets=["Milky Way core", "Faint galaxies", "Nebulae", "Star clusters"],
        exposure_multiplier=1.15
    ),

    BortleClass.CLASS_3: SkyQuality(
        bortle_class=BortleClass.CLASS_3,
        sky_brightness_mag=21.4,
        nelm=6.6,
        milky_way_visible=True,
        airglow_visible=False,
        zodiacal_light_visible=True,
        m31_visible=True,
        description="Rural sky. Some light pollution on horizon. Milky Way appears highly structured. "
                   "M15, M4, M5 distinct. Zodiacal light striking in spring/fall.",
        best_targets=["Milky Way", "Bright galaxies", "Emission nebulae", "Open clusters"],
        exposure_multiplier=1.35
    ),

    BortleClass.CLASS_4: SkyQuality(
        bortle_class=BortleClass.CLASS_4,
        sky_brightness_mag=20.8,
        nelm=6.1,
        milky_way_visible=True,
        airglow_visible=False,
        zodiacal_light_visible=True,
        m31_visible=True,
        description="Rural/suburban transition. Light pollution domes visible in several directions. "
                   "Milky Way impressive overhead but washed out near horizons. M33 difficult.",
        best_targets=["Milky Way (overhead)", "Bright nebulae", "Messier objects"],
        exposure_multiplier=1.6
    ),

    BortleClass.CLASS_5: SkyQuality(
        bortle_class=BortleClass.CLASS_5,
        sky_brightness_mag=20.3,
        nelm=5.6,
        milky_way_visible=True,  # Barely, overhead only
        airglow_visible=False,
        zodiacal_light_visible=False,
        m31_visible=True,  # Difficult
        description="Suburban sky. Light pollution domes visible in most directions. Milky Way washed out, "
                   "visible only overhead. M33 invisible. M31 difficult without optical aid.",
        best_targets=["Bright Messier objects", "Planets", "Moon", "Double stars"],
        exposure_multiplier=2.2
    ),

    BortleClass.CLASS_6: SkyQuality(
        bortle_class=BortleClass.CLASS_6,
        sky_brightness_mag=19.5,
        nelm=5.1,
        milky_way_visible=False,  # Not visible
        airglow_visible=False,
        zodiacal_light_visible=False,
        m31_visible=False,
        description="Bright suburban sky. Sky has grayish color. Milky Way invisible. "
                   "M31 difficult even with binoculars. Clouds brightly illuminated.",
        best_targets=["Bright planets", "Moon", "Brightest Messier objects (M13, M42)"],
        exposure_multiplier=3.5
    ),

    BortleClass.CLASS_7: SkyQuality(
        bortle_class=BortleClass.CLASS_7,
        sky_brightness_mag=18.9,
        nelm=4.6,
        milky_way_visible=False,
        airglow_visible=False,
        zodiacal_light_visible=False,
        m31_visible=False,
        description="Suburban/urban transition. Sky light gray. Light pollution severe in all directions. "
                   "Milky Way invisible. M44, Pleiades washed out. Clouds brilliantly lit.",
        best_targets=["Moon", "Bright planets", "M42 (barely)"],
        exposure_multiplier=6.0
    ),

    BortleClass.CLASS_8: SkyQuality(
        bortle_class=BortleClass.CLASS_8,
        sky_brightness_mag=18.4,
        nelm=4.1,
        milky_way_visible=False,
        airglow_visible=False,
        zodiacal_light_visible=False,
        m31_visible=False,
        description="City sky. Sky glows grayish-white. Only brightest Messier objects detectable with "
                   "moderate telescopes. Stars forming familiar constellations invisible or nearly so.",
        best_targets=["Moon", "Bright planets", "Double stars"],
        exposure_multiplier=12.0
    ),

    BortleClass.CLASS_9: SkyQuality(
        bortle_class=BortleClass.CLASS_9,
        sky_brightness_mag=17.5,  # Or worse
        nelm=3.5,  # Or worse
        milky_way_visible=False,
        airglow_visible=False,
        zodiacal_light_visible=False,
        m31_visible=False,
        description="Inner-city sky. Sky blazes with light pollution. Many stars forming constellations "
                   "invisible. Only brightest stars and planets visible. Deep-sky observing impossible.",
        best_targets=["Moon", "Bright planets only"],
        exposure_multiplier=25.0
    ),
}


# ============================================================================
# Helper Functions
# ============================================================================

def sqm_to_bortle(sky_brightness_mag: float) -> BortleClass:
    """
    Convert SQM reading (mag/arcsec²) to Bortle class.

    Args:
        sky_brightness_mag: Sky brightness in mag/arcsec² (SQM reading)

    Returns:
        BortleClass

    Example:
        >>> bortle = sqm_to_bortle(21.5)
        >>> bortle
        <BortleClass.CLASS_3: 3>
    """
    if sky_brightness_mag >= 21.9:
        return BortleClass.CLASS_1
    elif sky_brightness_mag >= 21.5:
        return BortleClass.CLASS_2
    elif sky_brightness_mag >= 21.0:
        return BortleClass.CLASS_3
    elif sky_brightness_mag >= 20.5:
        return BortleClass.CLASS_4
    elif sky_brightness_mag >= 20.0:
        return BortleClass.CLASS_5
    elif sky_brightness_mag >= 19.0:
        return BortleClass.CLASS_6
    elif sky_brightness_mag >= 18.5:
        return BortleClass.CLASS_7
    elif sky_brightness_mag >= 18.0:
        return BortleClass.CLASS_8
    else:
        return BortleClass.CLASS_9


def nelm_to_bortle(nelm: float) -> BortleClass:
    """
    Convert naked-eye limiting magnitude to Bortle class.

    Args:
        nelm: Naked-eye limiting magnitude

    Returns:
        BortleClass

    Example:
        >>> bortle = nelm_to_bortle(6.5)
        >>> bortle
        <BortleClass.CLASS_3: 3>
    """
    if nelm >= 7.4:
        return BortleClass.CLASS_1
    elif nelm >= 7.0:
        return BortleClass.CLASS_2
    elif nelm >= 6.5:
        return BortleClass.CLASS_3
    elif nelm >= 6.0:
        return BortleClass.CLASS_4
    elif nelm >= 5.5:
        return BortleClass.CLASS_5
    elif nelm >= 5.0:
        return BortleClass.CLASS_6
    elif nelm >= 4.5:
        return BortleClass.CLASS_7
    elif nelm >= 4.0:
        return BortleClass.CLASS_8
    else:
        return BortleClass.CLASS_9


def get_sky_quality(bortle_class: BortleClass) -> SkyQuality:
    """
    Get detailed sky quality metrics for a Bortle class.

    Args:
        bortle_class: Bortle classification

    Returns:
        SkyQuality object with all metrics

    Example:
        >>> sq = get_sky_quality(BortleClass.CLASS_4)
        >>> sq.milky_way_visible
        True
        >>> sq.exposure_multiplier
        1.6
    """
    return BORTLE_SCALE[bortle_class]


def calculate_exposure_adjustment(
    base_bortle: BortleClass,
    actual_bortle: BortleClass
) -> float:
    """
    Calculate exposure time adjustment for light pollution.

    Args:
        base_bortle: Reference Bortle class (typically CLASS_1 or CLASS_4)
        actual_bortle: Actual observing site Bortle class

    Returns:
        Multiplier for exposure time (e.g., 2.0 = double exposure needed)

    Example:
        >>> # Shooting from Bortle 5 instead of Bortle 3
        >>> multiplier = calculate_exposure_adjustment(BortleClass.CLASS_3, BortleClass.CLASS_5)
        >>> multiplier  # About 1.6x longer exposure needed
        1.63
    """
    base_sq = BORTLE_SCALE[base_bortle]
    actual_sq = BORTLE_SCALE[actual_bortle]

    return actual_sq.exposure_multiplier / base_sq.exposure_multiplier


def is_target_visible(
    bortle_class: BortleClass,
    target_surface_brightness: float,
    target_name: str = "target"
) -> Tuple[bool, str]:
    """
    Determine if a target is photographable under given sky conditions.

    Args:
        bortle_class: Sky quality class
        target_surface_brightness: Target brightness in mag/arcsec²
        target_name: Name of target for detailed message

    Returns:
        (is_visible, recommendation)

    Example:
        >>> visible, msg = is_target_visible(BortleClass.CLASS_4, 5.0, "Milky Way Core")
        >>> visible
        True
    """
    sq = BORTLE_SCALE[bortle_class]
    sky_brightness = sq.sky_brightness_mag

    # Contrast: target should be at least 1-2 mag brighter than sky
    contrast = sky_brightness - target_surface_brightness

    if contrast >= 3.0:
        return True, f"✓ Excellent - {target_name} will stand out strongly (contrast: {contrast:.1f} mag)"
    elif contrast >= 2.0:
        return True, f"✓ Good - {target_name} visible with good contrast (contrast: {contrast:.1f} mag)"
    elif contrast >= 1.0:
        return True, f"⚠️ Marginal - {target_name} visible but low contrast (contrast: {contrast:.1f} mag)"
    elif contrast >= 0.0:
        return False, f"❌ Poor - {target_name} barely above sky background (contrast: {contrast:.1f} mag)"
    else:
        return False, f"❌ Impossible - {target_name} dimmer than sky background (contrast: {contrast:.1f} mag)"


def recommend_targets_for_bortle(bortle_class: BortleClass) -> List[str]:
    """
    Get recommended astrophotography targets for a Bortle class.

    Args:
        bortle_class: Sky quality class

    Returns:
        List of recommended target types

    Example:
        >>> targets = recommend_targets_for_bortle(BortleClass.CLASS_4)
        >>> "Milky Way" in targets
        True
    """
    sq = BORTLE_SCALE[bortle_class]
    return sq.best_targets


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("Bortle Dark Sky Scale - Light Pollution Assessment")
    print("=" * 70)

    # Show all Bortle classes
    for bortle_class in BortleClass:
        sq = get_sky_quality(bortle_class)
        print(f"\n{'='*70}")
        print(f"Bortle Class {bortle_class.value}: {sq.sky_brightness_mag} mag/arcsec²")
        print(f"{'='*70}")
        print(f"NELM: {sq.nelm}")
        print(f"Milky Way visible: {sq.milky_way_visible}")
        print(f"Exposure multiplier: {sq.exposure_multiplier}x")
        print(f"\nDescription:")
        print(f"  {sq.description}")
        print(f"\nBest targets:")
        for target in sq.best_targets:
            print(f"  - {target}")

    # Example: Shooting Milky Way from different locations
    print("\n" + "=" * 70)
    print("Example: Milky Way Core Photography from Different Sites")
    print("=" * 70)

    milky_way_brightness = 5.0  # mag/arcsec² (typical)

    for bortle_class in [BortleClass.CLASS_1, BortleClass.CLASS_3,
                         BortleClass.CLASS_5, BortleClass.CLASS_7]:
        visible, msg = is_target_visible(bortle_class, milky_way_brightness, "Milky Way Core")
        sq = get_sky_quality(bortle_class)

        print(f"\nBortle {bortle_class.value} ({sq.sky_brightness_mag} mag/arcsec²):")
        print(f"  {msg}")
        if bortle_class != BortleClass.CLASS_1:
            exp_mult = calculate_exposure_adjustment(BortleClass.CLASS_1, bortle_class)
            print(f"  Need {exp_mult:.1f}x longer exposure than Bortle 1")

    print("\n" + "=" * 70)
