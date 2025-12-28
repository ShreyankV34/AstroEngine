"""
Astronomical time conversions.

Handles UTC -> JD -> GST -> LST transformations.
Based on Jean Meeus "Astronomical Algorithms" (1998).
"""
from datetime import datetime, timezone
import math


def utc_to_julian_date(dt: datetime) -> float:
    """
    Convert UTC datetime to Julian Date.
    
    Args:
        dt: UTC datetime object
        
    Returns:
        Julian Date (float)
        
    Reference:
        Meeus, "Astronomical Algorithms", Chapter 7
    """
    # Ensure UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour
    minute = dt.minute
    second = dt.second + dt.microsecond / 1e6
    
    # Adjust for Jan/Feb
    if month <= 2:
        year -= 1
        month += 12
    
    # Gregorian calendar correction
    a = math.floor(year / 100)
    b = 2 - a + math.floor(a / 4)
    
    # Julian Date calculation
    jd = (
        math.floor(365.25 * (year + 4716))
        + math.floor(30.6001 * (month + 1))
        + day
        + b
        - 1524.5
    )
    
    # Add time of day
    day_fraction = (hour + minute / 60 + second / 3600) / 24
    jd += day_fraction
    
    return jd


def julian_date_to_gst(jd: float) -> float:
    """
    Convert Julian Date to Greenwich Sidereal Time.
    
    Args:
        jd: Julian Date
        
    Returns:
        GST in hours [0, 24)
        
    Reference:
        Meeus, "Astronomical Algorithms", Chapter 12
    """
    # Days since J2000.0
    t = (jd - 2451545.0) / 36525.0
    
    # Mean sidereal time at 0h UT
    gst = (
        280.46061837
        + 360.98564736629 * (jd - 2451545.0)
        + 0.000387933 * t * t
        - (t * t * t) / 38710000.0
    )
    
    # Normalize to [0, 360)
    gst = gst % 360.0
    
    # Convert to hours
    gst_hours = gst / 15.0
    
    return gst_hours


def gst_to_lst(gst_hours: float, longitude_deg: float) -> float:
    """
    Convert Greenwich Sidereal Time to Local Sidereal Time.
    
    Args:
        gst_hours: GST in hours
        longitude_deg: Observer longitude in degrees (positive East)
        
    Returns:
        LST in hours [0, 24)
    """
    # Convert longitude to hours
    longitude_hours = longitude_deg / 15.0
    
    # LST = GST + longitude
    lst = gst_hours + longitude_hours
    
    # Normalize to [0, 24)
    lst = lst % 24.0
    
    return lst


def utc_to_lst(dt: datetime, longitude_deg: float) -> float:
    """
    Convert UTC datetime to Local Sidereal Time.
    
    Args:
        dt: UTC datetime
        longitude_deg: Observer longitude in degrees (positive East)
        
    Returns:
        LST in hours [0, 24)
    """
    jd = utc_to_julian_date(dt)
    gst = julian_date_to_gst(jd)
    lst = gst_to_lst(gst, longitude_deg)
    return lst


def format_time_hms(hours: float) -> str:
    """Format time in hours to HH:MM:SS string."""
    h = int(hours)
    m = int((hours - h) * 60)
    s = ((hours - h) * 60 - m) * 60
    return f"{h:02d}:{m:02d}:{s:05.2f}"


# Example usage
if __name__ == "__main__":
    # Test conversion
    dt = datetime(2025, 1, 15, 3, 0, 0, tzinfo=timezone.utc)
    lon = -118.1445  # Los Angeles
    
    jd = utc_to_julian_date(dt)
    gst = julian_date_to_gst(jd)
    lst = gst_to_lst(gst, lon)
    
    print(f"UTC: {dt}")
    print(f"JD: {jd:.6f}")
    print(f"GST: {format_time_hms(gst)}")
    print(f"LST: {format_time_hms(lst)}")