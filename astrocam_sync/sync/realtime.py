"""
Live data aggregation.

Aggregates real-time data from multiple sources:
- GPS/location
- Time systems
- Weather APIs
- SQM sensors
- User inputs
"""
from typing import Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass


@dataclass
class LiveConditions:
    """Real-time environmental conditions."""
    sky_brightness: float  # mag/arcsec²
    bortle: int
    cloud_cover: float
    humidity: float
    wind_speed: float
    temperature: float
    source: str  # 'sqm', 'api', 'manual'
    timestamp: datetime


def aggregate_location(
    gps: Optional[Tuple[float, float]] = None,
    manual_coords: Optional[Tuple[float, float]] = None
) -> Tuple[float, float]:
    """
    Aggregate location from various sources.
    
    Priority: GPS > Manual > Default
    
    Args:
        gps: GPS coordinates (lat, lon)
        manual_coords: Manually entered coordinates
        
    Returns:
        (latitude, longitude)
    """
    if gps:
        return gps
    
    if manual_coords:
        return manual_coords
    
    # Default fallback (Los Angeles)
    return (34.0522, -118.2437)


def aggregate_sky_conditions(
    sqm_reading: Optional[float] = None,
    weather_data: Optional[Dict] = None,
    manual_bortle: Optional[int] = None
) -> LiveConditions:
    """
    Aggregate sky brightness from multiple sources.
    
    Priority: SQM sensor > Weather API > Manual Bortle > Default
    
    Args:
        sqm_reading: Direct SQM measurement (mag/arcsec²)
        weather_data: Weather API data
        manual_bortle: User-provided Bortle scale
        
    Returns:
        Aggregated conditions
    """
    from ..conditions.light_pollution import bortle_to_sky_brightness, sky_brightness_to_bortle
    
    # Tier 1: Physical sensor (best)
    if sqm_reading is not None:
        bortle = sky_brightness_to_bortle(sqm_reading)
        
        # Get weather details if available
        if weather_data:
            cloud_cover = weather_data.get("cloud_cover_percent", 0)
            humidity = weather_data.get("humidity_percent", 50)
            wind_speed = weather_data.get("wind_speed_mph", 5)
            temperature = weather_data.get("temperature_celsius", 20)
        else:
            cloud_cover = 0
            humidity = 50
            wind_speed = 5
            temperature = 20
        
        return LiveConditions(
            sky_brightness=sqm_reading,
            bortle=bortle,
            cloud_cover=cloud_cover,
            humidity=humidity,
            wind_speed=wind_speed,
            temperature=temperature,
            source="sqm",
            timestamp=datetime.utcnow()
        )
    
    # Tier 2: Weather API (good)
    if weather_data:
        # Estimate sky brightness from weather
        # This is approximate - real measurements are better
        base_brightness = 19.0  # Assume moderate conditions
        
        cloud_cover = weather_data.get("cloud_cover_percent", 0)
        humidity = weather_data.get("humidity_percent", 50)
        
        # Cloud impact
        if cloud_cover > 50:
            brightness_penalty = 2.0
        elif cloud_cover > 30:
            brightness_penalty = 1.0
        else:
            brightness_penalty = 0.0
        
        sky_brightness = base_brightness - brightness_penalty
        bortle = sky_brightness_to_bortle(sky_brightness)
        
        return LiveConditions(
            sky_brightness=sky_brightness,
            bortle=bortle,
            cloud_cover=cloud_cover,
            humidity=humidity,
            wind_speed=weather_data.get("wind_speed_mph", 5),
            temperature=weather_data.get("temperature_celsius", 20),
            source="api",
            timestamp=datetime.utcnow()
        )
    
    # Tier 3: Manual Bortle (acceptable)
    if manual_bortle is not None:
        sky_brightness = bortle_to_sky_brightness(manual_bortle)
        
        return LiveConditions(
            sky_brightness=sky_brightness,
            bortle=manual_bortle,
            cloud_cover=0,
            humidity=50,
            wind_speed=5,
            temperature=20,
            source="manual",
            timestamp=datetime.utcnow()
        )
    
    # Tier 4: Default fallback
    return LiveConditions(
        sky_brightness=19.5,  # Bortle 4-5
        bortle=5,
        cloud_cover=0,
        humidity=50,
        wind_speed=5,
        temperature=20,
        source="default",
        timestamp=datetime.utcnow()
    )


def aggregate_time(
    manual_time: Optional[datetime] = None,
    use_utc: bool = True
) -> datetime:
    """
    Aggregate time from sources.
    
    Priority: Manual > System UTC > System Local
    
    Args:
        manual_time: User-provided time
        use_utc: Use UTC (recommended for astronomy)
        
    Returns:
        datetime object
    """
    if manual_time:
        return manual_time
    
    if use_utc:
        return datetime.utcnow()
    else:
        return datetime.now()


def aggregate_all(
    # Location
    gps: Optional[Tuple[float, float]] = None,
    manual_coords: Optional[Tuple[float, float]] = None,
    
    # Time
    manual_time: Optional[datetime] = None,
    
    # Sky conditions
    sqm_reading: Optional[float] = None,
    weather_data: Optional[Dict] = None,
    manual_bortle: Optional[int] = None
) -> Dict[str, any]:
    """
    Aggregate all real-time data.
    
    Args:
        gps: GPS coordinates
        manual_coords: Manual coordinates
        manual_time: Manual time
        sqm_reading: SQM measurement
        weather_data: Weather API data
        manual_bortle: Manual Bortle scale
        
    Returns:
        Complete aggregated data
    """
    location = aggregate_location(gps, manual_coords)
    time = aggregate_time(manual_time)
    conditions = aggregate_sky_conditions(sqm_reading, weather_data, manual_bortle)
    
    return {
        "location": {
            "latitude": location[0],
            "longitude": location[1]
        },
        "time": time,
        "conditions": {
            "sky_brightness": conditions.sky_brightness,
            "bortle": conditions.bortle,
            "cloud_cover": conditions.cloud_cover,
            "humidity": conditions.humidity,
            "wind_speed": conditions.wind_speed,
            "temperature": conditions.temperature,
            "source": conditions.source,
            "timestamp": conditions.timestamp
        }
    }


def get_data_quality_score(aggregated: Dict) -> Dict[str, any]:
    """
    Assess quality of aggregated data.
    
    Args:
        aggregated: Aggregated data from aggregate_all()
        
    Returns:
        Quality assessment
    """
    conditions = aggregated["conditions"]
    source = conditions["source"]
    
    # Score based on data source
    if source == "sqm":
        score = 100
        quality = "Excellent"
        description = "Direct SQM measurement - highest accuracy"
    elif source == "api":
        score = 75
        quality = "Good"
        description = "Weather API - good estimate"
    elif source == "manual":
        score = 50
        quality = "Fair"
        description = "Manual Bortle - approximate"
    else:
        score = 25
        quality = "Poor"
        description = "Default values - highly uncertain"
    
    # Time recency
    time_diff = (datetime.utcnow() - conditions["timestamp"]).seconds
    if time_diff > 600:  # 10 minutes
        score *= 0.8
        description += " (data older than 10 minutes)"
    
    return {
        "score": score,
        "quality": quality,
        "description": description,
        "source": source
    }


# Example usage
if __name__ == "__main__":
    print("=== Real-Time Data Aggregation Demo ===\n")
    
    # Scenario 1: Best case - SQM + GPS + Weather
    print("Scenario 1: Full sensor suite")
    data1 = aggregate_all(
        gps=(34.0522, -118.2437),
        sqm_reading=20.5,
        weather_data={
            "cloud_cover_percent": 10,
            "humidity_percent": 40,
            "wind_speed_mph": 8,
            "temperature_celsius": 18
        }
    )
    
    quality1 = get_data_quality_score(data1)
    
    print(f"Location: {data1['location']['latitude']:.4f}°, "
          f"{data1['location']['longitude']:.4f}°")
    print(f"Sky Brightness: {data1['conditions']['sky_brightness']:.2f} mag/arcsec²")
    print(f"Source: {data1['conditions']['source']}")
    print(f"Data Quality: {quality1['quality']} ({quality1['score']}/100)")
    print(f"  {quality1['description']}\n")
    
    # Scenario 2: Manual Bortle only
    print("Scenario 2: Manual input only")
    data2 = aggregate_all(
        manual_coords=(40.7128, -74.0060),
        manual_bortle=6
    )
    
    quality2 = get_data_quality_score(data2)
    
    print(f"Location: {data2['location']['latitude']:.4f}°, "
          f"{data2['location']['longitude']:.4f}°")
    print(f"Sky Brightness: {data2['conditions']['sky_brightness']:.2f} mag/arcsec²")
    print(f"Bortle: {data2['conditions']['bortle']}")
    print(f"Source: {data2['conditions']['source']}")
    print(f"Data Quality: {quality2['quality']} ({quality2['score']}/100)")
    print(f"  {quality2['description']}\n")
    
    # Scenario 3: Default fallback
    print("Scenario 3: No inputs (fallback)")
    data3 = aggregate_all()
    
    quality3 = get_data_quality_score(data3)
    
    print(f"Location: {data3['location']['latitude']:.4f}°, "
          f"{data3['location']['longitude']:.4f}°")
    print(f"Sky Brightness: {data3['conditions']['sky_brightness']:.2f} mag/arcsec²")
    print(f"Source: {data3['conditions']['source']}")
    print(f"Data Quality: {quality3['quality']} ({quality3['score']}/100)")
    print(f"  {quality3['description']}")