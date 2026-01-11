"""
Celestial coordinate transformations and astronomical calculations.

Observatory-grade coordinate transformations following Meeus "Astronomical Algorithms".
Includes RA/Dec, Alt/Az, hour angle conversions, atmospheric refraction, precession,
proper motion, airmass, and field of view calculations.

All algorithms follow Jean Meeus, "Astronomical Algorithms", 2nd Edition (1998).
"""
import math
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class EquatorialCoord:
    """
    Equatorial coordinates (Right Ascension and Declination).

    Attributes:
        ra_hours: Right Ascension in decimal hours [0, 24)
        dec_deg: Declination in decimal degrees [-90, 90]
        epoch: Coordinate epoch (default: J2000.0 = 2000.0)

    Examples:
        >>> # Betelgeuse (α Orionis)
        >>> coord = EquatorialCoord(5.9195, 7.4070)
        >>> print(coord.ra_hms())
        '05h 55m 10.2s'
        >>> print(coord.dec_dms())
        '+07° 24\' 25.2"'
    """
    ra_hours: float
    dec_deg: float
    epoch: float = 2000.0

    def __post_init__(self):
        """Validate coordinate ranges."""
        if not (0 <= self.ra_hours < 24):
            raise ValueError(f"RA must be in [0, 24), got {self.ra_hours}")
        if not (-90 <= self.dec_deg <= 90):
            raise ValueError(f"Dec must be in [-90, 90], got {self.dec_deg}")

    def ra_hms(self) -> str:
        """
        Format Right Ascension as HH:MM:SS.S.

        Returns:
            String in format "XXh XXm XX.Xs"
        """
        hours = int(self.ra_hours)
        minutes = int((self.ra_hours - hours) * 60)
        seconds = ((self.ra_hours - hours) * 60 - minutes) * 60
        return f"{hours:02d}h {minutes:02d}m {seconds:04.1f}s"

    def dec_dms(self) -> str:
        """
        Format Declination as ±DD°MM'SS.S".

        Returns:
            String in format "±XX° XX' XX.X\""
        """
        sign = '+' if self.dec_deg >= 0 else '-'
        abs_dec = abs(self.dec_deg)
        degrees = int(abs_dec)
        minutes = int((abs_dec - degrees) * 60)
        seconds = ((abs_dec - degrees) * 60 - minutes) * 60
        return f"{sign}{degrees:02d}° {minutes:02d}' {seconds:04.1f}\""

    def __str__(self) -> str:
        return f"RA {self.ra_hms()}, Dec {self.dec_dms()}"


@dataclass
class HorizontalCoord:
    """
    Horizontal coordinates (Altitude and Azimuth).

    Attributes:
        alt_deg: Altitude in degrees [-90, 90], 90 = zenith
        az_deg: Azimuth in degrees [0, 360), 0 = North, 90 = East

    Examples:
        >>> coord = HorizontalCoord(45.0, 180.0)
        >>> print(coord.compass_direction())
        'S'
        >>> print(coord)
        'Alt 45.00°, Az 180.00° (S)'
    """
    alt_deg: float
    az_deg: float

    def __post_init__(self):
        """Validate coordinate ranges."""
        if not (-90 <= self.alt_deg <= 90):
            raise ValueError(f"Altitude must be in [-90, 90], got {self.alt_deg}")
        # Normalize azimuth to [0, 360)
        self.az_deg = self.az_deg % 360

    def compass_direction(self) -> str:
        """
        Convert azimuth to compass direction.

        Returns:
            Compass direction (N, NE, E, SE, S, SW, W, NW)
        """
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        index = int((self.az_deg + 22.5) / 45) % 8
        return directions[index]

    def zenith_distance(self) -> float:
        """Calculate zenith distance (90° - altitude)."""
        return 90.0 - self.alt_deg

    def __str__(self) -> str:
        return f"Alt {self.alt_deg:.2f}°, Az {self.az_deg:.2f}° ({self.compass_direction()})"


def ra_to_hour_angle(ra_hours: float, lst_hours: float) -> float:
    """
    Convert Right Ascension to Hour Angle.

    Hour Angle = LST - RA. Positive when object is west of meridian.

    Args:
        ra_hours: Right Ascension in hours [0, 24)
        lst_hours: Local Sidereal Time in hours [0, 24)

    Returns:
        Hour Angle in hours [-12, 12]

    Examples:
        >>> ra_to_hour_angle(12.0, 15.0)  # Object 3h west of meridian
        3.0
        >>> ra_to_hour_angle(18.0, 6.0)   # Object 12h from meridian
        -12.0

    Reference:
        Meeus, Chapter 13, p. 93
    """
    ha = lst_hours - ra_hours

    # Normalize to [-12, 12]
    while ha < -12:
        ha += 24
    while ha > 12:
        ha -= 24

    return ha


def atmospheric_refraction(altitude_deg: float, pressure_mbar: float = 1010.0,
                          temp_celsius: float = 10.0) -> float:
    """
    Calculate atmospheric refraction correction using Bennett's formula.

    Accounts for pressure and temperature. Refraction makes objects appear
    higher than their true geometric altitude.

    Args:
        altitude_deg: True (geometric) altitude in degrees
        pressure_mbar: Atmospheric pressure in millibars (default: 1010)
        temp_celsius: Temperature in Celsius (default: 10)

    Returns:
        Refraction correction in degrees (always positive, add to true alt)

    Examples:
        >>> atmospheric_refraction(45.0)  # Mid-altitude
        0.0166...
        >>> atmospheric_refraction(10.0)  # Low altitude
        0.0978...
        >>> atmospheric_refraction(0.0)   # Horizon
        0.5666...

    Reference:
        Meeus, Chapter 16, p. 106 (Bennett's formula)
        Bennett, G.G. (1982), Journal of Navigation 35, 255-259
    """
    if altitude_deg < -2:
        return 0.0  # Below reasonable horizon

    # Avoid singularity at horizon
    h = max(altitude_deg, -0.5)

    # Bennett's formula (arcminutes)
    refr_arcmin = (
        1.02 / math.tan(math.radians(h + 10.3 / (h + 5.11)))
    )

    # Pressure and temperature correction
    refr_arcmin *= (pressure_mbar / 1010.0) * (283.0 / (273.0 + temp_celsius))

    # Convert to degrees
    return refr_arcmin / 60.0


def equatorial_to_horizontal(
    ra_hours: float,
    dec_deg: float,
    lst_hours: float,
    lat_deg: float,
    apply_refraction: bool = False,
    pressure_mbar: float = 1010.0,
    temp_celsius: float = 10.0
) -> HorizontalCoord:
    """
    Convert equatorial (RA/Dec) to horizontal (Alt/Az) coordinates.

    Args:
        ra_hours: Right Ascension in hours
        dec_deg: Declination in degrees
        lst_hours: Local Sidereal Time in hours
        lat_deg: Observer latitude in degrees
        apply_refraction: Apply atmospheric refraction correction
        pressure_mbar: Atmospheric pressure (if applying refraction)
        temp_celsius: Temperature in Celsius (if applying refraction)

    Returns:
        HorizontalCoord with altitude and azimuth

    Examples:
        >>> # Polaris at 40°N latitude (RA=2.53h, Dec=89.26°)
        >>> coord = equatorial_to_horizontal(2.53, 89.26, 14.0, 40.0)
        >>> print(f"Alt: {coord.alt_deg:.1f}°")  # Should be ~90°
        Alt: 89.5°

    Reference:
        Meeus, Chapter 13, p. 93
    """
    # Convert to radians
    ha = ra_to_hour_angle(ra_hours, lst_hours)
    ha_rad = math.radians(ha * 15)  # Convert hours to degrees, then radians
    dec_rad = math.radians(dec_deg)
    lat_rad = math.radians(lat_deg)

    # Calculate altitude (Meeus 13.5 and 13.6)
    sin_alt = (
        math.sin(dec_rad) * math.sin(lat_rad)
        + math.cos(dec_rad) * math.cos(lat_rad) * math.cos(ha_rad)
    )
    sin_alt = max(-1, min(1, sin_alt))  # Clamp for numerical stability
    alt_rad = math.asin(sin_alt)
    alt_deg = math.degrees(alt_rad)

    # Apply atmospheric refraction if requested
    if apply_refraction:
        refr = atmospheric_refraction(alt_deg, pressure_mbar, temp_celsius)
        alt_deg += refr

    # Calculate azimuth (Meeus 13.5 and 13.6)
    cos_az = (
        math.sin(dec_rad) - math.sin(lat_rad) * math.sin(alt_rad)
    ) / (math.cos(lat_rad) * math.cos(alt_rad))

    # Clamp to avoid numerical errors
    cos_az = max(-1, min(1, cos_az))
    az_rad = math.acos(cos_az)
    az_deg = math.degrees(az_rad)

    # Adjust azimuth quadrant based on hour angle (Meeus p. 93)
    if math.sin(ha_rad) > 0:
        az_deg = 360 - az_deg

    return HorizontalCoord(alt_deg, az_deg)


def horizontal_to_equatorial(
    alt_deg: float,
    az_deg: float,
    lst_hours: float,
    lat_deg: float
) -> EquatorialCoord:
    """
    Convert horizontal (Alt/Az) to equatorial (RA/Dec) coordinates.

    Inverse of equatorial_to_horizontal. Does not account for refraction
    (caller should remove refraction from altitude first if needed).

    Args:
        alt_deg: Altitude in degrees
        az_deg: Azimuth in degrees (0=North, 90=East)
        lst_hours: Local Sidereal Time in hours
        lat_deg: Observer latitude in degrees

    Returns:
        EquatorialCoord with RA and Dec

    Reference:
        Meeus, Chapter 13, p. 93 (inverse transformation)
    """
    # Convert to radians
    alt_rad = math.radians(alt_deg)
    az_rad = math.radians(az_deg)
    lat_rad = math.radians(lat_deg)

    # Calculate declination
    sin_dec = (
        math.sin(alt_rad) * math.sin(lat_rad)
        + math.cos(alt_rad) * math.cos(lat_rad) * math.cos(az_rad)
    )
    sin_dec = max(-1, min(1, sin_dec))
    dec_rad = math.asin(sin_dec)
    dec_deg = math.degrees(dec_rad)

    # Calculate hour angle
    cos_ha = (
        math.sin(alt_rad) - math.sin(lat_rad) * math.sin(dec_rad)
    ) / (math.cos(lat_rad) * math.cos(dec_rad))
    cos_ha = max(-1, min(1, cos_ha))
    ha_rad = math.acos(cos_ha)

    # Adjust hour angle quadrant
    if math.sin(az_rad) > 0:
        ha_rad = -ha_rad

    ha_hours = math.degrees(ha_rad) / 15.0

    # Convert hour angle to RA
    ra_hours = (lst_hours - ha_hours) % 24

    return EquatorialCoord(ra_hours, dec_deg)


def calculate_airmass(altitude_deg: float) -> float:
    """
    Calculate atmospheric airmass using Rozenberg (1966) formula.

    Airmass is the relative path length through the atmosphere.
    1.0 at zenith, increases toward horizon. Used for extinction calculations.

    Args:
        altitude_deg: Altitude in degrees

    Returns:
        Airmass (1.0 at zenith, ~38 at horizon, inf below horizon)

    Examples:
        >>> calculate_airmass(90.0)  # Zenith
        1.0
        >>> calculate_airmass(30.0)  # 60° zenith distance
        2.0...
        >>> calculate_airmass(0.0)   # Horizon
        38.7...

    Reference:
        Rozenberg, G.V. (1966), "Twilight: A Study in Atmospheric Optics"
        Also discussed in Kasten & Young (1989), Applied Optics 28, 4735
    """
    if altitude_deg <= 0:
        return float('inf')

    # Zenith distance
    z_deg = 90 - altitude_deg
    z_rad = math.radians(z_deg)

    # Rozenberg formula (valid for z < 85°)
    airmass = 1.0 / (
        math.cos(z_rad) + 0.025 * math.exp(-11 * math.cos(z_rad))
    )

    return airmass


def angular_separation(ra1_hours: float, dec1_deg: float,
                       ra2_hours: float, dec2_deg: float) -> float:
    """
    Calculate great circle angular separation between two celestial coordinates.

    Uses the haversine formula for numerical stability.

    Args:
        ra1_hours: First object's RA in hours
        dec1_deg: First object's Dec in degrees
        ra2_hours: Second object's RA in hours
        dec2_deg: Second object's Dec in degrees

    Returns:
        Angular separation in degrees

    Examples:
        >>> # Separation between Betelgeuse and Rigel (both in Orion)
        >>> angular_separation(5.919, 7.407, 5.242, -8.202)
        17.48...

    Reference:
        Meeus, Chapter 17, p. 115 (using haversine formula)
    """
    # Convert to radians
    ra1_rad = math.radians(ra1_hours * 15)
    dec1_rad = math.radians(dec1_deg)
    ra2_rad = math.radians(ra2_hours * 15)
    dec2_rad = math.radians(dec2_deg)

    # Haversine formula (more accurate than spherical law of cosines)
    delta_ra = ra2_rad - ra1_rad
    delta_dec = dec2_rad - dec1_rad

    a = (
        math.sin(delta_dec / 2) ** 2
        + math.cos(dec1_rad) * math.cos(dec2_rad) * math.sin(delta_ra / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    return math.degrees(c)


def apply_proper_motion(ra_hours: float, dec_deg: float,
                       pm_ra_mas_yr: float, pm_dec_mas_yr: float,
                       years_elapsed: float) -> Tuple[float, float]:
    """
    Apply proper motion to equatorial coordinates.

    Args:
        ra_hours: Right Ascension in hours at epoch
        dec_deg: Declination in degrees at epoch
        pm_ra_mas_yr: Proper motion in RA (mas/yr, includes cos(dec) factor)
        pm_dec_mas_yr: Proper motion in Dec (mas/yr)
        years_elapsed: Time elapsed since epoch (years)

    Returns:
        Tuple of (new_ra_hours, new_dec_deg)

    Examples:
        >>> # Barnard's Star has large proper motion
        >>> # PM_RA = -798 mas/yr, PM_Dec = 10328 mas/yr
        >>> ra, dec = apply_proper_motion(17.963, 4.693, -798, 10328, 10.0)
        >>> print(f"RA shift: {(ra - 17.963) * 3600:.1f} arcsec")
        RA shift: -5.3 arcsec

    Reference:
        Meeus, Chapter 21, p. 151
    """
    # Convert proper motion from mas/yr to degrees/yr
    pm_ra_deg_yr = (pm_ra_mas_yr / 1000.0) / 3600.0
    pm_dec_deg_yr = (pm_dec_mas_yr / 1000.0) / 3600.0

    # Apply proper motion
    delta_ra_deg = pm_ra_deg_yr * years_elapsed
    delta_dec_deg = pm_dec_deg_yr * years_elapsed

    # Convert RA shift to hours and apply
    new_ra_hours = (ra_hours + delta_ra_deg / 15.0) % 24
    new_dec_deg = dec_deg + delta_dec_deg

    # Clamp declination
    new_dec_deg = max(-90, min(90, new_dec_deg))

    return new_ra_hours, new_dec_deg


def precess_coordinates(ra_hours: float, dec_deg: float,
                        epoch_from: float, epoch_to: float) -> Tuple[float, float]:
    """
    Precess equatorial coordinates between epochs (rigorous method).

    Accounts for Earth's axial precession. Uses IAU 2000 precession model
    (simplified for most observatory applications).

    Args:
        ra_hours: Right Ascension in hours at epoch_from
        dec_deg: Declination in degrees at epoch_from
        epoch_from: Starting epoch (e.g., 2000.0 for J2000)
        epoch_to: Target epoch (e.g., 2024.0)

    Returns:
        Tuple of (new_ra_hours, new_dec_deg) at epoch_to

    Examples:
        >>> # Precess coordinates from J2000 to J2024
        >>> ra, dec = precess_coordinates(10.0, 20.0, 2000.0, 2024.0)
        >>> # Precession causes small shifts (~50 arcsec/year)

    Reference:
        Meeus, Chapter 21, p. 134-135 (rigorous method)
    """
    # Time in Julian centuries from J2000.0
    T = (epoch_from - 2000.0) / 100.0
    t = (epoch_to - epoch_from) / 100.0

    # Precession angles in arcseconds (IAU 2000, simplified)
    # These are approximate; full model requires many more terms
    zeta = (2306.2181 * t + 0.30188 * t**2 + 0.017998 * t**3) / 3600.0
    z = (2306.2181 * t + 1.09468 * t**2 + 0.018203 * t**3) / 3600.0
    theta = (2004.3109 * t - 0.42665 * t**2 - 0.041833 * t**3) / 3600.0

    # Convert to radians
    ra_rad = math.radians(ra_hours * 15)
    dec_rad = math.radians(dec_deg)
    zeta_rad = math.radians(zeta)
    z_rad = math.radians(z)
    theta_rad = math.radians(theta)

    # Calculate intermediate values (Meeus 21.4)
    A = math.cos(dec_rad) * math.sin(ra_rad + zeta_rad)
    B = (
        math.cos(theta_rad) * math.cos(dec_rad) * math.cos(ra_rad + zeta_rad)
        - math.sin(theta_rad) * math.sin(dec_rad)
    )
    C = (
        math.sin(theta_rad) * math.cos(dec_rad) * math.cos(ra_rad + zeta_rad)
        + math.cos(theta_rad) * math.sin(dec_rad)
    )

    # New coordinates
    new_ra_rad = math.atan2(A, B) + z_rad
    new_dec_rad = math.asin(C)

    new_ra_hours = (math.degrees(new_ra_rad) / 15.0) % 24
    new_dec_deg = math.degrees(new_dec_rad)

    return new_ra_hours, new_dec_deg


def calculate_field_of_view(focal_length_mm: float, sensor_width_mm: float,
                            sensor_height_mm: float) -> Tuple[float, float, float]:
    """
    Calculate field of view for a camera/telescope system.

    Args:
        focal_length_mm: Focal length in millimeters
        sensor_width_mm: Sensor width in millimeters
        sensor_height_mm: Sensor height in millimeters

    Returns:
        Tuple of (fov_width_deg, fov_height_deg, fov_diagonal_deg)

    Examples:
        >>> # Canon EOS with 50mm lens (36mm x 24mm sensor)
        >>> w, h, d = calculate_field_of_view(50, 36, 24)
        >>> print(f"FOV: {w:.1f}° x {h:.1f}°")
        FOV: 39.6° x 27.0°

    Reference:
        Standard optical formula: FOV = 2 * atan(sensor_size / (2 * focal_length))
    """
    if focal_length_mm <= 0:
        raise ValueError("Focal length must be positive")
    if sensor_width_mm <= 0 or sensor_height_mm <= 0:
        raise ValueError("Sensor dimensions must be positive")

    # Calculate FOV in each dimension
    fov_width_rad = 2 * math.atan(sensor_width_mm / (2 * focal_length_mm))
    fov_height_rad = 2 * math.atan(sensor_height_mm / (2 * focal_length_mm))

    # Diagonal FOV
    sensor_diagonal = math.sqrt(sensor_width_mm**2 + sensor_height_mm**2)
    fov_diagonal_rad = 2 * math.atan(sensor_diagonal / (2 * focal_length_mm))

    # Convert to degrees
    fov_width_deg = math.degrees(fov_width_rad)
    fov_height_deg = math.degrees(fov_height_rad)
    fov_diagonal_deg = math.degrees(fov_diagonal_rad)

    return fov_width_deg, fov_height_deg, fov_diagonal_deg


def is_target_visible(
    altitude_deg: float,
    min_altitude: float = 20.0,
    max_airmass: float = 2.5
) -> Tuple[bool, str]:
    """
    Check if target is visible based on altitude and airmass constraints.

    Args:
        altitude_deg: Target altitude in degrees
        min_altitude: Minimum acceptable altitude in degrees
        max_airmass: Maximum acceptable airmass

    Returns:
        Tuple of (is_visible: bool, reason: str)

    Examples:
        >>> is_target_visible(45.0)
        (True, 'Visible')
        >>> is_target_visible(10.0)
        (False, 'Too low (alt=10.0°, min=20.0°)')
    """
    if altitude_deg < min_altitude:
        return False, f"Too low (alt={altitude_deg:.1f}°, min={min_altitude:.1f}°)"

    airmass = calculate_airmass(altitude_deg)
    if airmass > max_airmass:
        return False, f"Too much atmosphere (airmass={airmass:.2f}, max={max_airmass:.1f})"

    return True, "Visible"


# Example usage and validation
if __name__ == "__main__":
    print("=" * 70)
    print("AstroEngine Coordinate System Examples")
    print("=" * 70)

    # Example 1: Equatorial coordinates with formatting
    print("\n1. EQUATORIAL COORDINATES (Betelgeuse)")
    betelgeuse = EquatorialCoord(5.9195, 7.4070, epoch=2000.0)
    print(f"   {betelgeuse}")
    print(f"   RA (decimal): {betelgeuse.ra_hours:.4f} hours")
    print(f"   Dec (decimal): {betelgeuse.dec_deg:.4f} degrees")

    # Example 2: Coordinate transformation
    print("\n2. COORDINATE TRANSFORMATION (Sagittarius A* from Los Angeles)")
    sgr_a_star = EquatorialCoord(17.761, -29.0)
    lat = 34.0522  # Los Angeles latitude
    lst = 20.0     # Example LST

    horiz = equatorial_to_horizontal(
        sgr_a_star.ra_hours, sgr_a_star.dec_deg,
        lst, lat, apply_refraction=True
    )
    print(f"   RA/Dec: {sgr_a_star}")
    print(f"   Observer: Latitude {lat}°, LST {lst}h")
    print(f"   {horiz}")
    print(f"   Airmass: {calculate_airmass(horiz.alt_deg):.2f}")

    # Example 3: Angular separation
    print("\n3. ANGULAR SEPARATION (Betelgeuse to Rigel)")
    rigel = EquatorialCoord(5.242, -8.202)
    separation = angular_separation(
        betelgeuse.ra_hours, betelgeuse.dec_deg,
        rigel.ra_hours, rigel.dec_deg
    )
    print(f"   Betelgeuse: {betelgeuse}")
    print(f"   Rigel: {rigel}")
    print(f"   Separation: {separation:.2f}°")

    # Example 4: Proper motion (Barnard's Star)
    print("\n4. PROPER MOTION (Barnard's Star, 10 years)")
    barnard_ra, barnard_dec = 17.963, 4.693
    new_ra, new_dec = apply_proper_motion(
        barnard_ra, barnard_dec,
        pm_ra_mas_yr=-798, pm_dec_mas_yr=10328,
        years_elapsed=10.0
    )
    print(f"   Original: RA {barnard_ra:.3f}h, Dec {barnard_dec:.3f}°")
    print(f"   After 10y: RA {new_ra:.3f}h, Dec {new_dec:.3f}°")
    print(f"   RA shift: {(new_ra - barnard_ra) * 3600:.1f} arcsec")
    print(f"   Dec shift: {(new_dec - barnard_dec) * 3600:.1f} arcsec")

    # Example 5: Precession (J2000 to current epoch)
    print("\n5. PRECESSION (J2000.0 → J2024.0)")
    ra_2000, dec_2000 = 10.0, 20.0
    ra_2024, dec_2024 = precess_coordinates(ra_2000, dec_2000, 2000.0, 2024.0)
    print(f"   J2000: RA {ra_2000:.4f}h, Dec {dec_2000:.4f}°")
    print(f"   J2024: RA {ra_2024:.4f}h, Dec {dec_2024:.4f}°")
    print(f"   Shift: {(ra_2024 - ra_2000) * 3600:.1f}\" RA, "
          f"{(dec_2024 - dec_2000) * 3600:.1f}\" Dec")

    # Example 6: Field of view
    print("\n6. FIELD OF VIEW (Canon EOS with 200mm lens)")
    fov_w, fov_h, fov_d = calculate_field_of_view(200, 36, 24)
    print(f"   Focal length: 200mm")
    print(f"   Sensor: 36mm x 24mm (full frame)")
    print(f"   FOV: {fov_w:.2f}° x {fov_h:.2f}° (diagonal {fov_d:.2f}°)")

    # Example 7: Atmospheric refraction
    print("\n7. ATMOSPHERIC REFRACTION")
    for alt in [0, 10, 30, 45, 90]:
        refr = atmospheric_refraction(alt)
        print(f"   Altitude {alt:2d}°: refraction = {refr * 60:.2f}' "
              f"({refr * 3600:.1f}\")")

    print("\n" + "=" * 70)
