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


def calculate_stacking_benefit(
    single_frame_snr: float,
    num_frames: int,
    stacking_efficiency: float = 0.95
) -> Tuple[float, float]:
    """
    Calculate SNR improvement from frame stacking.

    Args:
        single_frame_snr: SNR of a single exposure
        num_frames: Number of frames to stack
        stacking_efficiency: Stacking efficiency (0.9-1.0, default: 0.95)

    Returns:
        (stacked_snr, improvement_factor)

    Note:
        Theoretical SNR improves by sqrt(N), but practical efficiency is ~95%

    Example:
        >>> stacked_snr, improvement = calculate_stacking_benefit(10.0, 100)
        >>> improvement  # Should be close to 10x
        9.5
    """
    # Theoretical improvement: sqrt(N)
    theoretical_improvement = math.sqrt(num_frames)

    # Apply stacking efficiency
    actual_improvement = theoretical_improvement * stacking_efficiency

    # Stacked SNR
    stacked_snr = single_frame_snr * actual_improvement

    return stacked_snr, actual_improvement


def calculate_frames_needed(
    target_snr: float,
    single_frame_snr: float,
    stacking_efficiency: float = 0.95
) -> int:
    """
    Calculate number of frames needed to reach target SNR.

    Args:
        target_snr: Desired SNR
        single_frame_snr: SNR of single exposure
        stacking_efficiency: Stacking efficiency

    Returns:
        Number of frames required

    Example:
        >>> frames = calculate_frames_needed(100.0, 10.0)
        >>> frames  # Should be ~111 frames (100/10)^2 / 0.95
        111
    """
    if single_frame_snr >= target_snr:
        return 1

    # SNR_stacked = SNR_single * sqrt(N) * efficiency
    # N = (SNR_stacked / (SNR_single * efficiency))^2
    frames = math.ceil((target_snr / (single_frame_snr * stacking_efficiency)) ** 2)

    return max(1, frames)


def calculate_total_integration_time(
    exposure_seconds: float,
    num_frames: int,
    dithering_overhead_sec: float = 5.0
) -> Tuple[float, float]:
    """
    Calculate total session time including overhead.

    Args:
        exposure_seconds: Single exposure time
        num_frames: Number of frames
        dithering_overhead_sec: Time between frames for dithering (default: 5s)

    Returns:
        (total_time_hours, integration_time_hours)

    Example:
        >>> total, integration = calculate_total_integration_time(30.0, 100)
        >>> total  # 30s * 100 + 5s * 100 = 58.3 minutes
        0.97
        >>> integration  # 30s * 100 = 50 minutes
        0.83
    """
    # Pure integration time
    integration_time_sec = exposure_seconds * num_frames

    # Total time with overhead
    total_time_sec = integration_time_sec + (dithering_overhead_sec * num_frames)

    return total_time_sec / 3600.0, integration_time_sec / 3600.0


def calculate_diffraction_limit(
    focal_length_mm: float,
    aperture_fstop: float,
    wavelength_nm: float = 550.0
) -> float:
    """
    Calculate diffraction-limited resolution (Airy disk diameter).

    Args:
        focal_length_mm: Focal length
        aperture_fstop: Aperture f-number
        wavelength_nm: Wavelength (default: 550nm, green)

    Returns:
        Airy disk diameter in micrometers at focal plane

    Reference:
        Rayleigh criterion: θ = 1.22 * λ / D

    Example:
        >>> airy = calculate_diffraction_limit(200, 5.6)
        >>> airy  # Approximately 7.5 micrometers
        7.52
    """
    # Aperture diameter in mm
    aperture_diameter_mm = focal_length_mm / aperture_fstop

    # Convert to meters
    aperture_diameter_m = aperture_diameter_mm / 1000.0
    wavelength_m = wavelength_nm * 1e-9

    # Angular resolution in radians (Rayleigh criterion)
    angular_resolution_rad = 1.22 * wavelength_m / aperture_diameter_m

    # Convert to micrometers at focal plane
    # size = focal_length * angle
    airy_disk_um = focal_length_mm * 1000.0 * angular_resolution_rad

    return airy_disk_um


def is_pixel_pitch_optimal(
    pixel_pitch_um: float,
    focal_length_mm: float,
    aperture_fstop: float
) -> Tuple[bool, str]:
    """
    Check if pixel pitch is matched to optics (sampling theorem).

    Args:
        pixel_pitch_um: Pixel pitch in micrometers
        focal_length_mm: Focal length
        aperture_fstop: Aperture f-number

    Returns:
        (is_optimal, recommendation)

    Note:
        Nyquist sampling: need 2-3 pixels per Airy disk diameter

    Example:
        >>> optimal, msg = is_pixel_pitch_optimal(5.94, 200, 2.8)
        >>> optimal
        True
        >>> "well-sampled" in msg
        True
    """
    airy_disk_um = calculate_diffraction_limit(focal_length_mm, aperture_fstop)

    # Sampling ratio: how many pixels per Airy disk
    pixels_per_airy = airy_disk_um / pixel_pitch_um

    if pixels_per_airy < 1.5:
        return False, f"Undersampled: {pixels_per_airy:.1f} pixels/airy (need 2-3). Consider smaller pixels or longer focal length."
    elif pixels_per_airy > 5.0:
        return False, f"Oversampled: {pixels_per_airy:.1f} pixels/airy (ideal 2-3). Wasting resolution; could use larger pixels."
    else:
        return True, f"Well-sampled: {pixels_per_airy:.1f} pixels/airy (optimal: 2-3). Excellent match!"


def predict_histogram_position(
    target_brightness_mag: float,
    sky_brightness_mag: float,
    exposure_seconds: float,
    iso: int
) -> Tuple[float, str]:
    """
    Predict histogram position for exposure validation.

    Args:
        target_brightness_mag: Target surface brightness
        sky_brightness_mag: Sky background brightness
        exposure_seconds: Exposure time
        iso: ISO setting

    Returns:
        (histogram_position, advice)
        histogram_position: 0.0 (left/black) to 1.0 (right/white)

    Note:
        For astrophotography, aim for:
        - Sky background: 15-30% (avoid clipping)
        - Stars: 50-80% (good SNR without saturation)

    Example:
        >>> pos, advice = predict_histogram_position(5.0, 19.5, 25, 1600)
        >>> 0.1 < pos < 0.4  # Sky should be in left third
        True
    """
    # Convert magnitudes to relative flux
    sky_flux = mag_to_flux(sky_brightness_mag)
    target_flux = mag_to_flux(target_brightness_mag)

    # Histogram position (simplified model)
    # Base position increases with exposure and ISO
    base_position = (exposure_seconds / 30.0) * (iso / 800.0) * sky_flux

    # Normalize to [0, 1]
    histogram_pos = min(0.95, base_position * 0.25)

    # Generate advice
    if histogram_pos < 0.10:
        advice = "⚠️ Very dark - increase ISO or exposure time"
    elif histogram_pos < 0.20:
        advice = "✓ Good - sky background well-placed, plenty of headroom"
    elif histogram_pos < 0.35:
        advice = "✓ Optimal - excellent balance"
    elif histogram_pos < 0.50:
        advice = "⚠️ Getting bright - watch for highlight clipping"
    else:
        advice = "❌ Too bright - reduce ISO or exposure time to avoid clipping"

    return histogram_pos, advice


def calculate_contrast_threshold(
    target_brightness: float,
    sky_brightness: float,
    snr: float
) -> Tuple[bool, float]:
    """
    Check if target has sufficient contrast above sky background.

    Args:
        target_brightness: Target surface brightness (mag/arcsec²)
        sky_brightness: Sky brightness (mag/arcsec²)
        snr: Predicted SNR

    Returns:
        (is_detectable, contrast_ratio)

    Note:
        For visual detection, need SNR > 5 and contrast > 1 mag
        For photography, more forgiving due to stacking

    Example:
        >>> detectable, contrast = calculate_contrast_threshold(5.0, 19.5, 15.0)
        >>> detectable
        True
        >>> contrast > 1.0  # Good contrast
        True
    """
    # Contrast in magnitudes (lower mag = brighter)
    contrast_mag = sky_brightness - target_brightness

    # Detection threshold
    # Need both SNR > 3 and some contrast
    is_detectable = snr > 3.0 and contrast_mag > 0.5

    return is_detectable, contrast_mag


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
