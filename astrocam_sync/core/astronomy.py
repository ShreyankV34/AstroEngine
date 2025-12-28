"""
Celestial mechanics and motion calculations.

Handles object motion, rise/set times, and ephemeris calculations.
"""
import math
from typing import Optional, Tuple


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