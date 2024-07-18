"""
Sensor physics models.

Calculate sensor-specific characteristics like quantum efficiency,
well depth, and thermal noise.
"""
import math
from typing import Tuple
from dataclasses import dataclass


@dataclass
class SensorPhysics:
    """Physical sensor characteristics."""
    pixel_pitch_um: float
    read_noise_electrons: float
    full_well_capacity: int  # Electrons
    quantum_efficiency: float  # 0-1
    dark_current_rate: float  # e-/pixel/second


def calculate_pixel_area(pixel_pitch_um: float) -> float:
    """
    Calculate pixel area in square micrometers.
    
    Args:
        pixel_pitch_um: Pixel pitch in micrometers
        
    Returns:
        Pixel area in µm²
    """
    return pixel_pitch_um ** 2


def calculate_full_well_capacity(pixel_pitch_um: float) -> int:
    """
    Estimate full well capacity based on pixel size.
    
    Larger pixels can hold more electrons before saturation.
    
    Args:
        pixel_pitch_um: Pixel pitch in micrometers
        
    Returns:
        Estimated full well capacity in electrons
    """
    # Empirical formula: approximately 1000 electrons per square micrometer
    pixel_area = calculate_pixel_area(pixel_pitch_um)
    full_well = int(pixel_area * 1000)
    
    return full_well


def calculate_saturation_capacity(
    full_well_capacity: int,
    iso: int,
    base_iso: int = 100
) -> int:
    """
    Calculate effective saturation capacity at a given ISO.
    
    Higher ISO reduces effective capacity (unity gain occurs earlier).
    
    Args:
        full_well_capacity: Full well capacity at base ISO
        iso: Current ISO setting
        base_iso: Base ISO (typically 100)
        
    Returns:
        Effective capacity in electrons
    """
    iso_factor = base_iso / iso
    return int(full_well_capacity * iso_factor)


def calculate_read_noise_at_iso(
    base_read_noise: float,
    iso: int,
    base_iso: int = 100,
    iso_invariance_point: int = 640
) -> float:
    """
    Calculate read noise at a given ISO.
    
    Below ISO invariance point: noise increases with ISO
    Above ISO invariance point: noise stays constant (ISO invariant)
    
    Args:
        base_read_noise: Read noise at base ISO (electrons)
        iso: Target ISO
        base_iso: Base ISO
        iso_invariance_point: ISO where sensor becomes invariant
        
    Returns:
        Read noise in electrons
    """
    if iso <= iso_invariance_point:
        # Pre-invariance: read noise scales with ISO
        iso_factor = iso / base_iso
        return base_read_noise * iso_factor
    else:
        # Post-invariance: read noise constant
        invariance_factor = iso_invariance_point / base_iso
        return base_read_noise * invariance_factor


def calculate_dark_current(
    temperature_celsius: float,
    base_dark_current: float = 0.1,  # e-/pixel/second at 25°C
    doubling_temp: float = 6.3  # Temperature for doubling (typical)
) -> float:
    """
    Calculate dark current (thermal noise) at a given temperature.
    
    Dark current approximately doubles every 6-7°C.
    
    Args:
        temperature_celsius: Sensor temperature
        base_dark_current: Dark current at 25°C
        doubling_temp: Temperature increase that doubles dark current
        
    Returns:
        Dark current in electrons/pixel/second
    """
    temp_diff = temperature_celsius - 25.0
    doublings = temp_diff / doubling_temp
    
    dark_current = base_dark_current * (2 ** doublings)
    return dark_current


def calculate_dynamic_range(
    full_well_capacity: int,
    read_noise_electrons: float
) -> float:
    """
    Calculate sensor dynamic range in stops.
    
    Dynamic Range = log2(Full Well Capacity / Read Noise)
    
    Args:
        full_well_capacity: Maximum electrons per pixel
        read_noise_electrons: Read noise floor
        
    Returns:
        Dynamic range in stops
    """
    if read_noise_electrons <= 0:
        return 0.0
    
    dr = math.log2(full_well_capacity / read_noise_electrons)
    return dr


def calculate_shot_noise(signal_electrons: float) -> float:
    """
    Calculate photon shot noise.
    
    Shot noise follows Poisson statistics: σ = sqrt(N)
    
    Args:
        signal_electrons: Number of signal electrons
        
    Returns:
        Shot noise (standard deviation) in electrons
    """
    return math.sqrt(max(0, signal_electrons))


def calculate_total_noise(
    signal_electrons: float,
    read_noise: float,
    dark_current: float,
    exposure_seconds: float
) -> float:
    """
    Calculate total noise from all sources.
    
    Total Noise = sqrt(Shot² + Read² + Dark)
    
    Args:
        signal_electrons: Signal from target
        read_noise: Read noise in electrons
        dark_current: Dark current rate (e-/pixel/s)
        exposure_seconds: Exposure time
        
    Returns:
        Total noise in electrons
    """
    shot_noise = calculate_shot_noise(signal_electrons)
    dark_electrons = dark_current * exposure_seconds
    
    total_noise = math.sqrt(
        shot_noise**2 +
        read_noise**2 +
        dark_electrons
    )
    
    return total_noise


def calculate_snr(
    signal_electrons: float,
    read_noise: float,
    dark_current: float,
    exposure_seconds: float
) -> float:
    """
    Calculate Signal-to-Noise Ratio.
    
    Args:
        signal_electrons: Signal from target
        read_noise: Read noise in electrons
        dark_current: Dark current rate
        exposure_seconds: Exposure time
        
    Returns:
        SNR value
    """
    noise = calculate_total_noise(
        signal_electrons,
        read_noise,
        dark_current,
        exposure_seconds
    )
    
    if noise == 0:
        return 0.0
    
    return signal_electrons / noise


def estimate_quantum_efficiency(
    sensor_type: str = "CMOS",
    wavelength_nm: float = 550  # Green light
) -> float:
    """
    Estimate quantum efficiency for a sensor type.
    
    QE varies by wavelength - peaks around 550nm (green) for most sensors.
    
    Args:
        sensor_type: 'CMOS' or 'CCD'
        wavelength_nm: Light wavelength in nanometers
        
    Returns:
        Quantum efficiency (0-1)
    """
    # Simplified QE curve
    # Peak QE around 550nm, drops off at red/blue ends
    
    if sensor_type.upper() == "CMOS":
        peak_qe = 0.65  # Modern CMOS ~60-70% peak QE
    else:  # CCD
        peak_qe = 0.70  # CCD slightly better
    
    # Wavelength response (simplified Gaussian)
    optimal_wavelength = 550  # nm (green)
    wavelength_factor = math.exp(-((wavelength_nm - optimal_wavelength) / 200)**2)
    
    qe = peak_qe * wavelength_factor
    return max(0.0, min(1.0, qe))


def calculate_electrons_per_adu(
    iso: int,
    base_iso: int = 100,
    base_gain: float = 1.0  # electrons per ADU at base ISO
) -> float:
    """
    Calculate conversion gain (electrons per ADU) at a given ISO.
    
    Args:
        iso: Current ISO setting
        base_iso: Base ISO (typically 100)
        base_gain: Gain at base ISO
        
    Returns:
        Electrons per ADU (analog-to-digital unit)
    """
    # Higher ISO = lower gain (unity gain reached sooner)
    iso_factor = base_iso / iso
    return base_gain * iso_factor


# Example usage
if __name__ == "__main__":
    # Sony A7 III example
    pixel_pitch = 5.94  # µm
    base_read_noise = 3.0  # electrons
    
    print("=== Sony A7 III Sensor Analysis ===\n")
    
    # Calculate basic properties
    full_well = calculate_full_well_capacity(pixel_pitch)
    print(f"Full Well Capacity: {full_well:,} e-")
    
    dr = calculate_dynamic_range(full_well, base_read_noise)
    print(f"Dynamic Range: {dr:.1f} stops")
    
    # At different ISO values
    print("\nNoise at different ISO:")
    for iso in [100, 400, 1600, 3200, 6400]:
        read_noise = calculate_read_noise_at_iso(base_read_noise, iso, 100, 640)
        print(f"  ISO {iso}: {read_noise:.2f}e- read noise")
    
    # Temperature effect
    print("\nDark current at different temperatures:")
    for temp in [0, 10, 20, 30]:
        dark = calculate_dark_current(temp)
        print(f"  {temp}°C: {dark:.3f} e-/pixel/second")
    
    # SNR example
    print("\nSNR for 15-second exposure at ISO 3200:")
    signal = 5000  # electrons from target
    read_noise_iso = calculate_read_noise_at_iso(base_read_noise, 3200, 100, 640)
    dark = calculate_dark_current(20)  # 20°C
    
    snr = calculate_snr(signal, read_noise_iso, dark, 15)
    print(f"  Signal: {signal}e-")
    print(f"  SNR: {snr:.1f}")