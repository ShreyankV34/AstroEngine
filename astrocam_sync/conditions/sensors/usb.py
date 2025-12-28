"""
USB sensor protocol.

Direct USB/Serial communication with SQM devices.
"""
from typing import Optional


class USBSensor:
    """
    USB/Serial sensor interface.
    
    For direct serial communication with SQM-LU and similar devices.
    """
    
    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 115200):
        """
        Initialize USB sensor.
        
        Args:
            port: Serial port (e.g., /dev/ttyUSB0 or COM3)
            baudrate: Communication speed
        """
        self.port = port
        self.baudrate = baudrate
        self.connected = False
    
    def list_ports(self) -> list:
        """
        List available USB serial ports.
        
        Returns:
            List of available ports
        """
        # Placeholder - would use pyserial
        print("Available ports:")
        return ["/dev/ttyUSB0", "/dev/ttyUSB1", "COM3", "COM4"]
    
    def connect(self) -> bool:
        """
        Connect to USB sensor.
        
        Returns:
            True if connected
        """
        print(f"Opening serial port {self.port}...")
        # Would use pyserial here:
        # self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
        self.connected = False
        return self.connected
    
    def disconnect(self):
        """Close serial connection."""
        if self.connected:
            # self.serial.close()
            self.connected = False
    
    def read_raw(self) -> Optional[str]:
        """
        Read raw data from sensor.
        
        Returns:
            Raw sensor response or None
        """
        if not self.connected:
            return None
        
        # Placeholder - would read from serial port
        # return self.serial.readline().decode('utf-8').strip()
        return "r, 19.50m,0000000023Hz,0000000C, 018.5C"
    
    def parse_sqm_response(self, response: str) -> Optional[dict]:
        """
        Parse SQM device response.
        
        SQM format: "r, 19.50m,0000000023Hz,0000000C, 018.5C"
        
        Args:
            response: Raw response string
            
        Returns:
            Parsed data dict
        """
        if not response:
            return None
        
        try:
            parts = response.split(',')
            
            # Extract brightness (mag/arcsec²)
            brightness_str = parts[1].strip().replace('m', '')
            brightness = float(brightness_str)
            
            # Extract temperature
            temp_str = parts[4].strip().replace('C', '')
            temperature = float(temp_str)
            
            return {
                "brightness": brightness,
                "temperature": temperature,
                "raw_response": response
            }
        
        except (IndexError, ValueError) as e:
            print(f"Error parsing SQM response: {e}")
            return None


# Example usage
if __name__ == "__main__":
    print("USB Sensor Protocol - SQM-LU Support\n")
    
    sensor = USBSensor(port="/dev/ttyUSB0")
    
    print("Available ports:")
    for port in sensor.list_ports():
        print(f"  • {port}")
    
    print("\nExample SQM response parsing:")
    raw = "r, 19.50m,0000000023Hz,0000000C, 018.5C"
    parsed = sensor.parse_sqm_response(raw)
    
    if parsed:
        print(f"  Brightness: {parsed['brightness']} mag/arcsec²")
        print(f"  Temperature: {parsed['temperature']}°C")
    
    print("\n" + "="*50)
    print("Real Usage:")
    print("  pip install pyserial")
    print("  from astrocam_sync.conditions.sensors import USBSensor")
    print("  sensor = USBSensor(port='/dev/ttyUSB0')")
    print("  sensor.connect()")
    print("  data = sensor.read_raw()")