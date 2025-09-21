#!/usr/bin/env python3
"""
OpenRazer Basic System Test

This script performs basic tests to verify OpenRazer is working correctly.
Run this after installing OpenRazer to check if everything is set up properly.
"""

import sys
import subprocess
import importlib.util

def check_import(module_name):
    """Check if a module can be imported."""
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False

def run_command(command):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("OpenRazer Basic System Test")
    print("===========================")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Check for Razer devices
    print("\n1. Checking for Razer devices...")
    total_tests += 1
    
    success, stdout, stderr = run_command("lsusb | grep 1532")
    if success and stdout.strip():
        print("✓ Found Razer device(s):")
        for line in stdout.strip().split('\n'):
            print(f"  {line}")
        tests_passed += 1
    else:
        print("✗ No Razer devices found")
        print("  This is OK if you're testing with fake devices")
    
    # Test 2: Check kernel modules
    print("\n2. Checking kernel modules...")
    total_tests += 1
    
    success, stdout, stderr = run_command("lsmod | grep razer")
    if success and stdout.strip():
        print("✓ OpenRazer kernel modules loaded:")
        for line in stdout.strip().split('\n'):
            module_name = line.split()[0]
            print(f"  {module_name}")
        tests_passed += 1
    else:
        print("✗ No OpenRazer kernel modules loaded")
    
    # Test 3: Check Python library import
    print("\n3. Checking Python library...")
    total_tests += 1
    
    # Try to add local pylib to path for development testing
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    pylib_path = os.path.join(repo_root, 'pylib')
    
    if os.path.exists(pylib_path) and pylib_path not in sys.path:
        sys.path.insert(0, pylib_path)
    
    if check_import("openrazer.client"):
        print("✓ OpenRazer Python library can be imported")
        tests_passed += 1
    else:
        print("✗ Cannot import OpenRazer Python library")
        print("  Make sure openrazer is installed: pip3 install openrazer")
        print("  Or run from repository root with PYTHONPATH=pylib")
    
    # Test 4: Test device detection
    print("\n4. Testing device detection...")
    total_tests += 1
    
    try:
        from openrazer.client import DeviceManager
        device_manager = DeviceManager()
        device_count = len(device_manager.devices)
        
        if device_count > 0:
            print(f"✓ Found {device_count} device(s):")
            for device in device_manager.devices:
                print(f"  - {device.name} (Serial: {device.serial})")
            tests_passed += 1
        else:
            print("✗ No devices detected by OpenRazer")
            print("  This could be due to:")
            print("  - No physical devices connected")
            print("  - Permission issues")
            print("  - Driver not loaded")
    except Exception as e:
        print(f"✗ Error testing device detection: {e}")
    
    # Test 5: Check daemon status
    print("\n5. Checking daemon status...")
    total_tests += 1
    
    success, stdout, stderr = run_command("systemctl is-active openrazer-daemon")
    if success and "active" in stdout:
        print("✓ OpenRazer daemon is running")
        tests_passed += 1
    else:
        print("✗ OpenRazer daemon is not running")
        print("  Try: systemctl start openrazer-daemon")
    
    # Test 6: Test basic device functionality (if devices available)
    print("\n6. Testing basic device functionality...")
    total_tests += 1
    
    try:
        from openrazer.client import DeviceManager
        device_manager = DeviceManager()
        
        if len(device_manager.devices) > 0:
            device = device_manager.devices[0]
            print(f"  Testing with: {device.name}")
            
            # Test basic properties
            print(f"  - Type: {device.type}")
            print(f"  - Firmware: {device.firmware_version}")
            print(f"  - Driver: {device.driver_version}")
            
            # Test lighting (if supported)
            if hasattr(device, 'fx') and hasattr(device.fx, 'lighting_led_matrix'):
                try:
                    # Save current brightness
                    original_brightness = device.fx.lighting_led_matrix.brightness
                    
                    # Test setting brightness
                    device.fx.lighting_led_matrix.brightness = 128
                    current_brightness = device.fx.lighting_led_matrix.brightness
                    
                    if current_brightness == 128:
                        print("  - Brightness control: ✓")
                    else:
                        print("  - Brightness control: ✗")
                    
                    # Restore original brightness
                    device.fx.lighting_led_matrix.brightness = original_brightness
                    
                except Exception as e:
                    print(f"  - Lighting test failed: {e}")
            
            tests_passed += 1
        else:
            print("  Skipped - no devices available")
            tests_passed += 1  # Don't penalize for no devices
            
    except Exception as e:
        print(f"✗ Error testing device functionality: {e}")
    
    # Summary
    print(f"\n{'='*40}")
    print(f"Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! OpenRazer appears to be working correctly.")
        return 0
    elif tests_passed >= total_tests - 1:
        print("⚠️  Most tests passed. Minor issues detected.")
        return 0
    else:
        print("❌ Multiple tests failed. Please check the issues above.")
        print("\nFor troubleshooting help, see DEBUGGING_AND_TESTING.md")
        print("or run: ./scripts/troubleshoot.sh")
        return 1

if __name__ == "__main__":
    sys.exit(main())