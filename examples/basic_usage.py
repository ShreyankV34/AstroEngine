#!/usr/bin/env python3
"""
Basic AstroCamSync Usage Example

Demonstrates core functionality:
- Time conversions (UTC → LST)
- Coordinate transformations
- Target catalog queries
- Camera database lookups
- Exposure calculations
- Light pollution assessment
- Moon impact evaluation
"""

from datetime import datetime, timezone
from astrocam_sync.core import time, coordinates, astronomy, engine
from astrocam_sync.targets.catalog import get_target, list_targets
from astrocam_sync.cameras.database import get_camera
from astrocam_sync.cameras.phones import get_smartphone, get_top_astro_phones
from astrocam_sync.conditions.light_pollution import sqm_to_bortle, get_sky_quality, is_target_visible
from astrocam_sync.conditions.moon import assess_moon_impact, calculate_best_imaging_window


def main():
    print("=" * 80)
    print("AstroCamSync - Basic Usage Example")
    print("Observatory-Grade Astrophotography Planning")
    print("=" * 80)

    # ========================================================================
    # 1. LOCATION AND TIME SETUP
    # ========================================================================
    print("\n" + "=" * 80)
    print("1. LOCATION AND TIME")
    print("=" * 80)

    # Los Angeles coordinates
    latitude = 34.0522  # °N
    longitude = -118.2437  # °W

    # Current time
    current_utc = datetime.now(timezone.utc)

    print(f"\nLocation: Los Angeles ({latitude}°N, {longitude}°W)")
    print(f"Current UTC: {current_utc.strftime('%Y-%m-%d %H:%M:%S')}")

    # Convert to LST
    lst_hours = time.utc_to_lst(current_utc, longitude)
    print(f"Local Sidereal Time: {time.format_hours_hms(lst_hours)}")

    # Julian Date
    jd = time.utc_to_julian_date(current_utc)
    print(f"Julian Date: {jd:.6f}")

    # ========================================================================
    # 2. TARGET SELECTION
    # ========================================================================
    print("\n" + "=" * 80)
    print("2. TARGET SELECTION")
    print("=" * 80)

    # List available targets
    available_targets = list_targets()
    print(f"\nAvailable targets in database: {len(available_targets)}")
    print("\nSample targets:")
    for target_name in available_targets[:10]:
        print(f"  - {target_name}")

    # Select Milky Way Core
    target_name = "Milky Way Core"
    target = get_target(target_name)

    if target:
        print(f"\n📷 Selected Target: {target.name}")
        print(f"   RA: {time.format_hours_hms(target.ra_hours)} ({target.ra_hours:.4f}h)")
        print(f"   Dec: {target.dec_deg:+.2f}°")
        print(f"   Surface Brightness: {target.surface_brightness_mag:.1f} mag/arcsec²")
        print(f"   Angular Size: {target.angular_size_arcmin:.1f} arcmin")
        print(f"   Best Months: {', '.join(target.best_months)}")

        # Calculate current position
        horiz = coordinates.equatorial_to_horizontal(
            target.ra_hours,
            target.dec_deg,
            lst_hours,
            latitude
        )

        print(f"\n   Current Position:")
        print(f"   Altitude: {horiz.alt_deg:.1f}°")
        print(f"   Azimuth: {horiz.az_deg:.1f}° ({horiz.compass_direction()})")
        print(f"   Airmass: {horiz.airmass():.2f}")

        if horiz.alt_deg > 30:
            print(f"   ✅ Target is well-positioned for imaging!")
        elif horiz.alt_deg > 0:
            print(f"   ⚠️ Target is low (high airmass)")
        else:
            print(f"   ❌ Target is below horizon")

    # ========================================================================
    # 3. CAMERA SELECTION
    # ========================================================================
    print("\n" + "=" * 80)
    print("3. CAMERA SELECTION")
    print("=" * 80)

    # Get camera from database
    camera_name = "Sony A7 III"
    camera = get_camera(camera_name)

    if camera:
        print(f"\n📷 Selected Camera: {camera.brand} {camera.model}")
        print(f"   Sensor: {camera.sensor_width_mm:.1f}mm × {camera.sensor_height_mm:.1f}mm")
        print(f"   Resolution: {camera.resolution_megapixels:.1f} MP")
        print(f"   Pixel Pitch: {camera.pixel_pitch_um:.2f} μm")
        print(f"   Read Noise: {camera.read_noise_electrons_base:.1f} e⁻ @ ISO {camera.base_iso}")
        print(f"   ISO Invariance: {camera.iso_invariance_point}")

    # Alternative: Smartphone
    print(f"\n   Alternative - Best Smartphones for Astro:")
    top_phones = get_top_astro_phones(min_rating=9.0)
    for phone in top_phones[:3]:
        print(f"   - {phone.brand} {phone.model} (Rating: {phone.astro_rating}/10)")

    # ========================================================================
    # 4. LIGHT POLLUTION ASSESSMENT
    # ========================================================================
    print("\n" + "=" * 80)
    print("4. LIGHT POLLUTION ASSESSMENT")
    print("=" * 80)

    # Measure sky brightness (simulate SQM reading)
    sky_brightness_mag = 19.5  # mag/arcsec² (Bortle 4-5 - suburban)

    bortle_class = sqm_to_bortle(sky_brightness_mag)
    sky_quality = get_sky_quality(bortle_class)

    print(f"\n🌃 Sky Quality: Bortle Class {bortle_class.value}")
    print(f"   Sky Brightness: {sky_quality.sky_brightness_mag} mag/arcsec²")
    print(f"   NELM: {sky_quality.nelm}")
    print(f"   Milky Way Visible: {sky_quality.milky_way_visible}")
    print(f"   Description: {sky_quality.description}")

    # Check target visibility
    if target:
        visible, recommendation = is_target_visible(
            bortle_class,
            target.surface_brightness_mag,
            target.name
        )
        print(f"\n   Target Visibility: {recommendation}")

    # ========================================================================
    # 5. MOON CONDITIONS
    # ========================================================================
    print("\n" + "=" * 80)
    print("5. MOON CONDITIONS")
    print("=" * 80)

    # Calculate moon phase
    moon_phase_angle, moon_illumination = astronomy.moon_phase(jd)
    print(f"\n🌙 Moon Phase: {moon_illumination:.1f}% illuminated")
    print(f"   Phase Angle: {moon_phase_angle:.1f}°")

    # Assess impact (simulate moon position)
    moon_altitude = 15.0  # degrees above horizon
    moon_separation = 90.0  # degrees from target

    quality, assessment = assess_moon_impact(
        moon_illumination,
        moon_altitude,
        moon_separation
    )

    print(f"\n   Impact on Astrophotography: {quality.upper()}")
    print(f"   {assessment}")

    # Next dark window
    start, end, desc = calculate_best_imaging_window(current_utc)
    print(f"\n   {desc}")

    # ========================================================================
    # 6. EXPOSURE CALCULATIONS
    # ========================================================================
    print("\n" + "=" * 80)
    print("6. EXPOSURE CALCULATIONS")
    print("=" * 80)

    if target and camera:
        # Lens parameters
        focal_length_mm = 24  # 24mm wide-angle lens
        aperture_fstop = 2.8

        print(f"\n🔭 Optics: {focal_length_mm}mm f/{aperture_fstop}")

        # NPF Rule for max untracked exposure
        max_exposure_npf = astronomy.npf_rule(
            focal_length_mm,
            aperture_fstop,
            camera.pixel_pitch_um,
            target.dec_deg
        )

        print(f"\n   NPF Rule Maximum Exposure: {max_exposure_npf:.1f}s")

        # Create TargetProperties
        target_props = engine.TargetProperties(
            surface_brightness=target.surface_brightness_mag,
            angular_size_arcmin=target.angular_size_arcmin,
            target_type=str(target.target_type.value)
        )

        # Create CameraProperties
        camera_props = engine.CameraProperties(
            sensor_width_mm=camera.sensor_width_mm,
            sensor_height_mm=camera.sensor_height_mm,
            pixel_pitch_um=camera.pixel_pitch_um,
            read_noise_electrons=camera.read_noise_electrons_base,
            max_iso=camera.max_iso,
            iso_invariance_point=camera.iso_invariance_point
        )

        # Calculate optimal settings
        settings = engine.recommend_settings(
            target=target_props,
            camera=camera_props,
            focal_length_mm=focal_length_mm,
            aperture_fstop=aperture_fstop,
            sky_brightness=sky_brightness_mag,
            dec_deg=target.dec_deg,
            allow_tracking=False
        )

        print(f"\n   📊 RECOMMENDED SETTINGS:")
        print(f"   ├─ Shutter Speed: {settings.shutter_seconds}s")
        print(f"   ├─ ISO: {settings.iso}")
        print(f"   ├─ Aperture: f/{settings.aperture_fstop}")
        print(f"   ├─ Tracking Required: {settings.tracking_required}")
        print(f"   ├─ Predicted SNR: {settings.predicted_snr:.1f}")
        print(f"   ├─ Star Trailing: {settings.star_trailing_pixels:.2f} pixels")
        print(f"   └─ Dynamic Range: {settings.dynamic_range_stops:.1f} stops")

        # Multi-frame stacking recommendation
        num_frames = 100
        stacked_snr, improvement = engine.calculate_stacking_benefit(
            settings.predicted_snr,
            num_frames
        )

        total_time, integration_time = engine.calculate_total_integration_time(
            settings.shutter_seconds,
            num_frames
        )

        print(f"\n   📚 STACKING RECOMMENDATION:")
        print(f"   ├─ Frames: {num_frames}")
        print(f"   ├─ Stacked SNR: {stacked_snr:.1f} ({improvement:.1f}x improvement)")
        print(f"   ├─ Integration Time: {integration_time:.2f} hours")
        print(f"   └─ Total Session: {total_time:.2f} hours (with overhead)")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("IMAGING SESSION SUMMARY")
    print("=" * 80)

    print(f"\n✅ All systems nominal - ready for astrophotography!")
    print(f"\n📍 Location: {latitude}°N, {longitude}°W")
    print(f"🎯 Target: {target.name if target else 'N/A'}")
    print(f"📷 Camera: {camera.brand} {camera.model if camera else 'N/A'}")
    print(f"🌃 Sky: Bortle {bortle_class.value} ({sky_brightness_mag} mag/arcsec²)")
    print(f"🌙 Moon: {moon_illumination:.0f}% - {quality} conditions")
    if target and camera:
        print(f"⚙️  Settings: {settings.shutter_seconds}s @ ISO {settings.iso}, f/{aperture_fstop}")

    print("\n" + "=" * 80)
    print("This is instrument-grade astrophotography planning.")
    print("Built with precision. No shortcuts. Observatory-level thinking.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
