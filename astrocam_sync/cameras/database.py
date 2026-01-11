"""
Camera specifications database.

Contains sensor physics and noise characteristics for common cameras.
Includes detailed astrophotography-specific measurements and recommendations.
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class ReadNoiseCurve:
    """Read noise measurements at different ISO values."""
    iso_values: List[int]
    read_noise_electrons: List[float]

    def get_read_noise(self, iso: int) -> float:
        """Get read noise at specific ISO (interpolates if needed)."""
        if iso in self.iso_values:
            idx = self.iso_values.index(iso)
            return self.read_noise_electrons[idx]

        # Simple linear interpolation
        for i in range(len(self.iso_values) - 1):
            if self.iso_values[i] <= iso <= self.iso_values[i + 1]:
                # Linear interpolation
                iso1, iso2 = self.iso_values[i], self.iso_values[i + 1]
                rn1, rn2 = self.read_noise_electrons[i], self.read_noise_electrons[i + 1]
                factor = (iso - iso1) / (iso2 - iso1)
                return rn1 + (rn2 - rn1) * factor

        return self.read_noise_electrons[-1]


@dataclass
class DynamicRangeCurve:
    """Dynamic range measurements at different ISO values."""
    iso_values: List[int]
    dr_stops: List[float]

    def get_dynamic_range(self, iso: int) -> float:
        """Get dynamic range at specific ISO."""
        if iso in self.iso_values:
            idx = self.iso_values.index(iso)
            return self.dr_stops[idx]
        return self.dr_stops[0]  # Default to base ISO


@dataclass
class StarEaterAnalysis:
    """Analysis of star eater behavior (spatial filtering on long exposures)."""
    has_star_eater: bool
    affected_exposure_range: Optional[Tuple[float, float]] = None  # (min_sec, max_sec)
    severity: str = "None"  # None, Low, Medium, High
    workaround: Optional[str] = None
    firmware_fix_available: bool = False


@dataclass
class AstroSettings:
    """Recommended astrophotography settings."""
    recommended_iso_range: Tuple[int, int]  # (min, max)
    optimal_iso_single_shot: int
    optimal_iso_stacking: int
    bulb_mode_stable: bool
    long_exposure_nr_recommended: bool
    notes: str = ""


@dataclass
class Camera:
    """Comprehensive camera sensor specifications for astrophotography."""
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

    # Extended specifications
    read_noise_curve: Optional[ReadNoiseCurve] = None
    dynamic_range_curve: Optional[DynamicRangeCurve] = None
    star_eater: Optional[StarEaterAnalysis] = None
    astro_settings: Optional[AstroSettings] = None
    base_iso: int = 100
    native_iso_range: Optional[Tuple[int, int]] = None
    full_well_capacity: Optional[float] = None  # electrons
    quantum_efficiency: Optional[float] = None  # peak QE percentage

    def get_pixel_area_um2(self) -> float:
        """Calculate pixel area in square micrometers."""
        return self.pixel_pitch_um ** 2

    def get_sensor_area_mm2(self) -> float:
        """Calculate total sensor area in square millimeters."""
        return self.sensor_width_mm * self.sensor_height_mm

    def get_read_noise_at_iso(self, iso: int) -> float:
        """Get read noise at specific ISO."""
        if self.read_noise_curve:
            return self.read_noise_curve.get_read_noise(iso)
        return self.read_noise_electrons

    def get_dynamic_range_at_iso(self, iso: int) -> float:
        """Get dynamic range at specific ISO."""
        if self.dynamic_range_curve:
            return self.dynamic_range_curve.get_dynamic_range(iso)
        return self.dynamic_range_stops

    def is_iso_invariant_at(self, iso: int) -> bool:
        """Check if sensor is ISO invariant at given ISO."""
        return iso >= self.iso_invariance_point


# ============================================================================
# CAMERA DATABASE - 30+ Professional Cameras for Astrophotography
# ============================================================================

CAMERAS: Dict[str, Camera] = {
    # ========================================================================
    # SONY CAMERAS (12 models)
    # ========================================================================

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
        sensor_type="Full Frame",
        base_iso=100,
        native_iso_range=(100, 51200),
        full_well_capacity=52000,
        quantum_efficiency=58.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 640, 800, 1600, 3200, 6400, 12800, 25600],
            read_noise_electrons=[3.0, 2.8, 2.5, 2.2, 2.2, 2.3, 2.5, 2.8, 3.2, 3.8]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 640, 1600, 3200, 6400, 12800],
            dr_stops=[14.7, 14.5, 14.0, 13.5, 12.3, 11.0, 9.8, 8.5]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=True,
            affected_exposure_range=(3.2, 30.0),
            severity="Medium",
            workaround="Use firmware 3.10+ or Bulb mode with external intervalometer",
            firmware_fix_available=True
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(800, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=800,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Excellent all-around astro camera. Use firmware 3.10+ to avoid star eater. ISO 800-1600 ideal for Milky Way."
        )
    ),

    "Sony A7R III": Camera(
        name="Sony A7R III",
        manufacturer="Sony",
        sensor_width_mm=35.9,
        sensor_height_mm=24.0,
        pixel_pitch_um=4.51,
        resolution_mp=42.4,
        read_noise_electrons=3.2,
        max_iso=32000,
        iso_invariance_point=640,
        dynamic_range_stops=14.7,
        sensor_type="Full Frame",
        base_iso=100,
        native_iso_range=(100, 32000),
        full_well_capacity=31200,
        quantum_efficiency=56.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 640, 800, 1600, 3200, 6400, 12800],
            read_noise_electrons=[3.2, 3.0, 2.7, 2.4, 2.4, 2.5, 2.7, 3.0, 3.5]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 640, 1600, 3200, 6400],
            dr_stops=[14.7, 14.4, 13.9, 13.4, 12.2, 10.9, 9.6]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=True,
            affected_exposure_range=(3.2, 30.0),
            severity="High",
            workaround="Use uncompressed RAW + Bulb mode, or firmware update if available",
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(640, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=640,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="High resolution excellent for deep sky. Star eater is significant issue - use Bulb mode and uncompressed RAW."
        )
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
        sensor_type="Full Frame",
        base_iso=100,
        native_iso_range=(100, 32000),
        full_well_capacity=30800,
        quantum_efficiency=57.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 640, 800, 1600, 3200, 6400, 12800],
            read_noise_electrons=[3.3, 3.1, 2.8, 2.5, 2.5, 2.6, 2.8, 3.1, 3.6]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 640, 1600, 3200, 6400],
            dr_stops=[14.8, 14.5, 14.0, 13.5, 12.3, 11.0, 9.7]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(640, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=640,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Best Sony for deep sky imaging. 61MP allows aggressive cropping. No star eater issues. Pixel shift mode for ultimate detail."
        )
    ),

    "Sony A7R V": Camera(
        name="Sony A7R V",
        manufacturer="Sony",
        sensor_width_mm=35.7,
        sensor_height_mm=23.8,
        pixel_pitch_um=4.51,
        resolution_mp=61.0,
        read_noise_electrons=3.1,
        max_iso=32000,
        iso_invariance_point=500,
        dynamic_range_stops=14.9,
        sensor_type="Full Frame",
        base_iso=100,
        native_iso_range=(100, 32000),
        full_well_capacity=32000,
        quantum_efficiency=58.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 500, 640, 1600, 3200, 6400, 12800],
            read_noise_electrons=[3.1, 2.9, 2.6, 2.3, 2.3, 2.4, 2.6, 2.9, 3.4]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 640, 1600, 3200, 6400],
            dr_stops=[14.9, 14.6, 14.1, 13.6, 12.4, 11.1, 9.8]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(500, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=500,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Latest high-res Sony with improved sensor. Excellent for deep sky. Better low ISO performance than A7R IV."
        )
    ),

    "Sony A7S III": Camera(
        name="Sony A7S III",
        manufacturer="Sony",
        sensor_width_mm=35.6,
        sensor_height_mm=23.8,
        pixel_pitch_um=8.44,
        resolution_mp=12.1,
        read_noise_electrons=1.6,
        max_iso=409600,
        iso_invariance_point=2000,
        dynamic_range_stops=15.0,
        sensor_type="Full Frame",
        base_iso=80,
        native_iso_range=(80, 102400),
        full_well_capacity=95000,
        quantum_efficiency=65.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[80, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600, 51200],
            read_noise_electrons=[1.6, 1.5, 1.4, 1.3, 1.2, 1.2, 1.3, 1.5, 1.8, 2.2, 2.8]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[80, 100, 200, 400, 1600, 3200, 6400, 12800, 25600],
            dr_stops=[15.0, 14.9, 14.7, 14.3, 13.2, 12.0, 10.8, 9.6, 8.4]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(1600, 12800),
            optimal_iso_single_shot=6400,
            optimal_iso_stacking=3200,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Ultimate low-light camera. Massive 8.44µm pixels. Exceptional for Milky Way timelapses and aurora. Can shoot at insane ISOs."
        )
    ),

    "Sony A7C": Camera(
        name="Sony A7C",
        manufacturer="Sony",
        sensor_width_mm=35.6,
        sensor_height_mm=23.8,
        pixel_pitch_um=5.94,
        resolution_mp=24.2,
        read_noise_electrons=3.1,
        max_iso=51200,
        iso_invariance_point=640,
        dynamic_range_stops=14.6,
        sensor_type="Full Frame",
        base_iso=100,
        native_iso_range=(100, 51200),
        full_well_capacity=51000,
        quantum_efficiency=57.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 640, 800, 1600, 3200, 6400, 12800],
            read_noise_electrons=[3.1, 2.9, 2.6, 2.3, 2.3, 2.4, 2.6, 2.9, 3.3]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 640, 1600, 3200, 6400],
            dr_stops=[14.6, 14.4, 13.9, 13.4, 12.2, 10.9, 9.6]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(640, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=800,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Compact full-frame, same sensor as A7 III. Great travel astro camera. No star eater issues."
        )
    ),

    "Sony A7C II": Camera(
        name="Sony A7C II",
        manufacturer="Sony",
        sensor_width_mm=35.7,
        sensor_height_mm=23.8,
        pixel_pitch_um=5.86,
        resolution_mp=33.0,
        read_noise_electrons=2.8,
        max_iso=51200,
        iso_invariance_point=500,
        dynamic_range_stops=14.7,
        sensor_type="Full Frame",
        base_iso=100,
        native_iso_range=(100, 51200),
        full_well_capacity=48000,
        quantum_efficiency=59.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 500, 640, 1600, 3200, 6400, 12800],
            read_noise_electrons=[2.8, 2.6, 2.4, 2.1, 2.1, 2.2, 2.4, 2.7, 3.1]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 640, 1600, 3200, 6400],
            dr_stops=[14.7, 14.5, 14.0, 13.5, 12.3, 11.0, 9.7]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(500, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=640,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Updated compact full-frame with improved sensor. 33MP sweet spot for resolution vs pixel size. Great all-rounder."
        )
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
        sensor_type="APS-C",
        base_iso=100,
        native_iso_range=(100, 32000),
        full_well_capacity=21000,
        quantum_efficiency=55.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 800, 1600, 3200, 6400, 12800],
            read_noise_electrons=[2.8, 2.6, 2.4, 2.2, 2.3, 2.5, 2.8, 3.2]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 800, 1600, 3200, 6400],
            dr_stops=[13.7, 13.5, 13.1, 12.6, 11.4, 10.2, 9.0]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(800, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=800,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Budget-friendly APS-C for astro. Good performance for Milky Way. Lighter system for travel."
        )
    ),

    "Sony A6600": Camera(
        name="Sony A6600",
        manufacturer="Sony",
        sensor_width_mm=23.5,
        sensor_height_mm=15.6,
        pixel_pitch_um=3.92,
        resolution_mp=24.2,
        read_noise_electrons=2.7,
        max_iso=32000,
        iso_invariance_point=800,
        dynamic_range_stops=13.8,
        sensor_type="APS-C",
        base_iso=100,
        native_iso_range=(100, 32000),
        full_well_capacity=21500,
        quantum_efficiency=56.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 800, 1600, 3200, 6400, 12800],
            read_noise_electrons=[2.7, 2.5, 2.3, 2.1, 2.2, 2.4, 2.7, 3.1]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 800, 1600, 3200, 6400],
            dr_stops=[13.8, 13.6, 13.2, 12.7, 11.5, 10.3, 9.1]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(800, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=800,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="A6400 with IBIS and better battery. Excellent for tracked wide-field. In-body stabilization helpful for framing."
        )
    ),

    "Sony A6700": Camera(
        name="Sony A6700",
        manufacturer="Sony",
        sensor_width_mm=23.5,
        sensor_height_mm=15.6,
        pixel_pitch_um=3.76,
        resolution_mp=26.0,
        read_noise_electrons=2.6,
        max_iso=32000,
        iso_invariance_point=640,
        dynamic_range_stops=13.9,
        sensor_type="APS-C",
        base_iso=100,
        native_iso_range=(100, 32000),
        full_well_capacity=20800,
        quantum_efficiency=57.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 640, 800, 1600, 3200, 6400, 12800],
            read_noise_electrons=[2.6, 2.4, 2.2, 1.9, 2.0, 2.1, 2.3, 2.6, 3.0]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 640, 1600, 3200, 6400],
            dr_stops=[13.9, 13.7, 13.3, 12.8, 11.6, 10.4, 9.2]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(640, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=640,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Latest APS-C with AI processor. Improved sensor tech. Great for travel and lightweight setups."
        )
    ),

    "Sony A1": Camera(
        name="Sony A1",
        manufacturer="Sony",
        sensor_width_mm=35.9,
        sensor_height_mm=24.0,
        pixel_pitch_um=4.26,
        resolution_mp=50.1,
        read_noise_electrons=2.9,
        max_iso=32000,
        iso_invariance_point=500,
        dynamic_range_stops=14.8,
        sensor_type="Full Frame",
        base_iso=100,
        native_iso_range=(100, 32000),
        full_well_capacity=28500,
        quantum_efficiency=59.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 500, 640, 1600, 3200, 6400, 12800],
            read_noise_electrons=[2.9, 2.7, 2.4, 2.1, 2.2, 2.3, 2.5, 2.8, 3.2]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 640, 1600, 3200, 6400],
            dr_stops=[14.8, 14.6, 14.1, 13.6, 12.4, 11.1, 9.8]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(500, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=500,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Flagship Sony with stacked sensor. 50MP with excellent speed. Great for deep sky when detail matters. Premium choice."
        )
    ),

    "Sony A9 III": Camera(
        name="Sony A9 III",
        manufacturer="Sony",
        sensor_width_mm=35.7,
        sensor_height_mm=23.8,
        pixel_pitch_um=5.26,
        resolution_mp=24.6,
        read_noise_electrons=2.5,
        max_iso=51200,
        iso_invariance_point=400,
        dynamic_range_stops=14.8,
        sensor_type="Full Frame",
        base_iso=250,
        native_iso_range=(250, 25600),
        full_well_capacity=42000,
        quantum_efficiency=60.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[250, 400, 640, 1600, 3200, 6400, 12800, 25600],
            read_noise_electrons=[2.5, 2.2, 2.0, 2.1, 2.3, 2.6, 3.0, 3.5]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[250, 400, 640, 1600, 3200, 6400, 12800],
            dr_stops=[14.8, 14.5, 14.1, 12.9, 11.6, 10.3, 9.0]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(400, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=640,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Global shutter sensor - unique tech. No rolling shutter. Base ISO 250. Excellent for Milky Way timelapses and tracked imaging."
        )
    ),

    # ========================================================================
    # CANON CAMERAS (8 models)
    # ========================================================================

    "Canon EOS R5": Camera(
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
        sensor_type="Full Frame",
        base_iso=100,
        native_iso_range=(100, 51200),
        full_well_capacity=29500,
        quantum_efficiency=57.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600],
            read_noise_electrons=[2.9, 2.7, 2.5, 2.3, 2.4, 2.6, 2.9, 3.3, 3.8]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 800, 1600, 3200, 6400, 12800],
            dr_stops=[14.4, 14.2, 13.8, 13.3, 12.1, 10.8, 9.5, 8.2]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(800, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=800,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Flagship Canon mirrorless. 45MP excellent for deep sky. IBIS helps with framing. Watch for thermal limitations on long sessions."
        )
    ),

    "Canon EOS R6": Camera(
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
        sensor_type="Full Frame",
        base_iso=100,
        native_iso_range=(100, 102400),
        full_well_capacity=45000,
        quantum_efficiency=58.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600],
            read_noise_electrons=[2.5, 2.3, 2.1, 1.9, 1.9, 2.1, 2.4, 2.8, 3.3]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 1600, 3200, 6400, 12800],
            dr_stops=[14.3, 14.1, 13.7, 12.5, 11.2, 9.9, 8.6]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(1600, 6400),
            optimal_iso_single_shot=3200,
            optimal_iso_stacking=1600,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Low-light specialist. Large 5.36µm pixels. Excellent for Milky Way and aurora. ISO 3200-6400 very usable."
        )
    ),

    "Canon EOS R6 Mark II": Camera(
        name="Canon EOS R6 Mark II",
        manufacturer="Canon",
        sensor_width_mm=35.9,
        sensor_height_mm=23.9,
        pixel_pitch_um=5.15,
        resolution_mp=24.2,
        read_noise_electrons=2.4,
        max_iso=102400,
        iso_invariance_point=1600,
        dynamic_range_stops=14.4,
        sensor_type="Full Frame",
        base_iso=100,
        native_iso_range=(100, 102400),
        full_well_capacity=42000,
        quantum_efficiency=59.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600],
            read_noise_electrons=[2.4, 2.2, 2.0, 1.8, 1.8, 2.0, 2.3, 2.7, 3.2]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 1600, 3200, 6400, 12800],
            dr_stops=[14.4, 14.2, 13.8, 12.6, 11.3, 10.0, 8.7]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(1600, 6400),
            optimal_iso_single_shot=3200,
            optimal_iso_stacking=1600,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Updated R6 with 24MP. Better heat management. Sweet spot between resolution and low-light. Great all-rounder for astro."
        )
    ),

    "Canon EOS R": Camera(
        name="Canon EOS R",
        manufacturer="Canon",
        sensor_width_mm=36.0,
        sensor_height_mm=24.0,
        pixel_pitch_um=5.36,
        resolution_mp=30.3,
        read_noise_electrons=2.7,
        max_iso=40000,
        iso_invariance_point=1600,
        dynamic_range_stops=14.1,
        sensor_type="Full Frame",
        base_iso=100,
        native_iso_range=(100, 40000),
        full_well_capacity=44000,
        quantum_efficiency=56.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 800, 1600, 3200, 6400, 12800],
            read_noise_electrons=[2.7, 2.5, 2.3, 2.1, 2.1, 2.3, 2.6, 3.1]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 1600, 3200, 6400],
            dr_stops=[14.1, 13.9, 13.5, 12.3, 11.0, 9.7]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(1600, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=1600,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="First Canon RF mount. 30MP good balance. No IBIS, so tracking mount recommended for deep sky."
        )
    ),

    "Canon EOS RP": Camera(
        name="Canon EOS RP",
        manufacturer="Canon",
        sensor_width_mm=35.9,
        sensor_height_mm=24.0,
        pixel_pitch_um=5.76,
        resolution_mp=26.2,
        read_noise_electrons=2.8,
        max_iso=40000,
        iso_invariance_point=1600,
        dynamic_range_stops=13.9,
        sensor_type="Full Frame",
        base_iso=100,
        native_iso_range=(100, 40000),
        full_well_capacity=48000,
        quantum_efficiency=55.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 800, 1600, 3200, 6400, 12800],
            read_noise_electrons=[2.8, 2.6, 2.4, 2.2, 2.2, 2.4, 2.7, 3.2]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 1600, 3200, 6400],
            dr_stops=[13.9, 13.7, 13.3, 12.1, 10.8, 9.5]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(1600, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=1600,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Budget full-frame RF. Light and compact for travel. Large pixels good for low-light. Best value Canon for astro."
        )
    ),

    "Canon EOS R7": Camera(
        name="Canon EOS R7",
        manufacturer="Canon",
        sensor_width_mm=22.5,
        sensor_height_mm=15.0,
        pixel_pitch_um=3.72,
        resolution_mp=32.5,
        read_noise_electrons=2.6,
        max_iso=32000,
        iso_invariance_point=800,
        dynamic_range_stops=13.5,
        sensor_type="APS-C",
        base_iso=100,
        native_iso_range=(100, 32000),
        full_well_capacity=19500,
        quantum_efficiency=56.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 800, 1600, 3200, 6400, 12800],
            read_noise_electrons=[2.6, 2.4, 2.2, 2.0, 2.1, 2.3, 2.6, 3.0]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 800, 1600, 3200, 6400],
            dr_stops=[13.5, 13.3, 12.9, 12.4, 11.2, 10.0, 8.8]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(800, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=800,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="High-res APS-C. Great for planetary and lunar with long focal lengths. 32MP allows cropping. Crop factor extends reach."
        )
    ),

    "Canon EOS R8": Camera(
        name="Canon EOS R8",
        manufacturer="Canon",
        sensor_width_mm=36.0,
        sensor_height_mm=24.0,
        pixel_pitch_um=5.15,
        resolution_mp=24.2,
        read_noise_electrons=2.5,
        max_iso=102400,
        iso_invariance_point=1600,
        dynamic_range_stops=14.2,
        sensor_type="Full Frame",
        base_iso=100,
        native_iso_range=(100, 102400),
        full_well_capacity=41000,
        quantum_efficiency=58.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600],
            read_noise_electrons=[2.5, 2.3, 2.1, 1.9, 1.9, 2.1, 2.4, 2.8, 3.3]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 1600, 3200, 6400, 12800],
            dr_stops=[14.2, 14.0, 13.6, 12.4, 11.1, 9.8, 8.5]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(1600, 6400),
            optimal_iso_single_shot=3200,
            optimal_iso_stacking=1600,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Budget R6 II sensor. No IBIS but excellent sensor. Great value for dedicated astro setups with tracking mount."
        )
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
        sensor_type="Full Frame",
        base_iso=100,
        native_iso_range=(100, 32000),
        full_well_capacity=43000,
        quantum_efficiency=54.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 800, 1600, 3200, 6400, 12800],
            read_noise_electrons=[3.2, 3.0, 2.8, 2.6, 2.6, 2.8, 3.1, 3.6]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 1600, 3200, 6400],
            dr_stops=[13.6, 13.4, 13.0, 11.8, 10.5, 9.2]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(1600, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=1600,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Classic DSLR workhorse. Robust build. Dual card slots. Good for long sessions. Battery life excellent. Mirror lockup essential."
        )
    ),

    # ========================================================================
    # NIKON CAMERAS (8 models)
    # ========================================================================

    "Nikon Z6": Camera(
        name="Nikon Z6",
        manufacturer="Nikon",
        sensor_width_mm=35.9,
        sensor_height_mm=23.9,
        pixel_pitch_um=5.94,
        resolution_mp=24.5,
        read_noise_electrons=2.9,
        max_iso=51200,
        iso_invariance_point=400,
        dynamic_range_stops=14.6,
        sensor_type="Full Frame",
        base_iso=100,
        native_iso_range=(100, 51200),
        full_well_capacity=51000,
        quantum_efficiency=57.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600],
            read_noise_electrons=[2.9, 2.7, 2.4, 2.5, 2.6, 2.8, 3.1, 3.5, 4.0]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 800, 1600, 3200, 6400, 12800],
            dr_stops=[14.6, 14.4, 14.0, 13.5, 12.3, 11.0, 9.7, 8.4]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(400, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=400,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Excellent all-around Z mount. ISO invariance from 400 is rare advantage. Can shoot at 100-200 and push in post."
        )
    ),

    "Nikon Z6 II": Camera(
        name="Nikon Z6 II",
        manufacturer="Nikon",
        sensor_width_mm=35.9,
        sensor_height_mm=23.9,
        pixel_pitch_um=5.94,
        resolution_mp=24.5,
        read_noise_electrons=2.8,
        max_iso=51200,
        iso_invariance_point=400,
        dynamic_range_stops=14.5,
        sensor_type="Full Frame",
        base_iso=100,
        native_iso_range=(100, 51200),
        full_well_capacity=52000,
        quantum_efficiency=58.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600],
            read_noise_electrons=[2.8, 2.6, 2.3, 2.4, 2.5, 2.7, 3.0, 3.4, 3.9]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 400, 800, 1600, 3200, 6400, 12800],
            dr_stops=[14.5, 14.3, 13.9, 13.4, 12.2, 10.9, 9.6, 8.3]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(400, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=400,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Updated Z6 with dual processors. Faster buffer. Same sensor excellence. Dual card slots. ISO 400 invariance still applies."
        )
    ),

    "Nikon Z6 III": Camera(
        name="Nikon Z6 III",
        manufacturer="Nikon",
        sensor_width_mm=35.9,
        sensor_height_mm=23.9,
        pixel_pitch_um=5.15,
        resolution_mp=24.5,
        read_noise_electrons=2.6,
        max_iso=64000,
        iso_invariance_point=320,
        dynamic_range_stops=14.7,
        sensor_type="Full Frame",
        base_iso=100,
        native_iso_range=(100, 64000),
        full_well_capacity=40000,
        quantum_efficiency=60.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[100, 200, 320, 640, 1600, 3200, 6400, 12800, 25600],
            read_noise_electrons=[2.6, 2.4, 2.1, 2.2, 2.3, 2.5, 2.8, 3.2, 3.7]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[100, 200, 320, 640, 1600, 3200, 6400, 12800],
            dr_stops=[14.7, 14.5, 14.1, 13.6, 12.4, 11.1, 9.8, 8.5]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(320, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=320,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Partially stacked sensor. Improved speed and readout. ISO 320 invariance even better. 24MP sweet spot for astro. Flagship quality."
        )
    ),

    "Nikon Z7": Camera(
        name="Nikon Z7",
        manufacturer="Nikon",
        sensor_width_mm=35.9,
        sensor_height_mm=23.9,
        pixel_pitch_um=4.35,
        resolution_mp=45.7,
        read_noise_electrons=3.1,
        max_iso=25600,
        iso_invariance_point=400,
        dynamic_range_stops=14.6,
        sensor_type="Full Frame",
        base_iso=64,
        native_iso_range=(64, 25600),
        full_well_capacity=29000,
        quantum_efficiency=56.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[64, 100, 200, 400, 800, 1600, 3200, 6400, 12800],
            read_noise_electrons=[3.3, 3.1, 2.9, 2.6, 2.7, 2.8, 3.0, 3.3, 3.8]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[64, 100, 200, 400, 800, 1600, 3200, 6400],
            dr_stops=[14.8, 14.6, 14.3, 13.9, 13.4, 12.2, 10.9, 9.6]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(400, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=400,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="High-res Z mount. 45MP like D850. Base ISO 64 excellent for dark skies. ISO 400+ for stacking. Superb detail."
        )
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
        iso_invariance_point=400,
        dynamic_range_stops=14.6,
        sensor_type="Full Frame",
        base_iso=64,
        native_iso_range=(64, 25600),
        full_well_capacity=29500,
        quantum_efficiency=57.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[64, 100, 200, 400, 800, 1600, 3200, 6400, 12800],
            read_noise_electrons=[3.2, 3.0, 2.8, 2.5, 2.6, 2.7, 2.9, 3.2, 3.7]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[64, 100, 200, 400, 800, 1600, 3200, 6400],
            dr_stops=[14.8, 14.6, 14.3, 13.9, 13.4, 12.2, 10.9, 9.6]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(400, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=400,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Z7 with dual processors and dual card slots. Same sensor excellence. Professional reliability for long imaging sessions."
        )
    ),

    "Nikon Z8": Camera(
        name="Nikon Z8",
        manufacturer="Nikon",
        sensor_width_mm=35.9,
        sensor_height_mm=23.9,
        pixel_pitch_um=4.35,
        resolution_mp=45.7,
        read_noise_electrons=2.8,
        max_iso=64000,
        iso_invariance_point=320,
        dynamic_range_stops=14.8,
        sensor_type="Full Frame",
        base_iso=64,
        native_iso_range=(64, 25600),
        full_well_capacity=30000,
        quantum_efficiency=59.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[64, 100, 200, 320, 640, 1600, 3200, 6400, 12800],
            read_noise_electrons=[3.0, 2.8, 2.6, 2.3, 2.4, 2.5, 2.7, 3.0, 3.4]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[64, 100, 200, 320, 640, 1600, 3200, 6400],
            dr_stops=[15.0, 14.8, 14.5, 14.1, 13.6, 12.4, 11.1, 9.8]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(320, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=320,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Z9 sensor in Z8 body. Stacked sensor tech. 45MP with incredible speed. ISO 320 invariance. Top-tier for deep sky imaging."
        )
    ),

    "Nikon Z9": Camera(
        name="Nikon Z9",
        manufacturer="Nikon",
        sensor_width_mm=35.9,
        sensor_height_mm=23.9,
        pixel_pitch_um=4.35,
        resolution_mp=45.7,
        read_noise_electrons=2.7,
        max_iso=64000,
        iso_invariance_point=320,
        dynamic_range_stops=14.8,
        sensor_type="Full Frame",
        base_iso=64,
        native_iso_range=(64, 25600),
        full_well_capacity=30500,
        quantum_efficiency=59.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[64, 100, 200, 320, 640, 1600, 3200, 6400, 12800],
            read_noise_electrons=[2.9, 2.7, 2.5, 2.2, 2.3, 2.4, 2.6, 2.9, 3.3]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[64, 100, 200, 320, 640, 1600, 3200, 6400],
            dr_stops=[15.0, 14.8, 14.5, 14.1, 13.6, 12.4, 11.1, 9.8]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(320, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=320,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Flagship stacked sensor. 45MP beast. ISO 64 base for pristine data. ISO 320 invariance allows flexible workflow. Premium choice."
        )
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
        sensor_type="Full Frame",
        base_iso=64,
        native_iso_range=(64, 25600),
        full_well_capacity=29000,
        quantum_efficiency=58.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[64, 100, 200, 400, 800, 1600, 3200, 6400, 12800],
            read_noise_electrons=[2.9, 2.7, 2.5, 2.2, 2.3, 2.4, 2.6, 2.9, 3.4]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[64, 100, 200, 400, 800, 1600, 3200, 6400],
            dr_stops=[14.8, 14.6, 14.3, 13.9, 13.4, 12.2, 10.9, 9.6]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(400, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=400,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Legendary DSLR. 45MP, ISO 64 base, incredible DR. ISO 400 invariance unique. Astro classic. Battery lasts forever."
        )
    ),

    # ========================================================================
    # FUJIFILM CAMERAS (6 models)
    # ========================================================================

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
        sensor_type="APS-C",
        base_iso=160,
        native_iso_range=(160, 12800),
        full_well_capacity=19800,
        quantum_efficiency=56.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[160, 200, 400, 800, 1600, 3200, 6400, 12800],
            read_noise_electrons=[2.9, 2.8, 2.6, 2.4, 2.5, 2.7, 3.0, 3.4]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[160, 200, 400, 800, 1600, 3200, 6400],
            dr_stops=[13.2, 13.1, 12.7, 12.2, 11.0, 9.8, 8.6]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(800, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=800,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Excellent APS-C with IBIS. X-Trans sensor has unique color. 26MP good resolution. Great for travel astro."
        )
    ),

    "Fujifilm X-T5": Camera(
        name="Fujifilm X-T5",
        manufacturer="Fujifilm",
        sensor_width_mm=23.5,
        sensor_height_mm=15.6,
        pixel_pitch_um=3.34,
        resolution_mp=40.2,
        read_noise_electrons=2.7,
        max_iso=12800,
        iso_invariance_point=640,
        dynamic_range_stops=13.4,
        sensor_type="APS-C",
        base_iso=125,
        native_iso_range=(125, 12800),
        full_well_capacity=16200,
        quantum_efficiency=57.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[125, 160, 200, 400, 640, 1600, 3200, 6400, 12800],
            read_noise_electrons=[2.7, 2.6, 2.5, 2.3, 2.1, 2.2, 2.4, 2.7, 3.1]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[125, 160, 200, 400, 640, 1600, 3200, 6400],
            dr_stops=[13.4, 13.3, 13.2, 12.8, 12.3, 11.1, 9.9, 8.7]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(640, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=640,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="High-res APS-C with 40MP. Smaller pixels but more detail. Excellent for deep sky with telescope. Pixel shift mode available."
        )
    ),

    "Fujifilm X-S10": Camera(
        name="Fujifilm X-S10",
        manufacturer="Fujifilm",
        sensor_width_mm=23.5,
        sensor_height_mm=15.6,
        pixel_pitch_um=3.76,
        resolution_mp=26.1,
        read_noise_electrons=3.0,
        max_iso=12800,
        iso_invariance_point=800,
        dynamic_range_stops=13.1,
        sensor_type="APS-C",
        base_iso=160,
        native_iso_range=(160, 12800),
        full_well_capacity=19500,
        quantum_efficiency=55.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[160, 200, 400, 800, 1600, 3200, 6400, 12800],
            read_noise_electrons=[3.0, 2.9, 2.7, 2.5, 2.6, 2.8, 3.1, 3.5]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[160, 200, 400, 800, 1600, 3200, 6400],
            dr_stops=[13.1, 13.0, 12.6, 12.1, 10.9, 9.7, 8.5]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(800, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=800,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Compact budget Fuji with IBIS. Same sensor as X-T4. Great value for travel astro. Lighter kit for hiking."
        )
    ),

    "Fujifilm X-S20": Camera(
        name="Fujifilm X-S20",
        manufacturer="Fujifilm",
        sensor_width_mm=23.5,
        sensor_height_mm=15.6,
        pixel_pitch_um=3.76,
        resolution_mp=26.1,
        read_noise_electrons=2.8,
        max_iso=12800,
        iso_invariance_point=800,
        dynamic_range_stops=13.3,
        sensor_type="APS-C",
        base_iso=125,
        native_iso_range=(125, 12800),
        full_well_capacity=20000,
        quantum_efficiency=56.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[125, 160, 200, 400, 800, 1600, 3200, 6400, 12800],
            read_noise_electrons=[2.8, 2.7, 2.6, 2.4, 2.2, 2.3, 2.5, 2.8, 3.2]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[125, 160, 200, 400, 800, 1600, 3200, 6400],
            dr_stops=[13.3, 13.2, 13.1, 12.7, 12.2, 11.0, 9.8, 8.6]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(800, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=800,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Updated X-S10 with improved processing. Better battery. 26MP sweet spot. Great for Milky Way panoramas."
        )
    ),

    "Fujifilm X-H2": Camera(
        name="Fujifilm X-H2",
        manufacturer="Fujifilm",
        sensor_width_mm=23.5,
        sensor_height_mm=15.6,
        pixel_pitch_um=3.34,
        resolution_mp=40.2,
        read_noise_electrons=2.6,
        max_iso=12800,
        iso_invariance_point=640,
        dynamic_range_stops=13.5,
        sensor_type="APS-C",
        base_iso=125,
        native_iso_range=(125, 12800),
        full_well_capacity=16500,
        quantum_efficiency=58.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[125, 160, 200, 400, 640, 1600, 3200, 6400, 12800],
            read_noise_electrons=[2.6, 2.5, 2.4, 2.2, 2.0, 2.1, 2.3, 2.6, 3.0]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[125, 160, 200, 400, 640, 1600, 3200, 6400],
            dr_stops=[13.5, 13.4, 13.3, 12.9, 12.4, 11.2, 10.0, 8.8]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(640, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=640,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Flagship 40MP APS-C. Same sensor as X-T5 but pro features. Excellent for deep sky detail. Pixel shift for ultimate resolution."
        )
    ),

    "Fujifilm X-H2S": Camera(
        name="Fujifilm X-H2S",
        manufacturer="Fujifilm",
        sensor_width_mm=23.5,
        sensor_height_mm=15.6,
        pixel_pitch_um=4.08,
        resolution_mp=26.1,
        read_noise_electrons=2.5,
        max_iso=12800,
        iso_invariance_point=640,
        dynamic_range_stops=13.6,
        sensor_type="APS-C",
        base_iso=160,
        native_iso_range=(160, 12800),
        full_well_capacity=24000,
        quantum_efficiency=59.0,
        read_noise_curve=ReadNoiseCurve(
            iso_values=[160, 200, 400, 640, 1600, 3200, 6400, 12800],
            read_noise_electrons=[2.5, 2.4, 2.2, 2.0, 2.1, 2.3, 2.6, 3.0]
        ),
        dynamic_range_curve=DynamicRangeCurve(
            iso_values=[160, 200, 400, 640, 1600, 3200, 6400],
            dr_stops=[13.6, 13.5, 13.1, 12.6, 11.4, 10.2, 9.0]
        ),
        star_eater=StarEaterAnalysis(
            has_star_eater=False,
            severity="None",
            workaround=None,
            firmware_fix_available=False
        ),
        astro_settings=AstroSettings(
            recommended_iso_range=(640, 3200),
            optimal_iso_single_shot=1600,
            optimal_iso_stacking=640,
            bulb_mode_stable=True,
            long_exposure_nr_recommended=False,
            notes="Stacked sensor APS-C. Speed demon. Larger pixels than X-H2. Better low-light. Excellent for Milky Way timelapses."
        )
    ),
}


# ============================================================================
# QUERY FUNCTIONS
# ============================================================================

def get_camera(name: str) -> Optional[Camera]:
    """
    Get camera by name (case-insensitive, fuzzy matching).

    Args:
        name: Camera name

    Returns:
        Camera object or None

    Examples:
        >>> cam = get_camera("A7 III")
        >>> cam = get_camera("sony a7iii")
        >>> cam = get_camera("EOS R5")
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
    sensor_type: Optional[str] = None,
    min_resolution: Optional[float] = None,
    max_resolution: Optional[float] = None,
    min_pixel_pitch: Optional[float] = None,
    max_read_noise: Optional[float] = None
) -> List[Camera]:
    """
    List all cameras, optionally filtered by various criteria.

    Args:
        manufacturer: Filter by manufacturer (Sony, Canon, Nikon, Fujifilm)
        sensor_type: Filter by sensor type (Full Frame, APS-C)
        min_resolution: Minimum resolution in megapixels
        max_resolution: Maximum resolution in megapixels
        min_pixel_pitch: Minimum pixel pitch in micrometers
        max_read_noise: Maximum read noise in electrons

    Returns:
        List of cameras matching criteria

    Examples:
        >>> # Get all Sony full-frame cameras
        >>> cams = list_cameras(manufacturer="Sony", sensor_type="Full Frame")

        >>> # Get low-light specialists (large pixels, low noise)
        >>> cams = list_cameras(min_pixel_pitch=5.0, max_read_noise=3.0)
    """
    cameras = list(CAMERAS.values())

    if manufacturer:
        cameras = [c for c in cameras if c.manufacturer.lower() == manufacturer.lower()]

    if sensor_type:
        cameras = [c for c in cameras if c.sensor_type.lower() == sensor_type.lower()]

    if min_resolution is not None:
        cameras = [c for c in cameras if c.resolution_mp >= min_resolution]

    if max_resolution is not None:
        cameras = [c for c in cameras if c.resolution_mp <= max_resolution]

    if min_pixel_pitch is not None:
        cameras = [c for c in cameras if c.pixel_pitch_um >= min_pixel_pitch]

    if max_read_noise is not None:
        cameras = [c for c in cameras if c.read_noise_electrons <= max_read_noise]

    return sorted(cameras, key=lambda c: c.name)


def get_cameras_by_sensor_type(sensor_type: str) -> List[Camera]:
    """
    Get all cameras of a specific sensor type.

    Args:
        sensor_type: Sensor type ("Full Frame", "APS-C", etc.)

    Returns:
        List of cameras with matching sensor type
    """
    return [c for c in CAMERAS.values() if c.sensor_type == sensor_type]


def get_cameras_by_manufacturer(manufacturer: str) -> List[Camera]:
    """
    Get all cameras from a specific manufacturer.

    Args:
        manufacturer: Manufacturer name (Sony, Canon, Nikon, Fujifilm)

    Returns:
        List of cameras from manufacturer
    """
    return [c for c in CAMERAS.values()
            if c.manufacturer.lower() == manufacturer.lower()]


def find_best_for_deep_sky(
    min_resolution: float = 20.0,
    max_read_noise: float = 3.5
) -> List[Camera]:
    """
    Find cameras best suited for deep sky imaging.

    Criteria: High resolution, low read noise, good dynamic range

    Args:
        min_resolution: Minimum megapixels (default 20MP)
        max_read_noise: Maximum read noise in electrons (default 3.5e-)

    Returns:
        List of suitable cameras sorted by dynamic range
    """
    candidates = [
        c for c in CAMERAS.values()
        if c.resolution_mp >= min_resolution
        and c.read_noise_electrons <= max_read_noise
    ]
    return sorted(candidates, key=lambda c: c.dynamic_range_stops, reverse=True)


def find_best_for_milky_way(
    min_pixel_pitch: float = 4.5,
    max_read_noise: float = 3.0
) -> List[Camera]:
    """
    Find cameras best suited for Milky Way photography.

    Criteria: Large pixels for low-light, low read noise, high ISO capability

    Args:
        min_pixel_pitch: Minimum pixel pitch in micrometers (default 4.5µm)
        max_read_noise: Maximum read noise in electrons (default 3.0e-)

    Returns:
        List of suitable cameras sorted by pixel pitch (larger first)
    """
    candidates = [
        c for c in CAMERAS.values()
        if c.pixel_pitch_um >= min_pixel_pitch
        and c.read_noise_electrons <= max_read_noise
    ]
    return sorted(candidates, key=lambda c: c.pixel_pitch_um, reverse=True)


def find_iso_invariant_cameras(max_invariance_iso: int = 800) -> List[Camera]:
    """
    Find cameras with early ISO invariance (good for flexible exposure workflow).

    Args:
        max_invariance_iso: Maximum ISO invariance point (default 800)

    Returns:
        List of cameras sorted by ISO invariance point (lower first)
    """
    candidates = [
        c for c in CAMERAS.values()
        if c.iso_invariance_point <= max_invariance_iso
    ]
    return sorted(candidates, key=lambda c: c.iso_invariance_point)


def cameras_without_star_eater() -> List[Camera]:
    """
    Get all cameras without star eater issues.

    Returns:
        List of cameras without star eater problems
    """
    return [
        c for c in CAMERAS.values()
        if c.star_eater and not c.star_eater.has_star_eater
    ]


def compare_cameras(camera_names: List[str]) -> Optional[Dict]:
    """
    Compare multiple cameras side-by-side.

    Args:
        camera_names: List of camera names to compare

    Returns:
        Dictionary with comparison data, or None if cameras not found

    Example:
        >>> result = compare_cameras(["Sony A7 III", "Canon EOS R6", "Nikon Z6 II"])
    """
    cameras = []
    for name in camera_names:
        cam = get_camera(name)
        if cam:
            cameras.append(cam)
        else:
            print(f"Warning: Camera '{name}' not found")

    if not cameras:
        return None

    comparison = {
        "cameras": [c.name for c in cameras],
        "resolution_mp": [c.resolution_mp for c in cameras],
        "pixel_pitch_um": [c.pixel_pitch_um for c in cameras],
        "read_noise_e": [c.read_noise_electrons for c in cameras],
        "dynamic_range_stops": [c.dynamic_range_stops for c in cameras],
        "iso_invariance": [c.iso_invariance_point for c in cameras],
        "sensor_type": [c.sensor_type for c in cameras],
    }

    return comparison


def get_camera_stats() -> Dict:
    """
    Get database statistics.

    Returns:
        Dictionary with database stats
    """
    cameras = list(CAMERAS.values())

    manufacturers = {}
    sensor_types = {}

    for cam in cameras:
        manufacturers[cam.manufacturer] = manufacturers.get(cam.manufacturer, 0) + 1
        sensor_types[cam.sensor_type] = sensor_types.get(cam.sensor_type, 0) + 1

    return {
        "total_cameras": len(cameras),
        "manufacturers": manufacturers,
        "sensor_types": sensor_types,
        "avg_resolution_mp": sum(c.resolution_mp for c in cameras) / len(cameras),
        "avg_pixel_pitch_um": sum(c.pixel_pitch_um for c in cameras) / len(cameras),
        "avg_read_noise_e": sum(c.read_noise_electrons for c in cameras) / len(cameras),
        "avg_dynamic_range": sum(c.dynamic_range_stops for c in cameras) / len(cameras),
    }


def print_camera_summary(camera: Camera) -> None:
    """
    Print detailed summary of camera specifications.

    Args:
        camera: Camera object to summarize
    """
    print(f"\n{'='*70}")
    print(f"{camera.name} - {camera.manufacturer}")
    print(f"{'='*70}")
    print(f"\nSENSOR SPECIFICATIONS:")
    print(f"  Type:              {camera.sensor_type}")
    print(f"  Dimensions:        {camera.sensor_width_mm:.1f} × {camera.sensor_height_mm:.1f} mm")
    print(f"  Area:              {camera.get_sensor_area_mm2():.1f} mm²")
    print(f"  Resolution:        {camera.resolution_mp:.1f} MP")
    print(f"  Pixel Pitch:       {camera.pixel_pitch_um:.2f} µm")
    print(f"  Pixel Area:        {camera.get_pixel_area_um2():.2f} µm²")

    if camera.full_well_capacity:
        print(f"  Full Well:         {camera.full_well_capacity:,.0f} e-")
    if camera.quantum_efficiency:
        print(f"  Quantum Efficiency: {camera.quantum_efficiency:.1f}%")

    print(f"\nNOISE & DYNAMIC RANGE:")
    print(f"  Read Noise (base): {camera.read_noise_electrons:.1f} e-")
    print(f"  Dynamic Range:     {camera.dynamic_range_stops:.1f} stops")
    print(f"  Base ISO:          {camera.base_iso}")
    print(f"  Max ISO:           {camera.max_iso:,}")
    print(f"  ISO Invariance:    {camera.iso_invariance_point}")

    if camera.native_iso_range:
        print(f"  Native ISO Range:  {camera.native_iso_range[0]} - {camera.native_iso_range[1]:,}")

    if camera.star_eater:
        print(f"\nSTAR EATER ANALYSIS:")
        print(f"  Has Star Eater:    {'Yes' if camera.star_eater.has_star_eater else 'No'}")
        if camera.star_eater.has_star_eater:
            print(f"  Severity:          {camera.star_eater.severity}")
            if camera.star_eater.affected_exposure_range:
                print(f"  Affected Range:    {camera.star_eater.affected_exposure_range[0]:.1f}s - {camera.star_eater.affected_exposure_range[1]:.1f}s")
            if camera.star_eater.workaround:
                print(f"  Workaround:        {camera.star_eater.workaround}")

    if camera.astro_settings:
        print(f"\nASTROPHOTOGRAPHY RECOMMENDATIONS:")
        print(f"  Recommended ISO:   {camera.astro_settings.recommended_iso_range[0]} - {camera.astro_settings.recommended_iso_range[1]:,}")
        print(f"  Optimal (Single):  ISO {camera.astro_settings.optimal_iso_single_shot:,}")
        print(f"  Optimal (Stack):   ISO {camera.astro_settings.optimal_iso_stacking:,}")
        print(f"  Bulb Stable:       {'Yes' if camera.astro_settings.bulb_mode_stable else 'No'}")
        print(f"  Long Exp NR:       {'Recommended' if camera.astro_settings.long_exposure_nr_recommended else 'Not Recommended'}")
        if camera.astro_settings.notes:
            print(f"\n  Notes: {camera.astro_settings.notes}")

    print(f"\n{'='*70}\n")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("ASTROCAM DATABASE - EXAMPLE USAGE")
    print("="*70)

    # Database statistics
    print("\n1. DATABASE STATISTICS")
    print("-" * 70)
    stats = get_camera_stats()
    print(f"Total cameras in database: {stats['total_cameras']}")
    print(f"Manufacturers: {', '.join(f'{k} ({v})' for k, v in stats['manufacturers'].items())}")
    print(f"Sensor types: {', '.join(f'{k} ({v})' for k, v in stats['sensor_types'].items())}")
    print(f"Average resolution: {stats['avg_resolution_mp']:.1f} MP")
    print(f"Average pixel pitch: {stats['avg_pixel_pitch_um']:.2f} µm")
    print(f"Average read noise: {stats['avg_read_noise_e']:.2f} e-")
    print(f"Average dynamic range: {stats['avg_dynamic_range']:.1f} stops")

    # List cameras by manufacturer
    print("\n2. SONY FULL-FRAME CAMERAS")
    print("-" * 70)
    sony_ff = list_cameras(manufacturer="Sony", sensor_type="Full Frame")
    for camera in sony_ff[:5]:  # Show first 5
        print(f"  {camera.name:20s} - {camera.resolution_mp:5.1f}MP, "
              f"{camera.pixel_pitch_um:.2f}µm pixels, ISO inv @ {camera.iso_invariance_point}")

    # Best for deep sky
    print("\n3. BEST CAMERAS FOR DEEP SKY IMAGING")
    print("-" * 70)
    deep_sky = find_best_for_deep_sky(min_resolution=40.0, max_read_noise=3.2)
    for i, camera in enumerate(deep_sky[:5], 1):
        print(f"  {i}. {camera.name:25s} - {camera.resolution_mp:.1f}MP, "
              f"DR: {camera.dynamic_range_stops:.1f} stops, RN: {camera.read_noise_electrons:.1f}e-")

    # Best for Milky Way
    print("\n4. BEST CAMERAS FOR MILKY WAY")
    print("-" * 70)
    milky_way = find_best_for_milky_way(min_pixel_pitch=5.0, max_read_noise=2.8)
    for i, camera in enumerate(milky_way[:5], 1):
        print(f"  {i}. {camera.name:25s} - {camera.pixel_pitch_um:.2f}µm pixels, "
              f"RN: {camera.read_noise_electrons:.1f}e-")

    # ISO invariant cameras
    print("\n5. CAMERAS WITH EARLY ISO INVARIANCE (<= 640)")
    print("-" * 70)
    iso_inv = find_iso_invariant_cameras(max_invariance_iso=640)
    for camera in iso_inv[:5]:
        print(f"  {camera.name:25s} - ISO invariant from {camera.iso_invariance_point}")

    # Cameras without star eater
    print("\n6. CAMERAS WITHOUT STAR EATER ISSUES")
    print("-" * 70)
    no_star_eater = cameras_without_star_eater()
    print(f"  {len(no_star_eater)} out of {stats['total_cameras']} cameras have no star eater issues")

    # Detailed camera summary
    print("\n7. DETAILED CAMERA EXAMPLE - Sony A7S III")
    print("-" * 70)
    a7siii = get_camera("A7S III")
    if a7siii:
        print_camera_summary(a7siii)

    # Read noise at different ISOs
    print("\n8. READ NOISE CURVES - Comparison")
    print("-" * 70)
    test_cameras = ["Sony A7 III", "Canon EOS R6", "Nikon Z6 II"]
    test_isos = [100, 400, 1600, 6400]

    print(f"{'Camera':<20s}", end="")
    for iso in test_isos:
        print(f"  ISO {iso:5d}", end="")
    print()
    print("-" * 70)

    for cam_name in test_cameras:
        cam = get_camera(cam_name)
        if cam:
            print(f"{cam.name:<20s}", end="")
            for iso in test_isos:
                rn = cam.get_read_noise_at_iso(iso)
                print(f"  {rn:5.1f}e-", end="")
            print()

    # Camera comparison
    print("\n9. CAMERA COMPARISON")
    print("-" * 70)
    comparison = compare_cameras(["Sony A7R V", "Canon EOS R5", "Nikon Z8"])
    if comparison:
        print(f"{'Metric':<20s}", end="")
        for cam in comparison['cameras']:
            print(f"  {cam:<20s}", end="")
        print()
        print("-" * 70)

        metrics = [
            ('Resolution (MP)', 'resolution_mp', '.1f'),
            ('Pixel Pitch (µm)', 'pixel_pitch_um', '.2f'),
            ('Read Noise (e-)', 'read_noise_e', '.1f'),
            ('DR (stops)', 'dynamic_range_stops', '.1f'),
            ('ISO Invariance', 'iso_invariance', 'd'),
        ]

        for label, key, fmt in metrics:
            print(f"{label:<20s}", end="")
            for value in comparison[key]:
                print(f"  {value:<20{fmt}}", end="")
            print()

    print("\n" + "="*70)
    print("END OF EXAMPLES")
    print("="*70 + "\n")