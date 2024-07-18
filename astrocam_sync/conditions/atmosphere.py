"""
Transparency and seeing models.

Models atmospheric effects on astronomical observations.
"""
import math
from typing import Dict, Tuple


def estimate_atmospheric_transparency(
    humidity: float,
    aerosol_level: str = "low",  # 'low', 'moderate', 'high'
    cloud_cover: float = 0.0  # 0-100%
) -> Dict[str, any]:
    """
    Estimate atmospheric transparency from weather conditions.
    
    Args:
        humidity: Relative humidity (0-100%)
        aerosol_level: Aerosol/particulate level
        cloud_cover: Cloud cover percentage (0-100%)
        
    Returns:
        Transparency assessment
    """
    # Base transparency (mag extinction per airmass)
    base_extinction = 0.15  # Excellent conditions
    
    # Humidity impact (water vapor absorption)
    if humidity < 30:
        humidity_penalty = 0.0
        humidity_rating = "Excellent"
    elif humidity < 50:
        humidity_penalty = 0.05
        humidity_rating = "Good"
    elif humidity < 70:
        humidity_penalty = 0.15
        humidity_rating = "Fair"
    else:
        humidity_penalty = 0.30
        humidity_rating = "Poor"
    
    # Aerosol impact
    aerosol_penalties = {
        "low": 0.0,
        "moderate": 0.10,
        "high": 0.25
    }
    aerosol_penalty = aerosol_penalties.get(aerosol_level, 0.10)
    
    # Cloud impact (any clouds significantly reduce transparency)
    if cloud_cover < 10:
        cloud_penalty = 0.0
        cloud_rating = "Clear"
    elif cloud_cover < 30:
        cloud_penalty = 0.20
        cloud_rating = "Mostly Clear"
    elif cloud_cover < 50:
        cloud_penalty = 0.50
        cloud_rating = "Partly Cloudy"
    else:
        cloud_penalty = 1.0
        cloud_rating = "Cloudy"
    
    # Total extinction
    total_extinction = base_extinction + humidity_penalty + aerosol_penalty + cloud_penalty
    
    # Overall rating
    if total_extinction < 0.20:
        overall = "Excellent"
    elif total_extinction < 0.35:
        overall = "Good"
    elif total_extinction < 0.60:
        overall = "Fair"
    else:
        overall = "Poor"
    
    return {
        "extinction_mag_per_airmass": total_extinction,
        "overall_rating": overall,
        "humidity_rating": humidity_rating,
        "aerosol_level": aerosol_level,
        "cloud_rating": cloud_rating,
        "cloud_cover": cloud_cover,
        "shootable": cloud_cover < 30 and total_extinction < 0.6
    }


def estimate_seeing(
    wind_speed_mph: float,
    temperature_stability: str = "stable",  # 'stable', 'variable', 'turbulent'
    altitude_deg: float = 45.0
) -> Dict[str, any]:
    """
    Estimate atmospheric seeing conditions.
    
    Seeing affects star sharpness - poor seeing causes "twinkling".
    
    Args:
        wind_speed_mph: Wind speed in mph
        temperature_stability: Atmospheric stability
        altitude_deg: Target altitude
        
    Returns:
        Seeing assessment
    """
    # Base seeing (arcseconds FWHM)
    # Lower is better (sharper stars)
    
    # Wind impact
    if wind_speed_mph < 5:
        wind_seeing = 1.0  # Excellent
        wind_rating = "Calm"
    elif wind_speed_mph < 15:
        wind_seeing = 2.0  # Good
        wind_rating = "Light"
    elif wind_speed_mph < 25:
        wind_seeing = 3.0  # Fair
        wind_rating = "Moderate"
    else:
        wind_seeing = 4.5  # Poor
        wind_rating = "Strong"
    
    # Temperature stability impact
    stability_factors = {
        "stable": 1.0,
        "variable": 1.5,
        "turbulent": 2.5
    }
    stability_factor = stability_factors.get(temperature_stability, 1.5)
    
    # Altitude impact (worse seeing at lower altitudes due to more atmosphere)
    altitude_factor = 1.0 / math.sin(math.radians(altitude_deg))
    altitude_factor = min(altitude_factor, 3.0)  # Cap at 3x
    
    # Total seeing
    seeing_arcsec = wind_seeing * stability_factor * (altitude_factor ** 0.5)
    
    # Rating
    if seeing_arcsec < 2.0:
        rating = "Excellent"
        quality = "Sharp stars, excellent detail"
    elif seeing_arcsec < 3.0:
        rating = "Good"
        quality = "Good star sharpness"
    elif seeing_arcsec < 4.0:
        rating = "Fair"
        quality = "Slight star bloat"
    else:
        rating = "Poor"
        quality = "Significant star bloat, reduced detail"
    
    return {
        "seeing_arcsec": round(seeing_arcsec, 1),
        "rating": rating,
        "quality": quality,
        "wind_rating": wind_rating,
        "stability": temperature_stability,
        "suitable_for_planetary": seeing_arcsec < 2.5
    }


def calculate_atmospheric_extinction(
    altitude_deg: float,
    extinction_coefficient: float = 0.20  # mag per airmass
) -> float:
    """
    Calculate magnitude loss due to atmospheric extinction.
    
    Args:
        altitude_deg: Target altitude
        extinction_coefficient: Atmospheric extinction (mag/airmass)
        
    Returns:
        Magnitude loss
    """
    # Calculate airmass
    if altitude_deg <= 0:
        return float('inf')
    
    zenith_distance = 90 - altitude_deg
    z_rad = math.radians(zenith_distance)
    
    # Rozenberg formula for airmass
    airmass = 1.0 / (math.cos(z_rad) + 0.025 * math.exp(-11 * math.cos(z_rad)))
    
    # Extinction (magnitudes lost)
    extinction = extinction_coefficient * airmass
    
    return extinction


def assess_observing_conditions(
    altitude_deg: float,
    humidity: float,
    wind_speed_mph: float,
    cloud_cover: float,
    temperature_stability: str = "stable",
    aerosol_level: str = "low"
) -> Dict[str, any]:
    """
    Comprehensive atmospheric conditions assessment.
    
    Args:
        altitude_deg: Target altitude
        humidity: Relative humidity (%)
        wind_speed_mph: Wind speed
        cloud_cover: Cloud cover (%)
        temperature_stability: 'stable', 'variable', 'turbulent'
        aerosol_level: 'low', 'moderate', 'high'
        
    Returns:
        Complete conditions assessment
    """
    transparency = estimate_atmospheric_transparency(
        humidity,
        aerosol_level,
        cloud_cover
    )
    
    seeing = estimate_seeing(
        wind_speed_mph,
        temperature_stability,
        altitude_deg
    )
    
    extinction = calculate_atmospheric_extinction(
        altitude_deg,
        transparency["extinction_mag_per_airmass"]
    )
    
    # Overall shootability
    shootable = (
        transparency["shootable"] and
        cloud_cover < 30 and
        altitude_deg > 20
    )
    
    # Confidence rating
    if shootable and seeing["rating"] in ["Excellent", "Good"]:
        confidence = 0.85
        overall = "Excellent"
    elif shootable and seeing["rating"] == "Fair":
        confidence = 0.65
        overall = "Good"
    elif shootable:
        confidence = 0.45
        overall = "Fair"
    else:
        confidence = 0.0
        overall = "Poor"
    
    return {
        "shootable": shootable,
        "overall_rating": overall,
        "confidence": confidence,
        "transparency": transparency,
        "seeing": seeing,
        "extinction_magnitude": round(extinction, 2),
        "altitude": altitude_deg,
        "recommendations": _generate_recommendations(transparency, seeing, altitude_deg)
    }


def _generate_recommendations(
    transparency: Dict,
    seeing: Dict,
    altitude: float
) -> list:
    """Generate actionable recommendations based on conditions."""
    recommendations = []
    
    if transparency["cloud_cover"] > 50:
        recommendations.append("Wait for clearer skies - cloud cover too high")
    
    if transparency["humidity_rating"] == "Poor":
        recommendations.append("High humidity - expect reduced contrast and halos")
    
    if seeing["seeing_arcsec"] > 3.0:
        recommendations.append("Poor seeing - avoid planetary imaging")
    
    if altitude < 30:
        recommendations.append(f"Target low (alt={altitude:.0f}°) - wait for higher altitude")
    
    if transparency["aerosol_level"] == "high":
        recommendations.append("High aerosol levels - expect hazy conditions")
    
    if seeing["wind_rating"] in ["Moderate", "Strong"]:
        recommendations.append("Strong winds - ensure mount stability")
    
    if not recommendations:
        recommendations.append("Conditions favorable for imaging")
    
    return recommendations


# Example usage
if __name__ == "__main__":
    print("=== Atmospheric Conditions Assessment ===\n")
    
    # Example conditions
    conditions = assess_observing_conditions(
        altitude_deg=45,
        humidity=40,
        wind_speed_mph=8,
        cloud_cover=15,
        temperature_stability="stable",
        aerosol_level="low"
    )
    
    print(f"Overall: {conditions['overall_rating']}")
    print(f"Shootable: {conditions['shootable']}")
    print(f"Confidence: {conditions['confidence']:.0%}\n")
    
    print(f"Transparency: {conditions['transparency']['overall_rating']}")
    print(f"  Extinction: {conditions['extinction_magnitude']} mag")
    print(f"  Humidity: {conditions['transparency']['humidity_rating']}")
    print(f"  Clouds: {conditions['transparency']['cloud_rating']} "
          f"({conditions['transparency']['cloud_cover']:.0f}%)\n")
    
    print(f"Seeing: {conditions['seeing']['rating']}")
    print(f"  {conditions['seeing']['seeing_arcsec']}\" FWHM")
    print(f"  {conditions['seeing']['quality']}")
    print(f"  Wind: {conditions['seeing']['wind_rating']}\n")
    
    print("Recommendations:")
    for rec in conditions['recommendations']:
        print(f"  • {rec}")