#!/usr/bin/env python3
"""
OpenRazer Device Capability Test

This script tests the capabilities of connected OpenRazer devices.
It's useful for verifying what features are available on your specific hardware.
"""

import time
import sys
from openrazer.client import DeviceManager
from openrazer.client.debug import print_attrs


def test_device_info(device):
    """Test basic device information."""
    print(f"\n=== {device.name} ===")
    print(f"Type: {device.type}")
    print(f"Serial: {device.serial}")
    print(f"Firmware: {device.firmware_version}")
    print(f"Driver: {device.driver_version}")
    
    # Additional device info if available
    if hasattr(device, 'device_mode'):
        print(f"Device Mode: {device.device_mode}")
    
    if hasattr(device, 'poll_rate'):
        try:
            print(f"Poll Rate: {device.poll_rate}")
        except:
            print("Poll Rate: Not readable")


def test_lighting_capabilities(device):
    """Test lighting capabilities."""
    print(f"\n--- Lighting Capabilities for {device.name} ---")
    
    if not hasattr(device, 'fx'):
        print("No lighting effects available")
        return False
    
    fx = device.fx
    has_lighting = False
    
    # Check for matrix lighting
    if hasattr(fx, 'lighting_led_matrix'):
        print("✓ Matrix lighting available")
        has_lighting = True
        
        matrix = fx.lighting_led_matrix
        
        # Test brightness
        try:
            original_brightness = matrix.brightness
            print(f"  Current brightness: {original_brightness}")
            
            # Test setting brightness
            matrix.brightness = 128
            time.sleep(0.1)
            new_brightness = matrix.brightness
            print(f"  Set brightness to 128, got: {new_brightness}")
            
            # Restore original brightness
            matrix.brightness = original_brightness
            print("  ✓ Brightness control working")
        except Exception as e:
            print(f"  ✗ Brightness control failed: {e}")
        
        # Test static color
        try:
            matrix.static(255, 0, 0)  # Red
            print("  ✓ Static red color set")
            time.sleep(0.5)
            
            matrix.static(0, 255, 0)  # Green
            print("  ✓ Static green color set")
            time.sleep(0.5)
            
            matrix.static(0, 0, 255)  # Blue
            print("  ✓ Static blue color set")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ Static color failed: {e}")
        
        # Test other effects
        effects_to_test = [
            ('breath_random', 'Random breathing'),
            ('wave', 'Wave effect'),
            ('reactive', 'Reactive effect'),
            ('spectrum', 'Spectrum cycling'),
        ]
        
        for effect_name, description in effects_to_test:
            if hasattr(matrix, effect_name):
                try:
                    getattr(matrix, effect_name)()
                    print(f"  ✓ {description} working")
                    time.sleep(1)
                except Exception as e:
                    print(f"  ✗ {description} failed: {e}")
    
    # Check for logo lighting
    if hasattr(fx, 'lighting_logo'):
        print("✓ Logo lighting available")
        has_lighting = True
        
        try:
            fx.lighting_logo.static(255, 255, 255)  # White
            print("  ✓ Logo static color working")
        except Exception as e:
            print(f"  ✗ Logo lighting failed: {e}")
    
    # Check for scroll wheel lighting
    if hasattr(fx, 'lighting_scroll'):
        print("✓ Scroll wheel lighting available")
        has_lighting = True
        
        try:
            fx.lighting_scroll.static(255, 255, 0)  # Yellow
            print("  ✓ Scroll wheel static color working")
        except Exception as e:
            print(f"  ✗ Scroll wheel lighting failed: {e}")
    
    return has_lighting


def test_other_capabilities(device):
    """Test other device capabilities."""
    print(f"\n--- Other Capabilities for {device.name} ---")
    
    capabilities_tested = 0
    
    # Test DPI (for mice)
    if hasattr(device, 'dpi'):
        try:
            original_dpi = device.dpi
            print(f"  Current DPI: {original_dpi}")
            
            # Test setting DPI
            if hasattr(device, 'available_dpi'):
                available = device.available_dpi
                print(f"  Available DPI: {available}")
            
            capabilities_tested += 1
        except Exception as e:
            print(f"  ✗ DPI test failed: {e}")
    
    # Test battery (for wireless devices)
    if hasattr(device, 'battery_level'):
        try:
            battery = device.battery_level
            print(f"  Battery level: {battery}%")
            capabilities_tested += 1
        except Exception as e:
            print(f"  ✗ Battery test failed: {e}")
    
    # Test charging status
    if hasattr(device, 'is_charging'):
        try:
            charging = device.is_charging
            print(f"  Charging: {charging}")
            capabilities_tested += 1
        except Exception as e:
            print(f"  ✗ Charging status test failed: {e}")
    
    # Test idle time
    if hasattr(device, 'idle_time'):
        try:
            idle = device.idle_time
            print(f"  Idle time: {idle} seconds")
            capabilities_tested += 1
        except Exception as e:
            print(f"  ✗ Idle time test failed: {e}")
    
    # Test game mode
    if hasattr(device, 'game_mode_led'):
        try:
            game_mode = device.game_mode_led
            print(f"  Game mode LED: {game_mode}")
            capabilities_tested += 1
        except Exception as e:
            print(f"  ✗ Game mode test failed: {e}")
    
    if capabilities_tested == 0:
        print("  No additional capabilities detected")
    
    return capabilities_tested > 0


def main():
    print("OpenRazer Device Capability Test")
    print("=================================")
    
    try:
        device_manager = DeviceManager()
    except Exception as e:
        print(f"Error connecting to OpenRazer daemon: {e}")
        print("Make sure the daemon is running: systemctl start openrazer-daemon")
        return 1
    
    devices = device_manager.devices
    
    if not devices:
        print("No OpenRazer devices found.")
        print("This could mean:")
        print("- No physical devices are connected")
        print("- Devices are not recognized by OpenRazer")
        print("- Driver issues")
        print("\nFor testing without hardware, try: ./scripts/quick_test_setup.sh")
        return 1
    
    print(f"Found {len(devices)} device(s)")
    
    # Test each device
    for i, device in enumerate(devices):
        test_device_info(device)
        
        has_lighting = test_lighting_capabilities(device)
        has_other = test_other_capabilities(device)
        
        if not has_lighting and not has_other:
            print(f"\n--- Detailed Capabilities for {device.name} ---")
            print("Use this for debugging:")
            print_attrs(device)
        
        # Add separator between devices
        if i < len(devices) - 1:
            print("\n" + "="*50)
    
    print(f"\nTesting completed for {len(devices)} device(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())