"""
Celestial coordinate transformations.

RA/Dec -> Hour Angle -> Alt/Az conversions.
Pure spherical astronomy, no camera coupling.
"""
import math


def ra_to_hour_angle(ra_hours: float, lst_hours: float) -> float:
    """
    Convert Right Ascension to Hour Angle.
    
    Args:
        ra_hours: Right Ascension in hours
        lst_hours: Local Sidereal Time in hours
        
    Returns:
        Hour Angle in hours [-12, 12]
    """
    ha = lst_hours - ra_hours
    
    # Normalize to [-12, 12]
    while ha < -12:
        ha += 24
    while ha > 12:
        ha -= 24
    
    return ha


def equatorial_to_horizontal(
    ra_hours: float,
    dec_deg: float,
    lst_hours: float,
    lat_deg: float
) -> tuple[float, float]:
    """
    Convert equatorial (RA/Dec) to horizontal (Alt/Az) coordinates.
    
    Args:
        ra_hours: Right Ascension in hours
        dec_deg: Declination in degrees
        lst_hours: Local Sidereal Time in hours
        lat_deg: Observer latitude in degrees
        
    Returns:
        (altitude_deg, azimuth_deg) tuple
        
    Reference:
        Meeus, "Astronomical Algorithms", Chapter 13
    """
    # Convert to radians
    ha = ra_to_hour_angle(ra_hours, lst_hours)
    ha_rad = math.radians(ha * 15)  # Convert hours to degrees, then radians
    dec_rad = math.radians(dec_deg)
    lat_rad = math.radians(lat_deg)
    
    # Calculate altitude
    sin_alt = (
        math.sin(dec_rad) * math.sin(lat_rad)
        + math.cos(dec_rad) * math.cos(lat_rad) * math.cos(ha_rad)
    )
    alt_rad = math.asin(sin_alt)
    alt_deg = math.degrees(alt_rad)
    
    # Calculate azimuth
    cos_az = (
        math.sin(dec_rad) - math.sin(lat_rad) * sin_alt
    ) / (math.cos(lat_rad) * math.cos(alt_rad))
    
    # Clamp to avoid numerical errors
    cos_az = max(-1, min(1, cos_az))
    az_rad = math.acos(cos_az)
    az_deg = math.degrees(az_rad)
    
    # Adjust azimuth quadrant based on hour angle
    if math.sin(ha_rad) > 0:
        az_deg = 360 - az_deg
    
    return alt_deg, az_deg


def calculate_airmass(altitude_deg: float) -> float:
    """
    Calculate atmospheric airmass using Rozenberg (1966) formula.
    
    Args:
        altitude_deg: Altitude in degrees
        
    Returns:
        Airmass (1.0 at zenith, increases toward horizon)
        
    Reference:
        Rozenberg, G.V. (1966), "Twilight: A Study in Atmospheric Optics"
    """
    if altitude_deg <= 0:
        return float('inf')
    
    # Zenith distance
    z_deg = 90 - altitude_deg
    z_rad = math.radians(z_deg)
    
    # Rozenberg formula
    airmass = 1.0 / (
        math.cos(z_rad) + 0.025 * math.exp(-11 * math.cos(z_rad))
    )
    
    return airmass


def is_target_visible(
    altitude_deg: float,
    min_altitude: float = 20.0,
    max_airmass: float = 2.5
) -> tuple[bool, str]:
    """
    Check if target is visible based on altitude and airmass.
    
    Args:
        altitude_deg: Target altitude
        min_altitude: Minimum acceptable altitude
        max_airmass: Maximum acceptable airmass
        
    Returns:
        (is_visible, reason) tuple
    """
    if altitude_deg < min_altitude:
        return False, f"Too low (alt={altitude_deg:.1f}°, min={min_altitude}°)"
    
    airmass = calculate_airmass(altitude_deg)
    if airmass > max_airmass:
        return False, f"Too much atmosphere (airmass={airmass:.2f}, max={max_airmass})"
    
    return True, "Visible"


# Example usage
if __name__ == "__main__":
    # Milky Way Core (Sagittarius A*)
    ra = 17.761  # hours
    dec = -29.0  # degrees
    
    # Observer: Los Angeles
    lat = 34.0522  # degrees
    lst = 20.0  # hours (example)
    
    alt, az = equatorial_to_horizontal(ra, dec, lst, lat)
    airmass = calculate_airmass(alt)
    visible, reason = is_target_visible(alt)
    
    print(f"Target: RA {ra}h, Dec {dec}°")
    print(f"Observer: Lat {lat}°, LST {lst}h")
    print(f"Altitude: {alt:.2f}°")
    print(f"Azimuth: {az:.2f}°")
    print(f"Airmass: {airmass:.2f}")
    print(f"Visible: {visible} - {reason}")