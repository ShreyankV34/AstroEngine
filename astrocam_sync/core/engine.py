"""
Exposure calculation engine.

Deterministic physics-based exposure recommendations.
"""
import math
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ExposureSettings:
    """Recommended camera settings."""
    shutter_seconds: float
    iso: int
    aperture_fstop: float
    tracking_required: bool
    predicted_snr: float
    star_trailing_pixels: float
    dynamic_range_stops: float


@dataclass
class TargetProperties:
    """Target object properties."""
    surface_brightness: float  # mag/arcsec²
    angular_size_arcmin: float
    target_type: str  # 'extended', 'point', 'moving'


@dataclass
class CameraProperties:
    """Camera sensor properties."""
    sensor_width_mm: float
    sensor_height_mm: float
    pixel_pitch_um: float
    read_noise_electrons: float
    max_iso: int
    iso_invariance_point: int


def calculate_snr(
    signal_electrons: float,
    read_noise_electrons: float,
    dark_current_electrons: float,
    sky_noise_electrons: float
) -> float:
    """
    Calculate Signal-to-Noise Ratio.
    
    SNR = Signal / sqrt(Signal + Read Noise² + Dark Current + Sky Noise)
    
    Args:
        signal_electrons: Photo-electrons from target
        read_noise_electrons: Camera read noise
        dark_current_electrons: Thermal noise
        sky_noise_electrons: Sky background noise
        
    Returns:
        SNR value
    """
    total_noise = math.sqrt(
        signal_electrons
        + read_noise_electrons**2
        + dark_current_electrons
        + sky_noise_electrons
    )
    
    if total_noise == 0:
        return 0.0
    
    snr = signal_electrons / total_noise
    return snr


def mag_to_flux(magnitude: float) -> float:
    """
    Convert magnitude to relative flux.
    
    Uses Pogson's ratio: 100^(0.2) ≈ 2.512
    
    Args:
        magnitude: Magnitude value
        
    Returns:
        Relative flux
    """
    flux = 10 ** (-0.4 * magnitude)
    return flux


def calculate_optimal_iso(
    target_brightness: float,
    sky_brightness: float,
    read_noise: float,
    max_iso: int,
    iso_invariance: int
) -> int:
    """
    Calculate optimal ISO for given conditions.
    
    Args:
        target_brightness: Target surface brightness (mag/arcsec²)
        sky_brightness: Sky brightness (mag/arcsec²)
        read_noise: Camera read noise at base ISO
        max_iso: Maximum usable ISO
        iso_invariance: ISO where sensor becomes invariant
        
    Returns:
        Recommended ISO
    """
    # Contrast between target and sky
    contrast = sky_brightness - target_brightness
    
    # For dim targets in bright skies, use higher ISO
    if contrast < 2:
        # Sky-limited: maximize signal
        return min(max_iso, iso_invariance * 2)
    elif contrast < 4:
        # Balanced
        return iso_invariance
    else:
        # Read noise limited: use base ISO
        return min(800, iso_invariance // 2)


def calculate_exposure_time(
    target_brightness: float,
    focal_length_mm: float,
    aperture_fstop: float,
    pixel_pitch_um: float,
    dec_deg: float,
    allow_tracking: bool = False
) -> Tuple[float, bool]:
    """
    Calculate optimal exposure time.
    
    Args:
        target_brightness: Surface brightness (mag/arcsec²)
        focal_length_mm: Focal length
        aperture_fstop: f-stop
        pixel_pitch_um: Pixel pitch
        dec_deg: Declination
        allow_tracking: Whether tracking mount is available
        
    Returns:
        (exposure_seconds, tracking_needed)
    """
    from .astronomy import npf_rule
    
    # Maximum exposure without trailing
    max_untracked = npf_rule(focal_length_mm, aperture_fstop, pixel_pitch_um, dec_deg)
    
    # Ideal exposure based on target brightness
    # Brighter targets need less time
    target_flux = mag_to_flux(target_brightness)
    
    # Base exposure for mag 15/arcsec² at f/2.8, 24mm
    base_exposure = 20.0  # seconds
    
    # Scale based on target brightness and optics
    ideal_exposure = base_exposure / (target_flux * (2.8 / aperture_fstop)**2)
    
    # Limit to reasonable range
    ideal_exposure = max(5.0, min(300.0, ideal_exposure))
    
    # Determine if tracking needed
    if ideal_exposure <= max_untracked:
        return ideal_exposure, False
    elif allow_tracking:
        return ideal_exposure, True
    else:
        return max_untracked, False


def recommend_settings(
    target: TargetProperties,
    camera: CameraProperties,
    focal_length_mm: float,
    aperture_fstop: float,
    sky_brightness: float,
    dec_deg: float,
    allow_tracking: bool = False
) -> ExposureSettings:
    """
    Generate complete exposure recommendations.
    
    Args:
        target: Target object properties
        camera: Camera sensor properties
        focal_length_mm: Lens focal length
        aperture_fstop: Aperture f-stop
        sky_brightness: Sky brightness (mag/arcsec²)
        dec_deg: Target declination
        allow_tracking: Tracking mount available
        
    Returns:
        Complete exposure settings
    """
    from .astronomy import calculate_star_trailing
    
    # Calculate exposure time
    exposure, tracking = calculate_exposure_time(
        target.surface_brightness,
        focal_length_mm,
        aperture_fstop,
        camera.pixel_pitch_um,
        dec_deg,
        allow_tracking
    )
    
    # Calculate ISO
    iso = calculate_optimal_iso(
        target.surface_brightness,
        sky_brightness,
        camera.read_noise_electrons,
        camera.max_iso,
        camera.iso_invariance_point
    )
    
    # Calculate star trailing
    trailing = calculate_star_trailing(
        exposure,
        dec_deg,
        focal_length_mm,
        camera.pixel_pitch_um
    )
    
    # Estimate SNR (simplified)
    target_flux = mag_to_flux(target.surface_brightness)
    sky_flux = mag_to_flux(sky_brightness)
    
    # Signal electrons (proportional to exposure and flux)
    signal = target_flux * exposure * 1000  # Arbitrary scale
    sky_noise = sky_flux * exposure * 1000
    
    snr = calculate_snr(
        signal,
        camera.read_noise_electrons * (iso / 100),
        exposure * 0.1,  # Dark current estimate
        sky_noise
    )
    
    # Dynamic range (simplified)
    dynamic_range = 14.0 - math.log2(iso / 100) - (sky_brightness - 22) / 3
    
    return ExposureSettings(
        shutter_seconds=round(exposure, 1),
        iso=iso,
        aperture_fstop=aperture_fstop,
        tracking_required=tracking,
        predicted_snr=snr,
        star_trailing_pixels=trailing,
        dynamic_range_stops=max(8.0, min(14.0, dynamic_range))
    )


# Example usage
if __name__ == "__main__":
    # Milky Way Core
    target = TargetProperties(
        surface_brightness=5.0,  # mag/arcsec²
        angular_size_arcmin=120,
        target_type='extended'
    )
    
    # Sony A7 III
    camera = CameraProperties(
        sensor_width_mm=35.6,
        sensor_height_mm=23.8,
        pixel_pitch_um=5.94,
        read_noise_electrons=3.0,
        max_iso=51200,
        iso_invariance_point=640
    )
    
    # 24mm f/2.8 lens
    settings = recommend_settings(
        target=target,
        camera=camera,
        focal_length_mm=24,
        aperture_fstop=2.8,
        sky_brightness=19.5,  # Bortle 4
        dec_deg=-30,
        allow_tracking=False
    )
    
    print(f"Recommended Settings:")
    print(f"  Shutter: {settings.shutter_seconds}s")
    print(f"  ISO: {settings.iso}")
    print(f"  Aperture: f/{settings.aperture_fstop}")
    print(f"  Tracking: {settings.tracking_required}")
    print(f"  Predicted SNR: {settings.predicted_snr:.1f}")
    print(f"  Star Trailing: {settings.star_trailing_pixels:.2f} pixels")
    print(f"  Dynamic Range: {settings.dynamic_range_stops:.1f} stops")
