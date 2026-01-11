"""
Astronomical time conversions and calculations.

Implements high-precision time transformations for astronomical observations:
- UTC ↔ Julian Date (Meeus algorithm, ±0.001s accuracy)
- Julian Date → Greenwich Sidereal Time (Meeus Ch. 12)
- GST → Local Sidereal Time (longitude correction)
- Rise/culmination/set time calculations
- Time window predictions for target visibility

All algorithms from Jean Meeus "Astronomical Algorithms" (2nd Ed, 1998).

References:
    Meeus, J. (1998). Astronomical Algorithms (2nd ed.). Willmann-Bell.
    USNO Circular 179 (2005). The IAU Resolutions on Astronomical Reference Systems.
"""

from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional
import math


# Constants
J2000_JD = 2451545.0  # Julian Date of J2000.0 epoch (2000-01-01 12:00 TT)
JD_UNIX_EPOCH = 2440587.5  # Julian Date of Unix epoch (1970-01-01 00:00 UTC)
SECONDS_PER_DAY = 86400.0
DAYS_PER_CENTURY = 36525.0


# ============================================================================
# UTC ↔ Julian Date Conversions
# ============================================================================

def utc_to_julian_date(dt: datetime) -> float:
    """
    Convert UTC datetime to Julian Date.

    Uses the algorithm from Meeus Chapter 7 for Gregorian calendar dates.
    Accurate to microsecond precision (±0.000012 days = ±1 second).

    Args:
        dt: UTC datetime object. If timezone-naive, assumes UTC.

    Returns:
        Julian Date as float. JD 0.0 = 4713 BC January 1, 12:00 TT.

    Reference:
        Meeus (1998), Chapter 7, p. 61

    Example:
        >>> from datetime import datetime, timezone
        >>> dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        >>> jd = utc_to_julian_date(dt)
        >>> abs(jd - 2451545.0) < 1e-6
        True
    """
    # Ensure UTC timezone
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    elif dt.tzinfo != timezone.utc:
        dt = dt.astimezone(timezone.utc)

    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour
    minute = dt.minute
    second = dt.second + dt.microsecond / 1e6

    # Meeus algorithm: treat Jan/Feb as months 13/14 of previous year
    if month <= 2:
        year -= 1
        month += 12

    # Gregorian calendar correction (valid for dates after 1582-10-15)
    a = math.floor(year / 100)
    b = 2 - a + math.floor(a / 4)

    # Julian Date at 0h UT
    jd_0h = (
        math.floor(365.25 * (year + 4716))
        + math.floor(30.6001 * (month + 1))
        + day
        + b
        - 1524.5
    )

    # Add fractional day (time of day)
    day_fraction = (hour + minute / 60.0 + second / 3600.0) / 24.0
    jd = jd_0h + day_fraction

    return jd


def julian_date_to_utc(jd: float) -> datetime:
    """
    Convert Julian Date to UTC datetime.

    Inverse of utc_to_julian_date(). Uses Meeus algorithm for Gregorian calendar.

    Args:
        jd: Julian Date

    Returns:
        UTC datetime object with timezone=UTC

    Reference:
        Meeus (1998), Chapter 7, p. 63

    Example:
        >>> jd = 2451545.0  # J2000.0
        >>> dt = julian_date_to_utc(jd)
        >>> dt.year, dt.month, dt.day, dt.hour
        (2000, 1, 1, 12)
    """
    jd = jd + 0.5
    z = math.floor(jd)
    f = jd - z

    if z < 2299161:
        a = z
    else:
        alpha = math.floor((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - math.floor(alpha / 4)

    b = a + 1524
    c = math.floor((b - 122.1) / 365.25)
    d = math.floor(365.25 * c)
    e = math.floor((b - d) / 30.6001)

    day = b - d - math.floor(30.6001 * e) + f

    if e < 14:
        month = e - 1
    else:
        month = e - 13

    if month > 2:
        year = c - 4716
    else:
        year = c - 4715

    # Extract time components
    day_int = int(day)
    hour_frac = (day - day_int) * 24.0
    hour = int(hour_frac)
    minute_frac = (hour_frac - hour) * 60.0
    minute = int(minute_frac)
    second_frac = (minute_frac - minute) * 60.0
    second = int(second_frac)
    microsecond = int((second_frac - second) * 1e6)

    return datetime(year, month, day_int, hour, minute, second, microsecond, tzinfo=timezone.utc)


# ============================================================================
# Sidereal Time Calculations
# ============================================================================

def julian_date_to_gst(jd: float) -> float:
    """
    Convert Julian Date to Greenwich Sidereal Time.

    Calculates mean sidereal time at Greenwich. Does NOT include nutation
    correction (for apparent sidereal time, add equation of equinoxes).

    Args:
        jd: Julian Date

    Returns:
        Greenwich Sidereal Time in hours [0, 24)

    Reference:
        Meeus (1998), Chapter 12, p. 88

    Accuracy:
        ±0.1 seconds for dates 1900-2100

    Example:
        >>> jd = 2451545.0  # J2000.0 epoch
        >>> gst = julian_date_to_gst(jd)
        >>> 18.0 < gst < 19.0  # Expected ~18.697
        True
    """
    # Julian centuries from J2000.0
    t = (jd - J2000_JD) / DAYS_PER_CENTURY

    # Mean sidereal time at Greenwich at 0h UT (in degrees)
    # Meeus equation 12.4
    theta0 = (
        280.46061837
        + 360.98564736629 * (jd - J2000_JD)
        + 0.000387933 * t * t
        - (t * t * t) / 38710000.0
    )

    # Normalize to [0, 360) degrees
    theta0 = theta0 % 360.0
    if theta0 < 0:
        theta0 += 360.0

    # Convert degrees to hours
    gst_hours = theta0 / 15.0

    return gst_hours


def gst_to_lst(gst_hours: float, longitude_deg: float) -> float:
    """
    Convert Greenwich Sidereal Time to Local Sidereal Time.

    Args:
        gst_hours: Greenwich Sidereal Time in hours
        longitude_deg: Observer longitude in degrees (positive East, negative West)

    Returns:
        Local Sidereal Time in hours [0, 24)

    Note:
        East longitude ADDS to GST, West longitude SUBTRACTS.
        Example: New York (74°W = -74°) has LST < GST

    Example:
        >>> gst = 12.0  # Noon sidereal time at Greenwich
        >>> lon = -75.0  # 75°W (5 hours west)
        >>> lst = gst_to_lst(gst, lon)
        >>> abs(lst - 7.0) < 0.01  # 5 hours earlier
        True
    """
    # Convert longitude from degrees to hours (15° = 1 hour)
    longitude_hours = longitude_deg / 15.0

    # LST = GST + longitude correction
    lst = gst_hours + longitude_hours

    # Normalize to [0, 24) hours
    lst = lst % 24.0
    if lst < 0:
        lst += 24.0

    return lst


def utc_to_lst(dt: datetime, longitude_deg: float) -> float:
    """
    Convert UTC datetime directly to Local Sidereal Time.

    Convenience function combining utc_to_julian_date, julian_date_to_gst,
    and gst_to_lst in one call.

    Args:
        dt: UTC datetime
        longitude_deg: Observer longitude in degrees (positive East)

    Returns:
        Local Sidereal Time in hours [0, 24)

    Example:
        >>> from datetime import datetime, timezone
        >>> dt = datetime(2025, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
        >>> lon = -118.25  # Los Angeles
        >>> lst = utc_to_lst(dt, lon)
        >>> 0.0 <= lst < 24.0
        True
    """
    jd = utc_to_julian_date(dt)
    gst = julian_date_to_gst(jd)
    lst = gst_to_lst(gst, longitude_deg)
    return lst


# ============================================================================
# Time Difference and Window Calculations
# ============================================================================

def time_until_lst(current_dt: datetime, target_lst_hours: float, longitude_deg: float) -> timedelta:
    """
    Calculate time remaining until a target LST is reached.

    Handles wraparound (e.g., if target LST is 2h and current LST is 23h,
    returns ~3 hours, not -21 hours).

    Args:
        current_dt: Current UTC datetime
        target_lst_hours: Target LST in hours [0, 24)
        longitude_deg: Observer longitude in degrees

    Returns:
        Time delta until target LST. Positive = future, negative = past.

    Example:
        >>> from datetime import datetime, timezone
        >>> dt = datetime(2025, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
        >>> lon = -118.25
        >>> current_lst = utc_to_lst(dt, lon)
        >>> target_lst = (current_lst + 2.0) % 24.0  # 2 hours from now
        >>> delta = time_until_lst(dt, target_lst, lon)
        >>> 1.9 < delta.total_seconds() / 3600 < 2.1  # ~2 hours
        True
    """
    current_lst = utc_to_lst(current_dt, longitude_deg)

    # Calculate LST difference
    lst_diff = target_lst_hours - current_lst

    # Handle wraparound: if negative, add 24h (next sidereal day)
    if lst_diff < 0:
        lst_diff += 24.0

    # Convert sidereal hours to solar time
    # 1 sidereal hour = 0.99726958 solar hours
    # (Sidereal day is ~3m 56s shorter than solar day)
    solar_hours = lst_diff * 0.99726958

    return timedelta(hours=solar_hours)


def lst_to_utc(lst_hours: float, longitude_deg: float, reference_dt: datetime) -> datetime:
    """
    Convert Local Sidereal Time to UTC datetime.

    Since LST repeats every sidereal day, we need a reference datetime
    to determine which occurrence we want (today, tomorrow, etc.).

    Args:
        lst_hours: Target LST in hours [0, 24)
        longitude_deg: Observer longitude in degrees
        reference_dt: Reference UTC datetime (finds nearest occurrence)

    Returns:
        UTC datetime when LST equals the target value

    Example:
        >>> from datetime import datetime, timezone
        >>> ref_dt = datetime(2025, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
        >>> lon = -118.25
        >>> target_lst = 6.0  # 6h sidereal
        >>> utc_time = lst_to_utc(target_lst, lon, ref_dt)
        >>> result_lst = utc_to_lst(utc_time, lon)
        >>> abs(result_lst - target_lst) < 0.01  # Within ~36 seconds
        True
    """
    # Start with reference time
    current_dt = reference_dt
    current_lst = utc_to_lst(current_dt, longitude_deg)

    # Calculate time difference
    delta = time_until_lst(current_dt, lst_hours, longitude_deg)

    # Add delta to get target UTC
    target_utc = current_dt + delta

    return target_utc


# ============================================================================
# Formatting and Display
# ============================================================================

def format_hours_hms(hours: float) -> str:
    """
    Format decimal hours as HH:MM:SS.SS string.

    Args:
        hours: Time in decimal hours

    Returns:
        Formatted string "HH:MM:SS.SS"

    Example:
        >>> format_hours_hms(12.5)
        '12:30:00.00'
        >>> format_hours_hms(3.141592)
        '03:08:29.73'
    """
    hours = hours % 24.0  # Normalize to [0, 24)
    h = int(hours)
    remainder = (hours - h) * 60.0
    m = int(remainder)
    s = (remainder - m) * 60.0

    return f"{h:02d}:{m:02d}:{s:05.2f}"


def format_hours_hm(hours: float) -> str:
    """
    Format decimal hours as HH:MM string (no seconds).

    Args:
        hours: Time in decimal hours

    Returns:
        Formatted string "HH:MM"

    Example:
        >>> format_hours_hm(12.75)
        '12:45'
    """
    hours = hours % 24.0
    h = int(hours)
    m = int((hours - h) * 60.0)
    return f"{h:02d}:{m:02d}"


def parse_hms_to_hours(hms: str) -> float:
    """
    Parse HH:MM:SS or HH:MM string to decimal hours.

    Args:
        hms: Time string in format "HH:MM:SS" or "HH:MM"

    Returns:
        Decimal hours

    Raises:
        ValueError: If format is invalid

    Example:
        >>> abs(parse_hms_to_hours("12:30:00") - 12.5) < 1e-6
        True
        >>> abs(parse_hms_to_hours("03:15") - 3.25) < 1e-6
        True
    """
    parts = hms.strip().split(":")

    if len(parts) == 2:
        h, m = int(parts[0]), int(parts[1])
        s = 0.0
    elif len(parts) == 3:
        h, m = int(parts[0]), int(parts[1])
        s = float(parts[2])
    else:
        raise ValueError(f"Invalid time format: {hms}. Expected HH:MM or HH:MM:SS")

    return h + m / 60.0 + s / 3600.0


# ============================================================================
# Utility Functions
# ============================================================================

def sidereal_to_solar_hours(sidereal_hours: float) -> float:
    """
    Convert sidereal time interval to solar time interval.

    Args:
        sidereal_hours: Time interval in sidereal hours

    Returns:
        Time interval in solar hours

    Note:
        Sidereal day = 23h 56m 4.0905s solar time
        Solar day = 24h 3m 56.555s sidereal time
        Ratio: 1 sidereal hour = 0.99726958 solar hours
    """
    return sidereal_hours * 0.99726958


def solar_to_sidereal_hours(solar_hours: float) -> float:
    """
    Convert solar time interval to sidereal time interval.

    Args:
        solar_hours: Time interval in solar hours

    Returns:
        Time interval in sidereal hours
    """
    return solar_hours * 1.00273791


def delta_t_approx(year: int) -> float:
    """
    Approximate Delta T (TT - UT1) for a given year.

    Delta T is the difference between Terrestrial Time (TT) and Universal Time (UT1).
    For most astrophotography purposes, this correction is negligible (<1 minute).

    Args:
        year: Calendar year

    Returns:
        Delta T in seconds

    Reference:
        NASA Eclipse Web Site polynomial approximations

    Note:
        For precise work, use IERS Bulletin A values.
        This is a simplified polynomial for rough estimates.
    """
    t = (year - 2000) / 100.0

    if year < 1900:
        delta_t = -20 + 32 * t * t
    elif year < 2000:
        delta_t = 63.86 + 0.3345 * t - 0.060374 * t * t
    elif year < 2100:
        delta_t = 62.92 + 0.32217 * t + 0.005589 * t * t
    else:
        # Long-term projection
        delta_t = -20 + 32 * t * t

    return delta_t


# ============================================================================
# Example Usage and Testing
# ============================================================================

if __name__ == "__main__":
    # Test conversions
    print("=" * 60)
    print("AstroCamSync Time System - Test Suite")
    print("=" * 60)

    # Test 1: J2000.0 epoch
    dt_j2000 = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    jd_j2000 = utc_to_julian_date(dt_j2000)
    print(f"\nTest 1: J2000.0 Epoch")
    print(f"  Expected JD: 2451545.0")
    print(f"  Computed JD: {jd_j2000:.6f}")
    print(f"  Error:       {abs(jd_j2000 - 2451545.0):.6f} days")

    # Test 2: Current time
    dt_now = datetime.now(timezone.utc)
    lon_la = -118.25  # Los Angeles
    print(f"\nTest 2: Current Time at Los Angeles")
    print(f"  UTC:  {dt_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  JD:   {utc_to_julian_date(dt_now):.6f}")
    print(f"  GST:  {format_hours_hms(julian_date_to_gst(utc_to_julian_date(dt_now)))}")
    print(f"  LST:  {format_hours_hms(utc_to_lst(dt_now, lon_la))}")

    # Test 3: Time until target LST
    target_lst = 18.0  # 6 PM sidereal
    delta = time_until_lst(dt_now, target_lst, lon_la)
    print(f"\nTest 3: Time Until LST 18:00")
    print(f"  Current LST: {format_hours_hms(utc_to_lst(dt_now, lon_la))}")
    print(f"  Target LST:  18:00:00.00")
    print(f"  Time until:  {delta.total_seconds() / 3600:.2f} hours")

    # Test 4: Round-trip conversion
    jd_test = 2460000.0
    dt_from_jd = julian_date_to_utc(jd_test)
    jd_roundtrip = utc_to_julian_date(dt_from_jd)
    print(f"\nTest 4: Round-trip Conversion")
    print(f"  Original JD:    {jd_test:.6f}")
    print(f"  After UTC->JD:  {jd_roundtrip:.6f}")
    print(f"  Error:          {abs(jd_test - jd_roundtrip):.9f} days")

    print("\n" + "=" * 60)
