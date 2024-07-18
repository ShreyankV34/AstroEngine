"""
Camera specifications database.

Contains sensor physics and noise characteristics for common cameras.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Camera:
    """Camera sensor specifications."""
    name: str
    manufacturer: str
    sensor_width_mm: float
    sensor_height_mm: float
    pixel_pitch_um: float  # Micrometers
    resolution_mp: float  # Megapixels
    read_noise_electrons: float  # At base ISO
    max_iso: int
    iso_invariance_point: int  # ISO where sensor becomes invariant
    dynamic_range_stops: float  # At base ISO
    sensor_type: str  # 'Full Frame', 'APS-C', 'Micro 4/3', etc.


# Camera Database
CAMERAS: Dict[str, Camera] = {
    # Sony Cameras
    "Sony A7 III": Camera(
        name="Sony A7 III",
        manufacturer="Sony",
        sensor_width_mm=35.6,
        sensor_height_mm=23.8,
        pixel_pitch_um=5.94,
        resolution_mp=24.2,
        read_noise_electrons=3.0,
        max_iso=51200,
        iso_invariance_point=640,
        dynamic_range_stops=14.7,
        sensor_type="Full Frame"
    ),
    
    "Sony A7R IV": Camera(
        name="Sony A7R IV",
        manufacturer="Sony",
        sensor_width_mm=35.7,
        sensor_height_mm=23.8,
        pixel_pitch_um=4.51,
        resolution_mp=61.0,
        read_noise_electrons=3.3,
        max_iso=32000,
        iso_invariance_point=640,
        dynamic_range_stops=14.8,
        sensor_type="Full Frame"
    ),
    
    "Sony A7S III": Camera(
        name="Sony A7S III",
        manufacturer="Sony",
        sensor_width_mm=35.6,
        sensor_height_mm=23.8,
        pixel_pitch_um=8.44,  # Large pixels for low light
        resolution_mp=12.1,
        read_noise_electrons=1.6,  # Excellent low-light performance
        max_iso=409600,
        iso_invariance_point=2000,
        dynamic_range_stops=15.0,
        sensor_type="Full Frame"
    ),
    
    "Sony A6400": Camera(
        name="Sony A6400",
        manufacturer="Sony",
        sensor_width_mm=23.5,
        sensor_height_mm=15.6,
        pixel_pitch_um=3.92,
        resolution_mp=24.2,
        read_noise_electrons=2.8,
        max_iso=32000,
        iso_invariance_point=800,
        dynamic_range_stops=13.7,
        sensor_type="APS-C"
    ),
    
    # Canon Cameras
    "Canon R5": Camera(
        name="Canon EOS R5",
        manufacturer="Canon",
        sensor_width_mm=36.0,
        sensor_height_mm=24.0,
        pixel_pitch_um=4.39,
        resolution_mp=45.0,
        read_noise_electrons=2.9,
        max_iso=51200,
        iso_invariance_point=800,
        dynamic_range_stops=14.4,
        sensor_type="Full Frame"
    ),
    
    "Canon R6": Camera(
        name="Canon EOS R6",
        manufacturer="Canon",
        sensor_width_mm=35.9,
        sensor_height_mm=23.9,
        pixel_pitch_um=5.36,
        resolution_mp=20.1,
        read_noise_electrons=2.5,
        max_iso=102400,
        iso_invariance_point=1600,
        dynamic_range_stops=14.3,
        sensor_type="Full Frame"
    ),
    
    "Canon 5D Mark IV": Camera(
        name="Canon 5D Mark IV",
        manufacturer="Canon",
        sensor_width_mm=36.0,
        sensor_height_mm=24.0,
        pixel_pitch_um=5.36,
        resolution_mp=30.4,
        read_noise_electrons=3.2,
        max_iso=32000,
        iso_invariance_point=1600,
        dynamic_range_stops=13.6,
        sensor_type="Full Frame"
    ),
    
    "Canon 6D Mark II": Camera(
        name="Canon 6D Mark II",
        manufacturer="Canon",
        sensor_width_mm=35.9,
        sensor_height_mm=24.0,
        pixel_pitch_um=5.70,
        resolution_mp=26.2,
        read_noise_electrons=3.5,
        max_iso=40000,
        iso_invariance_point=1600,
        dynamic_range_stops=13.0,
        sensor_type="Full Frame"
    ),
    
    # Nikon Cameras
    "Nikon Z6 II": Camera(
        name="Nikon Z6 II",
        manufacturer="Nikon",
        sensor_width_mm=35.9,
        sensor_height_mm=23.9,
        pixel_pitch_um=5.94,
        resolution_mp=24.5,
        read_noise_electrons=2.8,
        max_iso=51200,
        iso_invariance_point=800,
        dynamic_range_stops=14.5,
        sensor_type="Full Frame"
    ),
    
    "Nikon Z7 II": Camera(
        name="Nikon Z7 II",
        manufacturer="Nikon",
        sensor_width_mm=35.9,
        sensor_height_mm=23.9,
        pixel_pitch_um=4.35,
        resolution_mp=45.7,
        read_noise_electrons=3.0,
        max_iso=25600,
        iso_invariance_point=640,
        dynamic_range_stops=14.6,
        sensor_type="Full Frame"
    ),
    
    "Nikon D850": Camera(
        name="Nikon D850",
        manufacturer="Nikon",
        sensor_width_mm=35.9,
        sensor_height_mm=23.9,
        pixel_pitch_um=4.35,
        resolution_mp=45.7,
        read_noise_electrons=2.7,
        max_iso=25600,
        iso_invariance_point=400,
        dynamic_range_stops=14.8,
        sensor_type="Full Frame"
    ),
    
    "Nikon D750": Camera(
        name="Nikon D750",
        manufacturer="Nikon",
        sensor_width_mm=35.9,
        sensor_height_mm=24.0,
        pixel_pitch_um=5.98,
        resolution_mp=24.3,
        read_noise_electrons=3.1,
        max_iso=12800,
        iso_invariance_point=400,
        dynamic_range_stops=14.5,
        sensor_type="Full Frame"
    ),
    
    # Fujifilm Cameras
    "Fujifilm X-T4": Camera(
        name="Fujifilm X-T4",
        manufacturer="Fujifilm",
        sensor_width_mm=23.5,
        sensor_height_mm=15.6,
        pixel_pitch_um=3.76,
        resolution_mp=26.1,
        read_noise_electrons=2.9,
        max_iso=12800,
        iso_invariance_point=800,
        dynamic_range_stops=13.2,
        sensor_type="APS-C"
    ),
    
    "Fujifilm X-T3": Camera(
        name="Fujifilm X-T3",
        manufacturer="Fujifilm",
        sensor_width_mm=23.5,
        sensor_height_mm=15.6,
        pixel_pitch_um=3.76,
        resolution_mp=26.1,
        read_noise_electrons=3.0,
        max_iso=12800,
        iso_invariance_point=800,
        dynamic_range_stops=13.1,
        sensor_type="APS-C"
    ),
    
    # Generic Phone Camera (for comparison)
    "Generic Phone": Camera(
        name="Generic Smartphone Camera",
        manufacturer="Generic",
        sensor_width_mm=6.17,  # ~1/2.55" sensor
        sensor_height_mm=4.55,
        pixel_pitch_um=1.4,  # Tiny pixels
        resolution_mp=12.0,
        read_noise_electrons=8.0,  # High noise
        max_iso=3200,
        iso_invariance_point=400,
        dynamic_range_stops=10.0,
        sensor_type="Mobile"
    ),
}


def get_camera(name: str) -> Optional[Camera]:
    """
    Get camera by name (case-insensitive, fuzzy matching).
    
    Args:
        name: Camera name
        
    Returns:
        Camera object or None
    """
    name_lower = name.lower()
    
    # Exact match
    for key, camera in CAMERAS.items():
        if key.lower() == name_lower:
            return camera
    
    # Partial match
    for key, camera in CAMERAS.items():
        if name_lower in key.lower() or name_lower in camera.name.lower():
            return camera
    
    return None


def list_cameras(
    manufacturer: Optional[str] = None,
    sensor_type: Optional[str] = None
) -> List[Camera]:
    """
    List all cameras, optionally filtered.
    
    Args:
        manufacturer: Filter by manufacturer
        sensor_type: Filter by sensor type
        
    Returns:
        List of cameras
    """
    cameras = list(CAMERAS.values())
    
    if manufacturer:
        cameras = [c for c in cameras if c.manufacturer.lower() == manufacturer.lower()]
    
    if sensor_type:
        cameras = [c for c in cameras if c.sensor_type.lower() == sensor_type.lower()]
    
    return sorted(cameras, key=lambda c: c.name)


def get_cameras_by_sensor_type(sensor_type: str) -> List[Camera]:
    """Get all cameras of a specific sensor type."""
    return [c for c in CAMERAS.values() if c.sensor_type == sensor_type]


# Example usage
if __name__ == "__main__":
    # List all full-frame cameras
    print("Full Frame Cameras:")
    for camera in list_cameras(sensor_type="Full Frame"):
        print(f"  {camera.name}: {camera.pixel_pitch_um}µm pixels, "
              f"ISO inv. @ {camera.iso_invariance_point}")
    
    print("\nSony Cameras:")
    for camera in list_cameras(manufacturer="Sony"):
        print(f"  {camera.name}: {camera.resolution_mp}MP")
    
    # Get specific camera
    a7iii = get_camera("A7 III")
    if a7iii:
        print(f"\n{a7iii.name}:")
        print(f"  Sensor: {a7iii.sensor_width_mm}×{a7iii.sensor_height_mm}mm")
        print(f"  Pixel Pitch: {a7iii.pixel_pitch_um}µm")
        print(f"  Read Noise: {a7iii.read_noise_electrons}e-")
        print(f"  Dynamic Range: {a7iii.dynamic_range_stops} stops")