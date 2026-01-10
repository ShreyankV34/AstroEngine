# AstroEngine Implementation Design
## NASA-Grade Architecture for Missing Critical Components

**Date**: 2026-01-10
**Status**: Design Phase
**Author**: Claude (AI Architecture Review)

---

## EXECUTIVE SUMMARY

AstroEngine currently has **excellent physics foundations** (60% complete) but is missing **three critical components** that block end-to-end functionality:

1. **Decision Fusion Engine** (`sync/fusion.py`) - The "brain" that makes shootability decisions
2. **Deep-Sky Object Catalog** (`targets/catalogs.py`) - The "memory" of what to photograph
3. **Weather Integration** (`conditions/weather.py`) - The "senses" for environmental awareness

This document provides **deterministic, physics-based architecture** for implementing these modules at production quality.

---

## 1. DECISION FUSION ENGINE (`sync/fusion.py`)

### Purpose
Integrate all physics modules into a **single decision engine** that returns:
- `shootable: bool` - Can this shot succeed?
- `quality: str` - excellent/good/fair/poor/impossible
- `confidence: float` - 0.0-1.0 based on data quality
- `settings: ExposureSettings` - Optimal camera configuration
- `predictions: dict` - SNR, trailing, dynamic range
- `warnings: list[str]` - Human-readable issues
- `tips: list[str]` - Optimization suggestions

### Architecture

```python
@dataclass
class DecisionInput:
    """Complete state of the universe for this shot"""
    # Target
    target_name: str
    target_ra: float
    target_dec: float
    target_surface_brightness: float
    target_size_arcmin: float
    target_type: str  # emission/reflection/planetary/galaxy/etc

    # Observer
    latitude: float
    longitude: float
    altitude_m: float
    time_utc: datetime

    # Camera
    camera_model: str
    focal_length_mm: float
    aperture_f_number: float
    filter_type: Optional[str]  # None/UHC/Ha/OIII/etc

    # Conditions
    sky_brightness: float  # mag/arcsec²
    bortle_class: int
    cloud_cover_percent: float
    humidity_percent: float
    temperature_c: float
    wind_speed_ms: float
    seeing_arcsec: float
    transparency_mag: float  # extinction
    moon_illumination: float
    moon_altitude: float

    # Hardware
    tracking: bool
    max_exposure_s: Optional[float]  # User constraint
    target_snr: Optional[float]  # User goal

    # Metadata
    data_quality: float  # From realtime.py
    data_sources: dict  # Which sensors provided data


@dataclass
class Decision:
    """Complete decision output with full traceability"""
    # Verdict
    shootable: bool
    quality: str  # excellent/good/fair/poor/impossible
    confidence: float  # 0.0-1.0
    reason: str  # Primary decision reason

    # Settings
    settings: ExposureSettings

    # Predictions (what will happen if you take this shot)
    predicted_snr: float
    predicted_star_trailing_px: float
    predicted_star_trailing_arcsec: float
    predicted_dynamic_range: float
    saturation_risk: str  # none/low/medium/high

    # Target visibility
    target_altitude: float
    target_azimuth: float
    target_hour_angle: float
    target_airmass: float
    target_rise_time: Optional[datetime]
    target_set_time: Optional[datetime]
    time_until_set: Optional[timedelta]

    # Sky conditions assessment
    sky_contrast: float  # target_brightness - sky_brightness
    effective_surface_brightness: float  # After light pollution
    moon_interference: str  # none/low/medium/high/severe

    # Warnings (things that reduce quality)
    warnings: list[str]

    # Tips (things user can do to improve)
    tips: list[str]

    # Traceability (physics audit trail)
    physics_trace: dict

    # Alternatives
    better_time: Optional[datetime]  # When conditions improve
    better_target: Optional[str]  # If this target is impossible


def fuse_decision(input: DecisionInput) -> Decision:
    """
    Main decision engine.

    Decision Logic Flow:
    1. Coordinate Transform (RA/Dec → Alt/Az)
    2. Visibility Check (altitude > 15°, airmass < 3.0)
    3. Weather Assessment (clouds, wind, humidity)
    4. Target-Sky Contrast (can we see it?)
    5. Camera Optimization (exposure, ISO, tracking)
    6. Physics Predictions (SNR, trailing, saturation)
    7. Quality Scoring (excellent/good/fair/poor/impossible)
    8. Warning Generation (what's wrong)
    9. Tip Generation (how to improve)
    10. Return Decision
    """
    pass  # Implementation below
```

### Decision Logic (Deterministic)

#### Step 1: Coordinate Transform
```python
# Use core/time.py and core/coordinates.py
jd = utc_to_julian_date(input.time_utc)
gst = julian_date_to_gst(jd)
lst = gst_to_lst(gst, input.longitude)
ha = ra_to_hour_angle(input.target_ra, lst)
alt, az = equatorial_to_horizontal(
    input.target_ra, input.target_dec,
    input.latitude, ha
)
airmass = calculate_airmass(alt)
```

#### Step 2: Visibility Gating
```python
if alt < 15.0:
    return Decision(
        shootable=False,
        quality="impossible",
        confidence=1.0,
        reason=f"Target is below horizon (altitude={alt:.1f}°)",
        warnings=["Target not visible"],
        tips=["Wait for target to rise", "Choose different target"]
    )

if airmass > 3.0:
    warnings.append(f"High airmass ({airmass:.1f}×) - significant extinction")
    quality_penalty += 0.2
```

#### Step 3: Weather Gating
```python
# Cloud cover
if input.cloud_cover_percent > 70:
    return Decision(shootable=False, quality="impossible",
                   reason="Heavy cloud cover")
elif input.cloud_cover_percent > 40:
    warnings.append(f"Moderate clouds ({input.cloud_cover_percent:.0f}%)")
    quality_penalty += 0.15

# Wind (tracking precision degradation)
if input.wind_speed_ms > 10.0:
    warnings.append(f"High wind ({input.wind_speed_ms:.1f} m/s) - tracking errors likely")
    quality_penalty += 0.1

# Humidity (dew risk)
if input.humidity_percent > 85:
    warnings.append(f"High humidity ({input.humidity_percent:.0f}%) - dew risk")
    tips.append("Use dew heater on optics")

# Seeing
if input.seeing_arcsec > 4.0:
    warnings.append(f"Poor seeing ({input.seeing_arcsec:.1f}\" FWHM)")
    quality_penalty += 0.1
```

#### Step 4: Target-Sky Contrast Analysis
```python
# From conditions/light_pollution
contrast = input.target_surface_brightness - input.sky_brightness

# Detect-ability thresholds (empirical from astrophotography)
if contrast < 1.0:
    return Decision(shootable=False, quality="impossible",
                   reason=f"Target too dim for sky brightness (contrast={contrast:.1f} mag)")
elif contrast < 2.0:
    warnings.append("Very low contrast - target barely visible")
    quality_penalty += 0.3
elif contrast < 3.0:
    warnings.append("Low contrast - challenging target")
    quality_penalty += 0.15
```

#### Step 5: Moon Interference
```python
# Moon brightness impact
if input.moon_illumination > 0.7 and input.moon_altitude > 20:
    moon_sky_brightness_increase = 2.0 * input.moon_illumination
    effective_sky_brightness = input.sky_brightness - moon_sky_brightness_increase
    warnings.append(f"Bright moon ({input.moon_illumination*100:.0f}% illuminated)")
    quality_penalty += 0.2

    if input.target_type in ["emission", "narrowband"]:
        tips.append("Consider narrowband filter (moon less impactful)")
```

#### Step 6: Camera Optimization
```python
# Get camera from database
from ..cameras.database import get_camera
from ..cameras.sensors import SensorPhysics
from ..core.engine import recommend_settings

camera = get_camera(input.camera_model)
sensor = SensorPhysics(
    pixel_pitch_um=camera.pixel_pitch_um,
    sensor_width_mm=camera.sensor_width_mm,
    sensor_height_mm=camera.sensor_height_mm,
    read_noise_e=camera.read_noise_e,
    full_well_capacity_e=calculate_full_well_capacity(camera.pixel_pitch_um),
    iso_invariance_point=camera.iso_invariance_point
)

# Calculate optimal settings
settings = recommend_settings(
    target_ra=input.target_ra,
    target_dec=input.target_dec,
    target_magnitude=input.target_surface_brightness,
    latitude=input.latitude,
    longitude=input.longitude,
    time_utc=input.time_utc,
    camera_pixel_pitch_um=sensor.pixel_pitch_um,
    focal_length_mm=input.focal_length_mm,
    aperture=input.aperture_f_number,
    sky_brightness=effective_sky_brightness,
    tracking=input.tracking,
    iso_invariance_point=sensor.iso_invariance_point
)
```

#### Step 7: Physics Predictions
```python
# SNR calculation with real sensor model
from ..cameras.sensors import (
    calculate_read_noise_at_iso,
    calculate_dark_current,
    calculate_saturation_capacity
)

read_noise = calculate_read_noise_at_iso(
    sensor.read_noise_e,
    settings.iso,
    sensor.iso_invariance_point
)

dark_current_e = calculate_dark_current(
    sensor.dark_current_e_per_s,
    input.temperature_c,
    settings.exposure_time
)

# Signal estimation (needs proper photon flux calculation)
# TODO: Integrate with proper quantum efficiency and filter transmission
signal_e = estimate_signal_electrons(
    target_surface_brightness=input.target_surface_brightness,
    sky_brightness=effective_sky_brightness,
    exposure_time=settings.exposure_time,
    aperture_mm=input.focal_length_mm / input.aperture_f_number,
    pixel_solid_angle=sensor.pixel_solid_angle,
    quantum_efficiency=estimate_quantum_efficiency(500)  # nm
)

sky_noise_e = estimate_sky_background_electrons(
    sky_brightness=effective_sky_brightness,
    exposure_time=settings.exposure_time,
    pixel_solid_angle=sensor.pixel_solid_angle
)

# Total SNR
predicted_snr = signal_e / math.sqrt(
    signal_e + read_noise**2 + dark_current_e + sky_noise_e
)

# Star trailing
from ..core.astronomy import calculate_star_trailing
trailing_arcsec, trailing_px = calculate_star_trailing(
    input.target_dec,
    input.focal_length_mm,
    sensor.pixel_pitch_um,
    settings.exposure_time,
    input.tracking
)

# Saturation check
saturation_capacity = calculate_saturation_capacity(
    sensor.full_well_capacity_e,
    settings.iso
)

saturation_fraction = signal_e / saturation_capacity
if saturation_fraction > 0.9:
    saturation_risk = "high"
    warnings.append("Signal approaching saturation - reduce exposure")
elif saturation_fraction > 0.7:
    saturation_risk = "medium"
    warnings.append("Signal approaching 70% capacity")
else:
    saturation_risk = "none"
```

#### Step 8: Quality Scoring
```python
# Start with perfect score
quality_score = 1.0 - quality_penalty

# SNR-based quality
if predicted_snr < 3.0:
    quality = "poor"
    warnings.append(f"Low SNR ({predicted_snr:.1f})")
elif predicted_snr < 5.0:
    quality = "fair"
elif predicted_snr < 10.0:
    quality = "good"
else:
    quality = "excellent"

# Degrade quality if trailing excessive
if not input.tracking and trailing_px > 2.0:
    quality = min(quality, "fair")
    warnings.append(f"Significant star trailing ({trailing_px:.1f} px)")

# Final shootable decision
shootable = (quality != "impossible" and
             quality_score > 0.3 and
             predicted_snr > 2.0)
```

#### Step 9: Tip Generation
```python
tips = []

# ISO optimization
if settings.iso < sensor.iso_invariance_point:
    tips.append(f"Increase ISO to {sensor.iso_invariance_point} (invariance point)")

# Tracking recommendation
if not input.tracking and settings.exposure_time > 10:
    tips.append("Enable tracking for longer exposures")

# Timing optimization
if airmass > 2.0:
    tips.append("Wait for target to reach higher altitude")

# Light pollution mitigation
if input.bortle_class >= 6 and input.target_type == "emission":
    tips.append("Use light pollution filter (UHC or narrowband)")

# Stacking suggestion
if predicted_snr < 10:
    frames_needed = int((10 / predicted_snr) ** 2)
    tips.append(f"Stack {frames_needed}+ frames for SNR~10")
```

#### Step 10: Physics Audit Trail
```python
physics_trace = {
    "coordinate_transform": {
        "jd": jd,
        "gst": gst,
        "lst": lst,
        "hour_angle": ha,
        "altitude": alt,
        "azimuth": az,
        "airmass": airmass
    },
    "sensor_model": {
        "read_noise_e": read_noise,
        "dark_current_e": dark_current_e,
        "saturation_capacity_e": saturation_capacity,
        "iso_invariance_point": sensor.iso_invariance_point
    },
    "signal_chain": {
        "signal_e": signal_e,
        "shot_noise_e": math.sqrt(signal_e),
        "read_noise_e": read_noise,
        "dark_noise_e": math.sqrt(dark_current_e),
        "sky_noise_e": math.sqrt(sky_noise_e),
        "total_noise_e": math.sqrt(signal_e + read_noise**2 + dark_current_e + sky_noise_e),
        "snr": predicted_snr
    },
    "star_trailing": {
        "trailing_arcsec": trailing_arcsec,
        "trailing_px": trailing_px,
        "npf_limit_s": npf_limit
    },
    "quality_factors": {
        "base_score": 1.0,
        "weather_penalty": weather_penalty,
        "contrast_penalty": contrast_penalty,
        "airmass_penalty": airmass_penalty,
        "final_score": quality_score
    }
}
```

### Confidence Calculation
```python
# Confidence based on data quality
confidence = input.data_quality / 100.0

# Reduce confidence if missing critical data
if not input.data_sources.get("weather_api"):
    confidence *= 0.8  # No live weather
if not input.data_sources.get("sqm_sensor"):
    confidence *= 0.9  # No SQM (using Bortle)
if not input.data_sources.get("gps"):
    confidence *= 0.95  # Manual location

# Clamp to [0, 1]
confidence = max(0.0, min(1.0, confidence))
```

---

## 2. DEEP-SKY OBJECT CATALOG (`targets/catalogs.py`)

### Purpose
Provide **curated, physics-accurate target database** for decision engine.

### Data Structure
```python
@dataclass
class DeepSkyObject:
    """Complete specification of an astrophotography target"""
    # Identity
    name: str
    common_name: Optional[str]
    catalog_id: str  # M31, NGC224, IC342, etc
    aliases: list[str]

    # Coordinates (J2000.0)
    ra_hours: float  # 0-24
    dec_degrees: float  # -90 to +90

    # Photometry
    surface_brightness: float  # mag/arcsec²
    integrated_magnitude: float  # Total brightness

    # Physical properties
    angular_size_arcmin: float  # Major axis
    angular_size_minor_arcmin: Optional[float]
    position_angle_deg: Optional[float]

    # Classification
    object_type: str  # galaxy/nebula/cluster/planetary_nebula/etc
    emission_type: Optional[str]  # H-alpha/OIII/continuum/mixed

    # Observability
    best_months: list[int]  # 1-12
    minimum_aperture_mm: Optional[float]
    minimum_focal_length_mm: Optional[float]
    difficulty: str  # easy/moderate/challenging/extreme

    # Imaging guidance
    recommended_exposure_s: float
    recommended_filters: list[str]
    recommended_focal_ratio: str  # "f/4-f/6" etc
    stacking_minimum: int  # Minimum frames for good SNR

    # Notes
    description: str
    imaging_notes: Optional[str]
```

### Catalogs to Include

#### Messier Catalog (110 objects)
**Priority**: Highest - Most popular targets

Data sources:
- SIMBAD (CDS Strasbourg) for accurate coordinates
- Observational photometry from literature
- Surface brightness from amateur photometry databases

Example entries:
```python
MESSIER_CATALOG = {
    "M31": DeepSkyObject(
        name="M31",
        common_name="Andromeda Galaxy",
        catalog_id="M31",
        aliases=["NGC224", "Andromeda"],
        ra_hours=0.712,  # 00h 42m 44s
        dec_degrees=41.269,  # +41° 16' 9"
        surface_brightness=13.5,  # mag/arcsec²
        integrated_magnitude=3.4,
        angular_size_arcmin=178.0,
        angular_size_minor_arcmin=63.0,
        object_type="galaxy",
        emission_type="continuum",
        best_months=[9, 10, 11, 12, 1],
        minimum_aperture_mm=50,
        minimum_focal_length_mm=100,
        difficulty="easy",
        recommended_exposure_s=120,
        recommended_filters=["None", "light_pollution"],
        recommended_focal_ratio="f/3-f/5",
        stacking_minimum=30,
        description="Nearest major galaxy, 2.5 million light-years distant",
        imaging_notes="Wide field required, dust lanes visible with narrowband"
    ),

    "M42": DeepSkyObject(
        name="M42",
        common_name="Orion Nebula",
        catalog_id="M42",
        aliases=["NGC1976", "Orion Nebula"],
        ra_hours=5.588,  # 05h 35m 17s
        dec_degrees=-5.391,  # -05° 23' 28"
        surface_brightness=17.0,  # mag/arcsec²
        integrated_magnitude=4.0,
        angular_size_arcmin=65.0,
        object_type="nebula",
        emission_type="H-alpha",
        best_months=[11, 12, 1, 2, 3],
        minimum_aperture_mm=50,
        minimum_focal_length_mm=200,
        difficulty="easy",
        recommended_exposure_s=60,
        recommended_filters=["None", "UHC", "H-alpha"],
        recommended_focal_ratio="f/4-f/8",
        stacking_minimum=20,
        description="Stellar nursery in Orion's sword",
        imaging_notes="Bright core requires HDR technique"
    )
}
```

#### NGC Popular Targets (~50 objects)
- Bright galaxies (NGC253, NGC2403, NGC4565, etc.)
- Emission nebulae (NGC7000 North America, NGC1499 California, etc.)
- Planetary nebulae (NGC7293 Helix, NGC6543 Cat's Eye, etc.)

#### Caldwell Catalog (109 objects)
- Supplement to Messier for southern hemisphere targets

#### Milky Way Regions (~20 entries)
```python
"MW_SAGITTARIUS": DeepSkyObject(
    name="Milky Way - Sagittarius",
    common_name="Galactic Core",
    catalog_id="MW_SAG",
    ra_hours=17.76,  # Sgr A*
    dec_degrees=-29.0,
    surface_brightness=18.0,  # Varies wildly
    object_type="milky_way",
    best_months=[5, 6, 7, 8],
    difficulty="easy",
    recommended_exposure_s=30,
    description="Densest star fields, galactic center"
)
```

### Search Interface
```python
def get_target(identifier: str) -> Optional[DeepSkyObject]:
    """Get target by name/ID with fuzzy matching"""
    # Search: M31, Andromeda, NGC 224, etc
    pass

def search_targets(
    object_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    month: Optional[int] = None,
    min_surface_brightness: Optional[float] = None,
    max_surface_brightness: Optional[float] = None,
    declination_range: Optional[tuple[float, float]] = None
) -> list[DeepSkyObject]:
    """Filter catalog by criteria"""
    pass

def get_visible_now(
    latitude: float,
    longitude: float,
    time_utc: datetime,
    min_altitude: float = 30.0
) -> list[DeepSkyObject]:
    """Return targets currently above horizon"""
    pass

def get_best_target_for_conditions(
    latitude: float,
    longitude: float,
    time_utc: datetime,
    sky_brightness: float,
    bortle: int,
    camera_model: str,
    focal_length: float
) -> Optional[DeepSkyObject]:
    """AI-assisted target selection"""
    pass
```

### Data Sources
- **SIMBAD** (Strasbourg astronomical database)
- **OpenNGC** (open-source NGC/IC catalog)
- **Messier Database** (verified amateur data)
- **Literature** (surface brightness photometry papers)

---

## 3. WEATHER INTEGRATION (`conditions/weather.py`)

### Purpose
Provide **real-time, astronomy-specific weather data** for decision engine.

### Data Structure
```python
@dataclass
class AstronomicalWeather:
    """Complete environmental state for astrophotography"""
    # Basic weather
    cloud_cover_percent: float
    humidity_percent: float
    temperature_c: float
    wind_speed_ms: float
    wind_direction_deg: float
    pressure_hpa: float
    dew_point_c: float

    # Sky conditions
    sky_clarity: str  # clear/partly_cloudy/cloudy/overcast
    precipitation: bool
    precipitation_type: Optional[str]  # rain/snow/sleet

    # Astronomical conditions
    seeing_estimate_arcsec: float  # From temperature gradient
    transparency_estimate: float  # From humidity/aerosols

    # Moon
    moon_phase: float  # 0-1
    moon_illumination: float  # 0-1
    moon_altitude: float  # degrees
    moon_azimuth: float  # degrees

    # Sun
    sun_altitude: float
    sun_azimuth: float
    astronomical_twilight: bool
    civil_twilight: bool
    nautical_twilight: bool

    # Metadata
    timestamp: datetime
    source: str  # "OpenWeatherMap" etc
    forecast: bool  # True if forecast, False if current
    forecast_hours: Optional[int]
```

### API Integration

#### OpenWeatherMap (Free tier: 1000 calls/day)
```python
def get_weather_from_openweathermap(
    lat: float,
    lon: float,
    api_key: str
) -> AstronomicalWeather:
    """
    Fetch current weather from OpenWeatherMap.

    API: https://api.openweathermap.org/data/2.5/weather
    Response includes: temp, humidity, clouds, wind, pressure
    """
    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric"
    }
    response = requests.get(url, params=params)
    data = response.json()

    # Parse response
    weather = AstronomicalWeather(
        cloud_cover_percent=data["clouds"]["all"],
        humidity_percent=data["main"]["humidity"],
        temperature_c=data["main"]["temp"],
        wind_speed_ms=data["wind"]["speed"],
        wind_direction_deg=data["wind"]["deg"],
        pressure_hpa=data["main"]["pressure"],
        dew_point_c=calculate_dew_point(
            data["main"]["temp"],
            data["main"]["humidity"]
        ),
        timestamp=datetime.utcnow(),
        source="OpenWeatherMap",
        forecast=False
    )

    return weather
```

#### Weather.gov (US only, no API key required)
```python
def get_weather_from_weathergov(
    lat: float,
    lon: float
) -> AstronomicalWeather:
    """
    Fetch weather from NOAA Weather.gov API (US only).

    API: https://api.weather.gov/points/{lat},{lon}
    Higher quality than OpenWeatherMap in US
    """
    # Get grid coordinates
    points_url = f"https://api.weather.gov/points/{lat},{lon}"
    # Then get forecast from grid endpoint
    pass
```

### Astronomical Calculations

#### Dew Point
```python
def calculate_dew_point(temp_c: float, humidity_percent: float) -> float:
    """
    Magnus formula for dew point.
    Critical for optics fogging prediction.
    """
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity_percent / 100.0)
    dew_point = (b * alpha) / (a - alpha)
    return dew_point
```

#### Seeing Estimation
```python
def estimate_seeing_from_weather(
    temperature_c: float,
    wind_speed_ms: float,
    altitude_m: float
) -> float:
    """
    Empirical seeing estimation from weather parameters.
    Not as accurate as actual seeing monitor, but reasonable.

    Based on:
    - Temperature gradient (turbulence)
    - Wind speed (atmospheric mixing)
    - Altitude (less atmosphere above)
    """
    base_seeing = 2.0  # arcsec at sea level, calm

    # Wind penalty (turbulence)
    wind_factor = 1.0 + (wind_speed_ms / 10.0) * 0.5

    # Temperature penalty (day vs night)
    # Warmer = worse seeing (thermal gradients)
    temp_factor = 1.0 + max(0, (temperature_c - 10) / 20.0)

    # Altitude bonus
    altitude_factor = 1.0 - (altitude_m / 5000.0) * 0.3

    seeing = base_seeing * wind_factor * temp_factor * altitude_factor
    return max(0.5, min(10.0, seeing))  # Clamp 0.5-10 arcsec
```

#### Astronomical Twilight
```python
def calculate_twilight_times(
    lat: float,
    lon: float,
    date: datetime
) -> dict:
    """
    Calculate sunrise, sunset, and twilight times.

    Twilight definitions (sun altitude):
    - Civil: -6°
    - Nautical: -12°
    - Astronomical: -18°

    For astrophotography: need astronomical twilight (sun < -18°)
    """
    # Use astropy for high accuracy
    from astropy.time import Time
    from astropy.coordinates import EarthLocation, get_sun

    location = EarthLocation(lat=lat*u.deg, lon=lon*u.deg)
    # Calculate sun altitude throughout night
    # Find times when sun crosses -18° altitude
    pass
```

#### Moon Position & Phase
```python
def calculate_moon_position(
    lat: float,
    lon: float,
    time_utc: datetime
) -> tuple[float, float, float, float]:
    """
    Calculate moon altitude, azimuth, phase, illumination.

    Uses simplified lunar theory (accurate to ~0.5°)
    For NASA-grade: use astropy or SPICE kernels
    """
    # Could use astropy.coordinates.get_moon()
    # Or implement simplified lunar theory
    pass
```

### Integration with Existing Modules
```python
def get_astronomical_weather(
    lat: float,
    lon: float,
    api_key: Optional[str] = None
) -> AstronomicalWeather:
    """
    Main entry point - attempts multiple sources in priority order.

    Priority:
    1. Weather.gov (if US location)
    2. OpenWeatherMap (if API key provided)
    3. Default assumptions (conservative)
    """
    # Try Weather.gov first (US only, more accurate)
    if is_us_location(lat, lon):
        try:
            return get_weather_from_weathergov(lat, lon)
        except Exception:
            pass

    # Try OpenWeatherMap
    if api_key:
        try:
            return get_weather_from_openweathermap(lat, lon, api_key)
        except Exception:
            pass

    # Return conservative defaults
    return get_default_weather(lat, lon)
```

---

## 4. INTEGRATION IMPROVEMENTS

### Problem: `engine.py` doesn't use `sensors.py`
Currently `engine.py` has simplified noise models. Should import from `sensors.py`:

```python
# engine.py - BEFORE (simplified)
def calculate_snr(...):
    read_noise_e = 5.0  # Hardcoded!
    dark_current_e = exposure * 0.1  # Oversimplified!

# engine.py - AFTER (integrated)
from ..cameras.sensors import (
    calculate_read_noise_at_iso,
    calculate_dark_current,
    calculate_saturation_capacity
)
from ..cameras.database import get_camera

def calculate_snr(...):
    camera = get_camera(camera_model)
    read_noise_e = calculate_read_noise_at_iso(
        camera.read_noise_e,
        iso,
        camera.iso_invariance_point
    )
    dark_current_e = calculate_dark_current(
        camera.dark_current_e_per_s,
        temperature_c,
        exposure
    )
```

### Problem: No signal photon flux calculation
Need proper photon flux model:

```python
def calculate_photon_flux(
    magnitude: float,
    exposure_time: float,
    aperture_diameter_mm: float,
    quantum_efficiency: float,
    atmospheric_extinction: float
) -> float:
    """
    Calculate photoelectrons from astronomical target.

    Based on Pogson's ratio: 100^0.2 = 2.512
    Zero-point flux: Vega at V=0 gives 1000 photons/s/cm²/Å
    """
    # Zero-point flux for V=0 star (Vega)
    zero_point_flux = 1000  # photons/s/cm²/Å at top of atmosphere

    # Adjust for magnitude (2.512x per magnitude)
    flux_factor = 10 ** (-magnitude / 2.5)

    # Aperture area
    aperture_area_cm2 = math.pi * (aperture_diameter_mm / 20) ** 2

    # Atmospheric extinction
    transmission = 10 ** (-atmospheric_extinction / 2.5)

    # Total photoelectrons
    photons = (zero_point_flux * flux_factor * aperture_area_cm2 *
               exposure_time * quantum_efficiency * transmission)

    return photons
```

---

## 5. TEST SUITE DESIGN

### Critical Tests Needed

#### Physics Validation
```python
# tests/test_coordinates.py
def test_coordinate_transform_against_usno():
    """Validate against US Naval Observatory data"""
    # M31 on 2026-01-10 12:00 UTC from Greenwich
    # Expected: alt=XX.XX°, az=YYY.YY° (from USNO MICA)
    pass

def test_airmass_calculation():
    """Validate Rozenberg formula"""
    assert calculate_airmass(90) == 1.0  # Zenith
    assert calculate_airmass(30) == pytest.approx(2.0, rel=0.05)
    assert calculate_airmass(10) == pytest.approx(5.6, rel=0.1)
```

#### Sensor Physics
```python
# tests/test_sensors.py
def test_iso_invariance():
    """Test read noise behavior at ISO invariance point"""
    # Below invariance: noise scales with ISO
    # Above invariance: noise constant
    pass

def test_dark_current_doubling():
    """Validate 6.3°C doubling time"""
    # At 20°C: X e-/s
    # At 26.3°C: 2X e-/s
    pass
```

#### Decision Logic
```python
# tests/test_fusion.py
def test_decision_shootable():
    """Test shootability gating"""
    # Below horizon → not shootable
    # Clouds > 70% → not shootable
    # SNR < 2 → not shootable
    pass

def test_decision_quality():
    """Test quality scoring"""
    # SNR 15, clear sky → excellent
    # SNR 5, clouds → fair
    # SNR 2 → poor
    pass
```

---

## 6. IMPLEMENTATION PRIORITY

### Phase 1: Critical Path (Week 1)
1. ✅ `sync/fusion.py` - Decision engine (2 days)
2. ✅ `targets/catalogs.py` - Messier catalog only (1 day)
3. ✅ `conditions/weather.py` - OpenWeatherMap integration (1 day)
4. ✅ Integration: engine.py → sensors.py (1 day)
5. ✅ Fix CLI broken imports (1 day)

**Deliverable**: Working end-to-end pipeline

### Phase 2: Validation (Week 2)
1. ✅ Test suite (physics validation)
2. ✅ Known-solution tests (M31 on specific date)
3. ✅ Edge case handling
4. ✅ Error message quality

**Deliverable**: Validated, trustworthy calculations

### Phase 3: Expansion (Week 3-4)
1. ✅ NGC/IC catalog (~50 popular targets)
2. ✅ Caldwell catalog
3. ✅ Milky Way regions
4. ✅ Weather.gov integration (US)
5. ✅ Configuration file support
6. ✅ Logging infrastructure

**Deliverable**: Production-ready tool

### Phase 4: Advanced Features (Month 2+)
1. Session planning (multi-target scheduling)
2. Filter support (Ha, OIII, light pollution filters)
3. Stacking optimization
4. Mobile app development
5. Hardware integration (GPS, SQM, weather stations)

---

## 7. NASA-GRADE QUALITY CHECKLIST

For each module, ensure:

- [ ] **Deterministic**: Same inputs → same outputs
- [ ] **Traceable**: Every decision has physics audit trail
- [ ] **Validated**: Tests against known solutions (USNO, literature)
- [ ] **Documented**: Docstrings cite sources (papers, formulas)
- [ ] **Error-handled**: Graceful degradation, informative errors
- [ ] **Type-safe**: Dataclasses, type hints, validation
- [ ] **Modular**: Clean interfaces, no circular dependencies
- [ ] **Configurable**: No hardcoded magic numbers
- [ ] **Logged**: Decision rationale recorded
- [ ] **Tested**: Unit tests, integration tests, edge cases

---

## 8. SUCCESS CRITERIA

### Minimal Viable Product
- User provides: target name, location, time
- System returns: shootable yes/no, optimal settings, predictions
- Confidence: ≥90% match to manual expert calculations

### Production Quality
- Test coverage: ≥80% of physics code
- Coordinate accuracy: <1 arcmin error
- SNR prediction: ±20% of measured values
- Decision reliability: <5% false positives (says shootable when not)

### NASA-Grade
- Full traceability: every decision justified
- Validation: tested against professional planning tools (TheSkyX, SkySafari)
- Documentation: publishable methods (could write paper on algorithms)
- Robustness: handles all edge cases gracefully

---

## APPENDICES

### A. Coordinate System Conventions
- RA: 0-24 hours (0h = vernal equinox)
- Dec: -90° to +90° (0° = celestial equator)
- Epoch: J2000.0 unless noted
- Alt/Az: Altitude 0-90°, Azimuth 0-360° (0° = North, 90° = East)

### B. Photometric Conventions
- Magnitudes: Vega system (V=0 for Vega)
- Surface brightness: mag/arcsec²
- Sky brightness: mag/arcsec² (darker sky = higher number)
- Contrast: target_brightness - sky_brightness (larger = better)

### C. Physics References
- Jean Meeus, "Astronomical Algorithms" (1998) - Time/coordinate transforms
- Rozenberg (1966) - Airmass formula
- Frédéric Michelet (2010) - NPF rule
- Pogson's ratio: 100^0.2 = 2.512 - Magnitude scale

### D. Data Sources
- SIMBAD: http://simbad.u-strasbg.fr/simbad/
- OpenNGC: https://github.com/mattiaverga/OpenNGC
- USNO MICA: https://aa.usno.navy.mil/data/
- OpenWeatherMap: https://openweathermap.org/api
- Weather.gov: https://www.weather.gov/documentation/services-web-api

---

**END OF DESIGN DOCUMENT**
