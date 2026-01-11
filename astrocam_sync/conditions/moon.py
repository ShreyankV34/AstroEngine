"""
Moon phase calculations and sky brightness impact for astrophotography.

The Moon is the single largest factor affecting deep-sky astrophotography conditions.
This module provides:
- Accurate moon phase and illumination calculations
- Sky brightness degradation from moonlight
- Angular separation between moon and targets
- Moonrise/moonset predictions
- Astrophotography viability assessment

References:
    Meeus, J. (1998). Astronomical Algorithms, Chapter 48.
    Krisciunas, K. & Schaefer, B. E. (1991). "A model of the brightness of moonlight".
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional
import math
from enum import Enum


class MoonPhase(Enum):
    """Moon phase names."""
    NEW = "new"
    WAXING_CRESCENT = "waxing_crescent"
    FIRST_QUARTER = "first_quarter"
    WAXING_GIBBOUS = "waxing_gibbous"
    FULL = "full"
    WANING_GIBBOUS = "waning_gibbous"
    LAST_QUARTER = "last_quarter"
    WANING_CRESCENT = "waning_crescent"


@dataclass
class MoonConditions:
    """Complete moon conditions for astrophotography assessment."""

    # Phase
    phase_angle_deg: float  # 0° = new, 180° = full
    illumination_percent: float  # 0-100%
    phase_name: MoonPhase

    # Position
    altitude_deg: float  # Above horizon (negative = below)
    azimuth_deg: float
    distance_km: float  # Earth-Moon distance

    # Impact
    sky_brightness_contribution: float  # Magnitude degradation
    is_visible: bool  # Above horizon
    astrophotography_quality: str  # excellent/good/poor/unusable

    # Timing
    moonrise_utc: Optional[datetime]
    moonset_utc: Optional[datetime]
    next_new_moon: datetime


def phase_angle_to_name(phase_angle_deg: float) -> MoonPhase:
    """
    Convert phase angle to descriptive name.

    Args:
        phase_angle_deg: Phase angle in degrees (0-360)

    Returns:
        MoonPhase enum

    Example:
        >>> phase_angle_to_name(0)
        <MoonPhase.NEW: 'new'>
        >>> phase_angle_to_name(180)
        <MoonPhase.FULL: 'full'>
    """
    # Normalize to [0, 360)
    angle = phase_angle_deg % 360.0

    if angle < 22.5 or angle >= 337.5:
        return MoonPhase.NEW
    elif 22.5 <= angle < 67.5:
        return MoonPhase.WAXING_CRESCENT
    elif 67.5 <= angle < 112.5:
        return MoonPhase.FIRST_QUARTER
    elif 112.5 <= angle < 157.5:
        return MoonPhase.WAXING_GIBBOUS
    elif 157.5 <= angle < 202.5:
        return MoonPhase.FULL
    elif 202.5 <= angle < 247.5:
        return MoonPhase.WANING_GIBBOUS
    elif 247.5 <= angle < 292.5:
        return MoonPhase.LAST_QUARTER
    else:  # 292.5 <= angle < 337.5
        return MoonPhase.WANING_CRESCENT


def calculate_moon_sky_brightness(
    moon_illumination_percent: float,
    moon_altitude_deg: float,
    moon_target_separation_deg: float,
    base_sky_brightness: float = 21.5
) -> float:
    """
    Calculate sky brightness degradation due to moonlight.

    Uses the Krisciunas-Schaefer model for lunar sky brightness.

    Args:
        moon_illumination_percent: Moon illumination (0-100%)
        moon_altitude_deg: Moon altitude above horizon
        moon_target_separation_deg: Angular distance from moon to target
        base_sky_brightness: Natural sky brightness (mag/arcsec²) without moon

    Returns:
        Degraded sky brightness in mag/arcsec²

    Reference:
        Krisciunas & Schaefer (1991), PASP 103, 1033

    Note:
        Lower magnitude = brighter sky = worse for astrophotography

    Example:
        >>> # Full moon 30° up, 90° from target
        >>> brightness = calculate_moon_sky_brightness(100.0, 30.0, 90.0)
        >>> brightness < 21.5  # Sky is brighter (worse)
        True
    """
    # Moon below horizon - no impact
    if moon_altitude_deg < 0:
        return base_sky_brightness

    # No moon - no impact
    if moon_illumination_percent < 1:
        return base_sky_brightness

    # Convert to fractions
    k = moon_illumination_percent / 100.0  # Illumination fraction
    alpha_moon = moon_altitude_deg  # Moon altitude
    rho = moon_target_separation_deg  # Angular separation

    # Krisciunas-Schaefer model
    # More complex form involves airmass, extinction, but simplified here

    # Moon contribution to sky brightness
    # f(rho) = 10^5.36 * (1.06 + cos²(rho)) + 10^(6.15 - rho/40)
    rho_rad = math.radians(rho)
    f_rho = 10**5.36 * (1.06 + math.cos(rho_rad)**2)

    if rho < 10:
        # Very close to moon - use different formula
        f_rho += 10**(6.15 - rho / 40.0)

    # Zenith angle factor (simplified)
    X = 1.0 / math.cos(math.radians(90 - alpha_moon)) if alpha_moon > 0 else 10.0
    X = min(X, 10.0)  # Cap at airmass 10

    # Moon brightness contribution (simplified)
    # Full Krisciunas-Schaefer includes atmospheric extinction
    I_moon = -12.7 + 0.026 * abs(rho) + 4e-9 * (rho**4)

    # Add moon illumination dependence
    moon_mag_contribution = I_moon - 2.5 * math.log10(k * f_rho * (1 - 10**(-0.4 * X)))

    # Combine with base sky
    # Convert magnitudes to flux, add, convert back
    base_flux = 10**(-0.4 * base_sky_brightness)
    moon_flux = 10**(-0.4 * moon_mag_contribution)

    total_flux = base_flux + moon_flux
    degraded_brightness = -2.5 * math.log10(total_flux)

    return degraded_brightness


def assess_moon_impact(
    moon_illumination_percent: float,
    moon_altitude_deg: float,
    moon_target_separation_deg: float
) -> Tuple[str, str]:
    """
    Assess impact of moon on deep-sky astrophotography.

    Args:
        moon_illumination_percent: Moon illumination (0-100%)
        moon_altitude_deg: Moon altitude
        moon_target_separation_deg: Angular separation from target

    Returns:
        (quality_rating, detailed_assessment)

    Quality ratings:
        - "excellent": New moon or moon below horizon
        - "good": Thin crescent or moon far from target
        - "fair": Moderate moon with good separation
        - "poor": Bright moon, modest separation
        - "unusable": Full moon near target

    Example:
        >>> quality, msg = assess_moon_impact(100.0, 45.0, 30.0)
        >>> quality
        'unusable'
    """
    # Moon below horizon
    if moon_altitude_deg < 0:
        return "excellent", "🌑 Moon below horizon - perfect dark sky conditions"

    # New moon
    if moon_illumination_percent < 5:
        return "excellent", "🌑 New moon (< 5% illumination) - excellent conditions"

    # Thin crescent
    if moon_illumination_percent < 20:
        if moon_target_separation_deg > 60:
            return "good", f"🌒 Thin crescent ({moon_illumination_percent:.0f}% lit), well separated - good conditions"
        else:
            return "fair", f"🌒 Thin crescent ({moon_illumination_percent:.0f}% lit), but close to target"

    # Quarter moon
    if moon_illumination_percent < 60:
        if moon_target_separation_deg > 90:
            return "fair", f"🌓 Quarter moon ({moon_illumination_percent:.0f}% lit), opposite side of sky - acceptable"
        elif moon_target_separation_deg > 60:
            return "poor", f"🌓 Quarter moon ({moon_illumination_percent:.0f}% lit), moderate separation - challenging"
        else:
            return "poor", f"🌓 Quarter moon ({moon_illumination_percent:.0f}% lit), too close to target"

    # Gibbous/Full
    if moon_illumination_percent >= 60:
        if moon_target_separation_deg > 120:
            return "poor", f"🌕 Bright moon ({moon_illumination_percent:.0f}% lit), but far from target - difficult"
        elif moon_target_separation_deg > 90:
            return "unusable", f"🌕 Bright moon ({moon_illumination_percent:.0f}% lit), too close - not recommended"
        else:
            return "unusable", f"🌕 Bright moon ({moon_illumination_percent:.0f}% lit), very close - unusable for deep sky"

    return "poor", "Moon conditions unfavorable"


def calculate_next_new_moon(reference_date: datetime) -> datetime:
    """
    Calculate the date of the next new moon.

    Uses a simplified algorithm based on mean synodic month.

    Args:
        reference_date: Starting date

    Returns:
        Datetime of next new moon (approximate within ~1 day)

    Note:
        For precise calculations, use JPL ephemerides or skyfield library.
        This is a simplified algorithm sufficient for planning purposes.

    Example:
        >>> from datetime import datetime, timezone
        >>> dt = datetime(2025, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
        >>> next_new = calculate_next_new_moon(dt)
        >>> next_new > dt
        True
    """
    from ..core.time import utc_to_julian_date
    from ..core.astronomy import moon_phase as calc_moon_phase

    jd_start = utc_to_julian_date(reference_date)

    # Synodic month = 29.530589 days
    synodic_month = 29.530589

    # Search forward for new moon (phase angle near 0° or 360°)
    for days_ahead in range(0, 60):  # Search up to 2 months
        test_jd = jd_start + days_ahead
        phase_angle, _ = calc_moon_phase(test_jd)

        # New moon when phase angle is near 0° or 360°
        if phase_angle < 5.0 or phase_angle > 355.0:
            # Convert back to datetime
            from ..core.time import julian_date_to_utc
            return julian_date_to_utc(test_jd)

    # Fallback: approximate based on synodic month
    return reference_date + timedelta(days=synodic_month)


def calculate_best_imaging_window(
    reference_date: datetime,
    window_days: int = 14
) -> Tuple[datetime, datetime, str]:
    """
    Find the best astrophotography window around new moon.

    Args:
        reference_date: Starting date
        window_days: Number of days for dark window around new moon (default: 14)

    Returns:
        (window_start, window_end, description)

    Note:
        "Dark time" is typically defined as within ±7 days of new moon,
        when moon is < 50% illuminated.

    Example:
        >>> from datetime import datetime, timezone
        >>> dt = datetime(2025, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
        >>> start, end, desc = calculate_best_imaging_window(dt)
        >>> (end - start).days >= 14
        True
    """
    next_new = calculate_next_new_moon(reference_date)

    # Dark window: ±window_days/2 around new moon
    window_start = next_new - timedelta(days=window_days / 2)
    window_end = next_new + timedelta(days=window_days / 2)

    description = (
        f"Best imaging window from {window_start.strftime('%Y-%m-%d')} "
        f"to {window_end.strftime('%Y-%m-%d')} "
        f"(centered on new moon: {next_new.strftime('%Y-%m-%d')})"
    )

    return window_start, window_end, description


def exposure_time_adjustment_for_moon(
    moon_illumination_percent: float,
    moon_altitude_deg: float,
    moon_target_separation_deg: float
) -> float:
    """
    Calculate exposure time reduction factor due to moonlight.

    When the moon is up, you must shorten exposures to avoid overexposing
    the sky background.

    Args:
        moon_illumination_percent: Moon illumination
        moon_altitude_deg: Moon altitude
        moon_target_separation_deg: Separation from target

    Returns:
        Exposure reduction factor (e.g., 0.5 = use half the exposure time)

    Example:
        >>> # Full moon 30° up, 60° from target
        >>> factor = exposure_time_adjustment_for_moon(100.0, 30.0, 60.0)
        >>> factor < 1.0  # Must reduce exposure
        True
    """
    # Moon below horizon - no adjustment
    if moon_altitude_deg < 0:
        return 1.0

    # Calculate sky brightness degradation
    base_sky = 21.5  # Typical dark sky
    degraded_sky = calculate_moon_sky_brightness(
        moon_illumination_percent,
        moon_altitude_deg,
        moon_target_separation_deg,
        base_sky
    )

    # Sky brightness change in magnitudes
    sky_change_mag = base_sky - degraded_sky

    # Each magnitude is 2.512x flux change
    # Brighter sky = shorter exposures needed
    flux_ratio = 10**(0.4 * sky_change_mag)

    # Reduction factor (inverse of flux ratio)
    reduction_factor = 1.0 / max(1.0, flux_ratio)

    return max(0.1, min(1.0, reduction_factor))


# Example usage
if __name__ == "__main__":
    from ..core.time import utc_to_julian_date
    from ..core.astronomy import moon_phase as calc_moon_phase

    print("=" * 70)
    print("Moon Impact on Astrophotography")
    print("=" * 70)

    # Test different moon scenarios
    scenarios = [
        {"name": "New Moon", "illum": 0.0, "alt": -10.0, "sep": 90.0},
        {"name": "Thin Crescent", "illum": 15.0, "alt": 20.0, "sep": 90.0},
        {"name": "First Quarter", "illum": 50.0, "alt": 45.0, "sep": 90.0},
        {"name": "Full Moon - Far", "illum": 100.0, "alt": 30.0, "sep": 120.0},
        {"name": "Full Moon - Close", "illum": 100.0, "alt": 60.0, "sep": 30.0},
    ]

    for scenario in scenarios:
        print(f"\n{'-'*70}")
        print(f"Scenario: {scenario['name']}")
        print(f"  Illumination: {scenario['illum']:.0f}%")
        print(f"  Altitude: {scenario['alt']:.0f}°")
        print(f"  Target separation: {scenario['sep']:.0f}°")

        quality, msg = assess_moon_impact(
            scenario['illum'],
            scenario['alt'],
            scenario['sep']
        )

        sky_brightness = calculate_moon_sky_brightness(
            scenario['illum'],
            scenario['alt'],
            scenario['sep']
        )

        exp_factor = exposure_time_adjustment_for_moon(
            scenario['illum'],
            scenario['alt'],
            scenario['sep']
        )

        print(f"\n  Quality: {quality.upper()}")
        print(f"  Assessment: {msg}")
        print(f"  Sky brightness: {sky_brightness:.2f} mag/arcsec²")
        print(f"  Exposure adjustment: {exp_factor:.2f}x")

    # Next imaging window
    print(f"\n{'='*70}")
    print("Next Dark Sky Window")
    print(f"{'='*70}")

    ref_date = datetime(2025, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
    start, end, desc = calculate_best_imaging_window(ref_date)
    print(f"\n{desc}")
    print(f"  Duration: {(end - start).days} days")

    print(f"\n{'='*70}")
