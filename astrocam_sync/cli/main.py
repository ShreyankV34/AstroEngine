"""
Command-line interface.

Main entry point for astrocam command.
"""
import click
from datetime import datetime
from typing import Optional


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    AstroCamSync - Real-time astrophotography decision engine.
    
    Computes optimal camera settings by fusing celestial mechanics,
    sensor physics, and live environmental data.
    """
    pass


@cli.command()
@click.option('--target', '-t', required=True, help='Target name (e.g., "Milky Way Core")')
@click.option('--camera', '-c', required=True, help='Camera model (e.g., "Sony A7 III")')
@click.option('--lens', '-l', type=float, required=True, help='Focal length in mm')
@click.option('--aperture', '-a', type=float, required=True, help='Aperture f-stop')
@click.option('--lat', type=float, help='Latitude (decimal degrees)')
@click.option('--lon', type=float, help='Longitude (decimal degrees)')
@click.option('--gps', is_flag=True, help='Use GPS for location (if available)')
@click.option('--bortle', type=int, help='Manual Bortle scale (1-9)')
@click.option('--time', type=str, help='Time (ISO format: 2025-01-15T03:00:00Z)')
@click.option('--live', is_flag=True, help='Use live weather data')
@click.option('--tracking', is_flag=True, help='Tracking mount available')
def recommend(
    target: str,
    camera: str,
    lens: float,
    aperture: float,
    lat: Optional[float],
    lon: Optional[float],
    gps: bool,
    bortle: Optional[int],
    time: Optional[str],
    live: bool,
    tracking: bool
):
    """Generate camera settings recommendation."""
    
    click.echo("🌌 AstroCamSync Decision Engine\n")
    click.echo("=" * 60)
    
    # Parse inputs
    try:
        # Get target
        from ..targets.catalog import get_target
        target_obj = get_target(target)
        
        if not target_obj:
            click.echo(f"❌ Target '{target}' not found")
            click.echo("\nUse 'astrocam targets' to list available targets")
            return
        
        # Get camera
        from ..cameras.database import get_camera
        camera_obj = get_camera(camera)
        
        if not camera_obj:
            click.echo(f"❌ Camera '{camera}' not found")
            click.echo("\nUse 'astrocam cameras' to list available cameras")
            return
        
        # Location
        if gps:
            click.echo("📍 GPS location not yet implemented")
            coords = (34.0522, -118.2437)  # Default
        elif lat and lon:
            coords = (lat, lon)
        else:
            coords = (34.0522, -118.2437)  # Default
        
        # Time
        if time:
            obs_time = datetime.fromisoformat(time.replace('Z', '+00:00'))
        else:
            obs_time = datetime.utcnow()
        
        # Calculate position
        from ..core.time import utc_to_lst
        from ..core.coordinates import equatorial_to_horizontal, calculate_airmass
        
        lst = utc_to_lst(obs_time, coords[1])
        alt, az = equatorial_to_horizontal(
            target_obj.ra_hours,
            target_obj.dec_deg,
            lst,
            coords[0]
        )
        airmass = calculate_airmass(alt)
        
        # Live conditions
        if live:
            from ..conditions.weather import get_astronomical_weather
            weather_data = get_astronomical_weather(coords[0], coords[1])
            sky_brightness = 19.5  # Would come from weather/SQM
        elif bortle:
            from ..conditions.light_pollution import bortle_to_sky_brightness
            sky_brightness = bortle_to_sky_brightness(bortle)
            weather_data = None
        else:
            sky_brightness = 19.5
            weather_data = None
            bortle = 5
        
        # Build decision inputs
        from ..sync.fusion import DecisionInput, fuse_decision
        
        inputs = DecisionInput(
            target_name=target_obj.name,
            target_brightness=target_obj.surface_brightness,
            target_type=target_obj.target_type,
            ra_hours=target_obj.ra_hours,
            dec_deg=target_obj.dec_deg,
            altitude_deg=alt,
            azimuth_deg=az,
            airmass=airmass,
            camera_name=camera_obj.name,
            pixel_pitch_um=camera_obj.pixel_pitch_um,
            read_noise_electrons=camera_obj.read_noise_electrons,
            iso_invariance_point=camera_obj.iso_invariance_point,
            focal_length_mm=lens,
            aperture_fstop=aperture,
            sky_brightness=sky_brightness,
            bortle=bortle if bortle else 5,
            cloud_cover=weather_data.get('cloud_cover_percent', 0) if weather_data else 0,
            humidity=weather_data.get('humidity_percent', 50) if weather_data else 50,
            wind_speed=weather_data.get('wind_speed_mph', 5) if weather_data else 5,
            temperature=weather_data.get('temperature_celsius', 20) if weather_data else 20,
            current_time=obs_time,
            allow_tracking=tracking
        )
        
        # Run decision fusion
        decision = fuse_decision(inputs)
        
        # Display results
        click.echo(f"\n📅 Time: {obs_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        click.echo(f"📍 Location: {coords[0]:.4f}°, {coords[1]:.4f}°")
        click.echo(f"🎯 Target: {target_obj.name}")
        click.echo(f"📷 Camera: {camera_obj.name}")
        click.echo(f"🔭 Lens: {lens}mm f/{aperture}")
        
        click.echo(f"\n🌟 VISIBILITY:")
        click.echo(f"  Altitude: {alt:.1f}°")
        click.echo(f"  Azimuth: {az:.1f}°")
        click.echo(f"  Airmass: {airmass:.2f}")
        
        if weather_data:
            click.echo(f"\n🌤️  CONDITIONS (Live):")
            click.echo(f"  Sky Brightness: {sky_brightness:.1f} mag/arcsec²")
            click.echo(f"  Cloud Cover: {weather_data['cloud_cover_percent']}%")
            click.echo(f"  Humidity: {weather_data['humidity_percent']}%")
            click.echo(f"  Wind: {weather_data['wind_speed_mph']} mph")
        else:
            click.echo(f"\n🌤️  CONDITIONS:")
            click.echo(f"  Sky Brightness: {sky_brightness:.1f} mag/arcsec²")
            click.echo(f"  Bortle: {bortle if bortle else 'Unknown'}")
        
        # Decision
        click.echo(f"\n{'✅' if decision.shootable else '❌'} DECISION:")
        click.echo(f"  Shootable: {'YES' if decision.shootable else 'NO'}")
        click.echo(f"  Quality: {decision.quality.upper()}")
        click.echo(f"  Confidence: {decision.confidence:.0%}")
        click.echo(f"  Reason: {decision.reason}")
        
        if decision.settings:
            click.echo(f"\n⚙️  SETTINGS:")
            click.echo(f"  Shutter: {decision.settings['shutter_seconds']}s")
            click.echo(f"  ISO: {decision.settings['iso']}")
            click.echo(f"  Aperture: f/{decision.settings['aperture_fstop']}")
            click.echo(f"  Tracking: {'Required' if decision.settings['tracking_required'] else 'Not needed'}")
        
        if decision.predictions:
            click.echo(f"\n📊 PREDICTIONS:")
            click.echo(f"  SNR: {decision.predictions['snr']:.1f}")
            click.echo(f"  Star Trailing: {decision.predictions['star_trailing_pixels']:.2f} pixels")
            click.echo(f"  Dynamic Range: {decision.predictions['dynamic_range_stops']:.1f} stops")
        
        if decision.warnings:
            click.echo(f"\n⚠️  WARNINGS:")
            for warning in decision.warnings:
                click.echo(f"  • {warning}")
        
        if decision.tips:
            click.echo(f"\n💡 TIPS:")
            for tip in decision.tips:
                click.echo(f"  • {tip}")
        
        click.echo("\n" + "=" * 60)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


@cli.command()
@click.option('--type', '-t', help='Filter by type (extended, point, moving)')
def targets(type: Optional[str]):
    """List available targets."""
    from ..targets.catalog import list_targets
    
    targets = list_targets(type)
    
    click.echo(f"\n🎯 Available Targets ({len(targets)}):\n")
    
    for target in targets:
        click.echo(f"• {target.name}")
        click.echo(f"  Type: {target.target_type}")
        click.echo(f"  Brightness: {target.surface_brightness} mag/arcsec²")
        click.echo(f"  Best months: {', '.join(target.best_months[:3])}")
        click.echo()


@cli.command()
@click.option('--manufacturer', '-m', help='Filter by manufacturer')
def cameras(manufacturer: Optional[str]):
    """List available cameras."""
    from ..cameras.database import list_cameras
    
    cameras_list = list_cameras(manufacturer=manufacturer)
    
    click.echo(f"\n📷 Available Cameras ({len(cameras_list)}):\n")
    
    for cam in cameras_list:
        click.echo(f"• {cam.name}")
        click.echo(f"  Sensor: {cam.sensor_type}")
        click.echo(f"  Resolution: {cam.resolution_mp}MP")
        click.echo(f"  Pixel Pitch: {cam.pixel_pitch_um}µm")
        click.echo(f"  ISO Invariance: {cam.iso_invariance_point}")
        click.echo()


if __name__ == '__main__':
    cli()