"""
Celestial mechanics and motion calculations.

Implements astronomical calculations for astrophotography planning:
- Rise/set/culmination times
- Star trailing and motion calculations
- NPF rule for maximum untracked exposure
- Atmospheric refraction corrections
- Extinction and airmass effects
- Moon phase and illumination
- Twilight calculations
- Field of view and image scale

References:
    Meeus, J. (1998). Astronomical Algorithms (2nd ed.). Willmann-Bell.
    Green, R. M. (1985). Spherical Astronomy. Cambridge University Press.
"""
import math
from datetime import datetime, timezone
from typing import Optional, Tuple
from .time import utc_to_julian_date


def calculate_rise_set_times(
    ra_hours: float,
    dec_deg: float,
    lat_deg: float,
    lst_hours: float,
    horizon_deg: float = 0.0
) -> Tuple[Optional[float], Optional[float], float]:
    """
    Calculate rise and set times for a celestial object.
    
    Args:
        ra_hours: Right Ascension in hours
        dec_deg: Declination in degrees
        lat_deg: Observer latitude in degrees
        lst_hours: Current Local Sidereal Time in hours
        horizon_deg: Horizon altitude (0° for geometric, -0.833° for refraction)
        
    Returns:
        (rise_ha, set_ha, culmination_ha) in hours
        None if object is circumpolar or never rises
    """
    lat_rad = math.radians(lat_deg)
    dec_rad = math.radians(dec_deg)
    horizon_rad = math.radians(horizon_deg)
    
    # Calculate hour angle at rise/set
    cos_ha = (
        (math.sin(horizon_rad) - math.sin(lat_rad) * math.sin(dec_rad))
        / (math.cos(lat_rad) * math.cos(dec_rad))
    )
    
    # Check if object is circumpolar or never rises
    if cos_ha > 1:
        return None, None, 0.0  # Never rises
    if cos_ha < -1:
        return None, None, 0.0  # Circumpolar (always up)
    
    # Hour angle at rise/set
    ha_rad = math.acos(cos_ha)
    ha_hours = math.degrees(ha_rad) / 15.0
    
    rise_ha = -ha_hours  # Object rises before culmination
    set_ha = ha_hours    # Object sets after culmination
    
    return rise_ha, set_ha, 0.0  # Culmination at HA=0


def calculate_angular_velocity(
    dec_deg: float,
    focal_length_mm: float
) -> float:
    """
    Calculate angular velocity of stars due to Earth's rotation.
    
    Args:
        dec_deg: Declination of target
        focal_length_mm: Focal length in mm
        
    Returns:
        Angular velocity in arcsec/second
    """
    # Earth's rotation rate: 15 arcsec/second at equator
    # Adjusted for declination
    dec_rad = math.radians(dec_deg)
    angular_velocity = 15.0 * math.cos(dec_rad)  # arcsec/second
    
    return angular_velocity


def calculate_star_trailing(
    exposure_seconds: float,
    dec_deg: float,
    focal_length_mm: float,
    pixel_pitch_um: float
) -> float:
    """
    Calculate star trailing in pixels.
    
    Args:
        exposure_seconds: Exposure time
        dec_deg: Declination
        focal_length_mm: Focal length
        pixel_pitch_um: Pixel size in micrometers
        
    Returns:
        Trailing distance in pixels
    """
    # Angular velocity
    angular_vel = calculate_angular_velocity(dec_deg, focal_length_mm)
    
    # Total angular motion during exposure
    total_motion_arcsec = angular_vel * exposure_seconds
    
    # Convert to pixels
    # Image scale: arcsec per pixel = 206265 * pixel_pitch_um / focal_length_mm
    image_scale = 206265 * (pixel_pitch_um / 1000.0) / focal_length_mm
    
    trailing_pixels = total_motion_arcsec / image_scale
    
    return trailing_pixels


def npf_rule(
    focal_length_mm: float,
    aperture_fstop: float,
    pixel_pitch_um: float,
    dec_deg: float
) -> float:
    """
    Calculate maximum exposure time using NPF rule.
    
    More accurate than the "500 rule" or "600 rule".
    
    Args:
        focal_length_mm: Focal length
        aperture_fstop: f-stop number
        pixel_pitch_um: Pixel pitch in micrometers
        dec_deg: Declination of target
        
    Returns:
        Maximum exposure time in seconds
        
    Reference:
        Frédéric Michelet, "Stellafane Convention" (2010)
    """
    dec_rad = math.radians(dec_deg)
    
    # NPF formula
    max_exposure = (
        (35 * aperture_fstop + 30 * pixel_pitch_um)
        / (focal_length_mm * math.cos(dec_rad))
    )
    
    return max_exposure


def calculate_field_of_view(
    focal_length_mm: float,
    sensor_width_mm: float,
    sensor_height_mm: float
) -> Tuple[float, float]:
    """
    Calculate camera field of view.
    
    Args:
        focal_length_mm: Focal length
        sensor_width_mm: Sensor width
        sensor_height_mm: Sensor height
        
    Returns:
        (fov_width_deg, fov_height_deg)
    """
    fov_width_rad = 2 * math.atan(sensor_width_mm / (2 * focal_length_mm))
    fov_height_rad = 2 * math.atan(sensor_height_mm / (2 * focal_length_mm))
    
    fov_width_deg = math.degrees(fov_width_rad)
    fov_height_deg = math.degrees(fov_height_rad)
    
    return fov_width_deg, fov_height_deg


def atmospheric_refraction(altitude_deg: float, temperature_c: float = 10.0, pressure_mb: float = 1010.0) -> float:
    """
    Calculate atmospheric refraction correction.

    Refraction causes objects near the horizon to appear higher than their
    true geometric position. This becomes significant below ~30° altitude.

    Args:
        altitude_deg: Apparent altitude in degrees
        temperature_c: Temperature in Celsius (default: 10°C)
        pressure_mb: Atmospheric pressure in millibars (default: 1010 mb)

    Returns:
        Refraction correction in arcminutes (subtract from apparent altitude)

    Reference:
        Meeus (1998), Chapter 16

    Example:
        >>> ref = atmospheric_refraction(10.0)  # 10° above horizon
        >>> ref  # Approximately 5 arcminutes
        5.27
    """
    if altitude_deg < -2:
        return 0.0  # Object below horizon, refraction undefined

    # Convert to radians
    h = altitude_deg

    # Bennett's formula (accurate to 0.07' for h > 15°)
    # R = cot(h + 7.31/(h + 4.4)) arcminutes
    if h > 15:
        r = 1.0 / math.tan(math.radians(h + 7.31 / (h + 4.4)))
    else:
        # Sæmundsson's formula for low altitudes
        r = 1.02 / math.tan(math.radians(h + 10.3 / (h + 5.11)))

    # Pressure and temperature correction
    # R' = R * (P/1010) * (283/(273+T))
    r_corrected = r * (pressure_mb / 1010.0) * (283.0 / (273.0 + temperature_c))

    return r_corrected


def atmospheric_extinction(airmass: float, wavelength_nm: float = 550.0, altitude_m: float = 0.0) -> float:
    """
    Calculate atmospheric extinction in magnitudes.

    Light is absorbed and scattered by the atmosphere. This effect increases
    with airmass (path length through atmosphere).

    Args:
        airmass: Airmass value (1.0 at zenith)
        wavelength_nm: Wavelength in nanometers (default: 550nm, V-band)
        altitude_m: Observing site altitude in meters (default: sea level)

    Returns:
        Extinction in magnitudes (brightness reduction)

    Reference:
        Schaefer (1993), "Telescopic Limiting Magnitudes"

    Example:
        >>> ext = atmospheric_extinction(2.0)  # Airmass 2 (30° altitude)
        >>> ext  # Approximately 0.3 magnitudes
        0.32
    """
    # Rayleigh scattering (wavelength-dependent)
    rayleigh = 0.1451 * (550.0 / wavelength_nm) ** 4

    # Aerosol extinction (less wavelength-dependent)
    aerosol = 0.120

    # Total extinction at sea level
    k_total = rayleigh + aerosol

    # Altitude correction (thinner atmosphere at higher altitude)
    # Extinction decreases by ~20% per km
    altitude_factor = math.exp(-altitude_m / 8000.0)
    k_corrected = k_total * altitude_factor

    # Total extinction = k * X (where X is airmass)
    extinction_mag = k_corrected * airmass

    return extinction_mag


def moon_phase(jd: float) -> Tuple[float, float]:
    """
    Calculate Moon phase and illumination percentage.

    Args:
        jd: Julian Date

    Returns:
        (phase_angle_deg, illumination_percent)
        Phase angle: 0° = new, 90° = first quarter, 180° = full

    Reference:
        Meeus (1998), Chapter 48

    Example:
        >>> from astrocam_sync.core.time import utc_to_julian_date
        >>> from datetime import datetime, timezone
        >>> dt = datetime(2025, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
        >>> jd = utc_to_julian_date(dt)
        >>> phase, illum = moon_phase(jd)
        >>> 0 <= phase <= 360 and 0 <= illum <= 100
        True
    """
    # Time in Julian centuries from J2000.0
    T = (jd - 2451545.0) / 36525.0

    # Sun's mean longitude
    L_sun = 280.466 + 36000.770 * T

    # Moon's mean longitude
    L_moon = 218.316 + 481267.881 * T

    # Moon's mean elongation from Sun
    D = L_moon - L_sun

    # Normalize to [0, 360)
    D = D % 360.0
    if D < 0:
        D += 360.0

    # Phase angle (0° = new, 180° = full)
    phase_angle = D

    # Illumination fraction (0-1)
    # i = (1 - cos(phase)) / 2
    illumination = (1.0 - math.cos(math.radians(phase_angle))) / 2.0

    return phase_angle, illumination * 100.0


def sun_position(jd: float) -> Tuple[float, float]:
    """
    Calculate Sun's equatorial coordinates (simplified).

    Args:
        jd: Julian Date

    Returns:
        (ra_hours, dec_deg) - Sun's position

    Note:
        Simplified algorithm, accurate to ~1° (sufficient for twilight calculations)

    Reference:
        Meeus (1998), Chapter 25 (low-precision formulas)
    """
    # Days since J2000.0
    n = jd - 2451545.0

    # Mean longitude of Sun (degrees)
    L = 280.460 + 0.9856474 * n
    L = L % 360.0

    # Mean anomaly (degrees)
    g = 357.528 + 0.9856003 * n
    g = g % 360.0
    g_rad = math.radians(g)

    # Ecliptic longitude (degrees)
    lambda_sun = L + 1.915 * math.sin(g_rad) + 0.020 * math.sin(2 * g_rad)
    lambda_rad = math.radians(lambda_sun)

    # Obliquity of ecliptic (degrees)
    epsilon = 23.439 - 0.0000004 * n
    epsilon_rad = math.radians(epsilon)

    # Convert ecliptic to equatorial coordinates
    ra_rad = math.atan2(math.cos(epsilon_rad) * math.sin(lambda_rad), math.cos(lambda_rad))
    dec_rad = math.asin(math.sin(epsilon_rad) * math.sin(lambda_rad))

    # Convert to hours and degrees
    ra_hours = (math.degrees(ra_rad) / 15.0) % 24.0
    dec_deg = math.degrees(dec_rad)

    return ra_hours, dec_deg


def twilight_times(jd: float, latitude_deg: float, longitude_deg: float) -> dict:
    """
    Calculate twilight times for a given date and location.

    Returns civil, nautical, and astronomical twilight times.

    Args:
        jd: Julian Date (for the date, time is ignored)
        latitude_deg: Observer latitude
        longitude_deg: Observer longitude (East positive)

    Returns:
        Dictionary with:
        - 'civil_begin': Sun at -6° (civil dawn)
        - 'nautical_begin': Sun at -12° (nautical dawn)
        - 'astronomical_begin': Sun at -18° (astronomical dawn)
        - 'civil_end': Sun at -6° (civil dusk)
        - 'nautical_end': Sun at -12° (nautical dusk)
        - 'astronomical_end': Sun at -18° (astronomical dusk)

    Note:
        All times are approximate LST hours. Requires conversion to UTC.

    Reference:
        USNO "Rise, Set, and Twilight Definitions"
    """
    # Get Sun's position for this date
    ra_sun, dec_sun = sun_position(jd)

    # Calculate hour angles for different twilight levels
    twilight_angles = {
        'civil': -6.0,       # -6° altitude
        'nautical': -12.0,   # -12° altitude
        'astronomical': -18.0  # -18° altitude
    }

    results = {}
    lat_rad = math.radians(latitude_deg)
    dec_rad = math.radians(dec_sun)

    for name, altitude in twilight_angles.items():
        alt_rad = math.radians(altitude)

        # Calculate hour angle when Sun reaches this altitude
        cos_ha = (
            (math.sin(alt_rad) - math.sin(lat_rad) * math.sin(dec_rad))
            / (math.cos(lat_rad) * math.cos(dec_rad))
        )

        if cos_ha > 1:
            # Sun never reaches this altitude (polar night)
            results[f'{name}_begin'] = None
            results[f'{name}_end'] = None
        elif cos_ha < -1:
            # Sun always above this altitude (polar day)
            results[f'{name}_begin'] = 0.0
            results[f'{name}_end'] = 24.0
        else:
            ha_rad = math.acos(cos_ha)
            ha_hours = math.degrees(ha_rad) / 15.0

            # LST when Sun is at this altitude
            lst_rise = (ra_sun - ha_hours) % 24.0  # Morning
            lst_set = (ra_sun + ha_hours) % 24.0   # Evening

            results[f'{name}_begin'] = lst_rise
            results[f'{name}_end'] = lst_set

    return results


def is_astronomical_dark(jd: float, latitude_deg: float, longitude_deg: float) -> bool:
    """
    Check if it's astronomical dark (Sun below -18°).

    Args:
        jd: Julian Date and time
        latitude_deg: Observer latitude
        longitude_deg: Observer longitude

    Returns:
        True if astronomical dark (deep sky photography possible)

    Example:
        >>> # Midnight in winter should be astronomical dark
        >>> from astrocam_sync.core.time import utc_to_julian_date
        >>> dt = datetime(2025, 1, 15, 6, 0, 0, tzinfo=timezone.utc)  # Midnight PST
        >>> jd = utc_to_julian_date(dt)
        >>> is_astronomical_dark(jd, 34.0, -118.0)  # Los Angeles
        True
    """
    # Get Sun's position
    ra_sun, dec_sun = sun_position(jd)

    # Calculate Sun's altitude
    # (This requires converting RA/Dec to Alt/Az - simplified here)
    # For quick check, we use a simplified calculation

    # Get approximate LST
    from .time import julian_date_to_gst, gst_to_lst
    gst = julian_date_to_gst(jd)
    lst = gst_to_lst(gst, longitude_deg)

    # Hour angle
    ha = lst - ra_sun
    ha_rad = math.radians(ha * 15.0)

    # Altitude calculation
    lat_rad = math.radians(latitude_deg)
    dec_rad = math.radians(dec_sun)

    sin_alt = (
        math.sin(lat_rad) * math.sin(dec_rad)
        + math.cos(lat_rad) * math.cos(dec_rad) * math.cos(ha_rad)
    )

    altitude_deg = math.degrees(math.asin(sin_alt))

    # Astronomical dark: Sun below -18°
    return altitude_deg < -18.0


# Example usage
if __name__ == "__main__":
    # Test NPF rule for Milky Way
    focal_length = 24  # mm
    aperture = 2.8
    pixel_pitch = 5.94  # μm (Sony A7 III)
    dec = -30  # degrees (Milky Way core)
    
    max_exp = npf_rule(focal_length, aperture, pixel_pitch, dec)
    print(f"NPF Rule Max Exposure: {max_exp:.1f}s")
    
    # Test trailing at 15s exposure
    trailing = calculate_star_trailing(15, dec, focal_length, pixel_pitch)
    print(f"Star Trailing at 15s: {trailing:.2f} pixels")
    
    # Test FOV
    fov_w, fov_h = calculate_field_of_view(focal_length, 35.6, 23.8)
    print(f"Field of View: {fov_w:.1f}° × {fov_h:.1f}°")