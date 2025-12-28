"""
Sky Quality Meter (SQM) integration.

Supports Unihedron SQM-LU and SQM-LE devices for direct
sky brightness measurements.
"""
from typing import Optional, Dict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SQMReading:
    """Sky Quality Meter reading."""
    brightness: float  # mag/arcsec²
    temperature: float  # Celsius
    timestamp: datetime
    device_id: str
    quality: str  # 'excellent', 'good', 'fair', 'poor'


class SQMDevice:
    """
    Base class for Sky Quality Meter devices.
    
    SQM directly measures sky brightness in mag/arcsec²,
    which is much more accurate than Bortle scale estimates.
    """
    
    def __init__(self, device_id: str = "SQM-LU"):
        """
        Initialize SQM device.
        
        Args:
            device_id: Device identifier
        """
        self.device_id = device_id
        self.connected = False
    
    def connect(self) -> bool:
        """
        Connect to SQM device.
        
        Returns:
            True if connected successfully
        """
        # Placeholder - actual implementation would use serial/bluetooth
        print(f"Connecting to {self.device_id}...")
        self.connected = True
        return True
    
    def disconnect(self):
        """Disconnect from device."""
        self.connected = False
        print(f"Disconnected from {self.device_id}")
    
    def read(self) -> Optional[SQMReading]:
        """
        Read current sky brightness.
        
        Returns:
            SQMReading or None if error
        """
        if not self.connected:
            print("Device not connected")
            return None
        
        # Placeholder - would read from actual device
        return self._simulate_reading()
    
    def _simulate_reading(self) -> SQMReading:
        """Simulate SQM reading for testing."""
        # Typical reading: 19.5 mag/arcsec² (Bortle 4-5)
        brightness = 19.5
        temperature = 18.5
        
        # Quality assessment
        if brightness >= 21.5:
            quality = "excellent"
        elif brightness >= 20.0:
            quality = "good"
        elif brightness >= 18.5:
            quality = "fair"
        else:
            quality = "poor"
        
        return SQMReading(
            brightness=brightness,
            temperature=temperature,
            timestamp=datetime.utcnow(),
            device_id=self.device_id,
            quality=quality
        )


class SQM_LU(SQMDevice):
    """
    Unihedron SQM-LU (USB version).
    
    USB connection, typically used with computer control.
    """
    
    def __init__(self, port: str = "/dev/ttyUSB0"):
        """
        Initialize SQM-LU device.
        
        Args:
            port: USB serial port
        """
        super().__init__("SQM-LU")
        self.port = port


class SQM_LE(SQMDevice):
    """
    Unihedron SQM-LE (Ethernet version).
    
    Network connection for remote mounting.
    """
    
    def __init__(self, ip_address: str = "192.168.1.100"):
        """
        Initialize SQM-LE device.
        
        Args:
            ip_address: Device IP address
        """
        super().__init__("SQM-LE")
        self.ip_address = ip_address


def parse_sqm_reading(reading: SQMReading) -> Dict[str, any]:
    """
    Parse SQM reading into useful information.
    
    Args:
        reading: SQM reading
        
    Returns:
        Detailed sky conditions
    """
    from ..light_pollution import sky_brightness_to_bortle
    
    bortle = sky_brightness_to_bortle(reading.brightness)
    
    # Quality assessment
    if reading.brightness >= 21.5:
        description = "Exceptional dark sky - pristine conditions"
        color = "darkgreen"
    elif reading.brightness >= 21.0:
        description = "Excellent dark sky - near-perfect"
        color = "green"
    elif reading.brightness >= 20.0:
        description = "Good dark sky - rural site"
        color = "lightgreen"
    elif reading.brightness >= 19.0:
        description = "Fair sky - light pollution present"
        color = "yellow"
    elif reading.brightness >= 18.0:
        description = "Moderate light pollution"
        color = "orange"
    else:
        description = "Heavy light pollution"
        color = "red"
    
    # Milky Way visibility
    if reading.brightness >= 21.0:
        mw_visible = "Excellent - detailed structure visible"
    elif reading.brightness >= 20.0:
        mw_visible = "Good - clearly visible"
    elif reading.brightness >= 19.0:
        mw_visible = "Fair - visible but washed out"
    else:
        mw_visible = "Poor - barely visible or invisible"
    
    return {
        "brightness": reading.brightness,
        "bortle": bortle,
        "quality": reading.quality,
        "description": description,
        "color": color,
        "milky_way_visibility": mw_visible,
        "temperature": reading.temperature,
        "timestamp": reading.timestamp,
        "device": reading.device_id
    }


def continuous_monitoring(
    device: SQMDevice,
    duration_minutes: int = 60,
    interval_seconds: int = 60
) -> list:
    """
    Continuously monitor sky brightness.
    
    Args:
        device: SQM device
        duration_minutes: How long to monitor
        interval_seconds: Time between readings
        
    Returns:
        List of readings
    """
    readings = []
    
    if not device.connect():
        return readings
    
    try:
        import time
        end_time = time.time() + (duration_minutes * 60)
        
        while time.time() < end_time:
            reading = device.read()
            if reading:
                readings.append(reading)
                print(f"Sky: {reading.brightness:.2f} mag/arcsec² "
                      f"(Temp: {reading.temperature:.1f}°C)")
            
            time.sleep(interval_seconds)
    
    finally:
        device.disconnect()
    
    return readings


# Example usage
if __name__ == "__main__":
    print("=== Sky Quality Meter Demo ===\n")
    
    # Initialize device
    sqm = SQM_LU()
    
    # Connect and read
    if sqm.connect():
        print("Device connected!\n")
        
        # Single reading
        reading = sqm.read()
        
        if reading:
            print(f"Raw Reading:")
            print(f"  Brightness: {reading.brightness:.2f} mag/arcsec²")
            print(f"  Temperature: {reading.temperature:.1f}°C")
            print(f"  Quality: {reading.quality}")
            print(f"  Time: {reading.timestamp}")
            
            # Parse reading
            parsed = parse_sqm_reading(reading)
            
            print(f"\nParsed Conditions:")
            print(f"  Bortle Class: {parsed['bortle']}")
            print(f"  Description: {parsed['description']}")
            print(f"  Milky Way: {parsed['milky_way_visibility']}")
        
        sqm.disconnect()
    
    print("\n" + "="*50)
    print("Real Device Usage:")
    print("  from astrocam_sync.conditions.sensors import SQM_LU")
    print("  sqm = SQM_LU(port='/dev/ttyUSB0')")
    print("  sqm.connect()")
    print("  reading = sqm.read()")
    print("\nSupported Devices:")
    print("  • Unihedron SQM-LU (USB)")
    print("  • Unihedron SQM-LE (Ethernet)")
    