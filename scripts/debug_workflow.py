#!/usr/bin/env python3
"""
OpenRazer Debug Workflow

This script demonstrates a systematic approach to debugging OpenRazer issues.
It walks through the debugging process step by step, similar to what a user
might do when troubleshooting their setup.
"""

import sys
import os
import subprocess
import time


def run_command(command, description="Running command"):
    """Run a command and capture output."""
    print(f"\n{description}...")
    print(f"$ {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print(f"Exit code: {result.returncode}")
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print("Command timed out!")
        return False, "", "Timeout"
    except Exception as e:
        print(f"Error running command: {e}")
        return False, "", str(e)


def check_step(step_name, condition, success_msg, failure_msg, tip=""):
    """Check a debugging step and provide feedback."""
    print(f"\n{'='*50}")
    print(f"STEP: {step_name}")
    print('='*50)
    
    if condition:
        print(f"✓ {success_msg}")
        return True
    else:
        print(f"✗ {failure_msg}")
        if tip:
            print(f"TIP: {tip}")
        return False


def main():
    print("OpenRazer Debug Workflow")
    print("=" * 60)
    print("This script walks through a systematic debugging process")
    print("for OpenRazer. Follow along to identify issues with your setup.")
    print("=" * 60)
    
    issues_found = []
    
    # Step 1: Check for hardware
    success, stdout, stderr = run_command("lsusb | grep 1532", "Checking for Razer devices")
    has_hardware = check_step(
        "Hardware Detection",
        success and stdout.strip(),
        f"Found Razer device(s):\n{stdout}",
        "No Razer devices detected by USB subsystem",
        "Try a different USB port or check if device is powered on"
    )
    
    if not has_hardware:
        issues_found.append("No hardware detected")
        print("\nINFO: Continuing with software checks...")
    
    # Step 2: Check kernel modules
    success, stdout, stderr = run_command("lsmod | grep razer", "Checking kernel modules")
    has_modules = check_step(
        "Kernel Module Loading",
        success and stdout.strip(),
        f"OpenRazer modules loaded:\n{stdout}",
        "No OpenRazer kernel modules loaded",
        "Try: sudo modprobe razerkbd razermouse razeraccessory"
    )
    
    if not has_modules:
        issues_found.append("Kernel modules not loaded")
        
        # Try to check DKMS status
        success, stdout, stderr = run_command("dkms status openrazer-driver", "Checking DKMS status")
        if success and stdout.strip():
            print(f"DKMS status:\n{stdout}")
        else:
            print("DKMS module not found or not installed")
    
    # Step 3: Check module installation
    success, stdout, stderr = run_command("find /lib/modules/$(uname -r) -name '*razer*'", "Checking module files")
    has_module_files = check_step(
        "Module Files",
        success and stdout.strip(),
        f"Found module files:\n{stdout}",
        "No OpenRazer module files found",
        "Try reinstalling OpenRazer or check DKMS installation"
    )
    
    if not has_module_files:
        issues_found.append("Module files missing")
    
    # Step 4: Check device files in sysfs
    if has_hardware and has_modules:
        success, stdout, stderr = run_command("find /sys/bus/hid/drivers/razer* -name '*1532*' 2>/dev/null", "Checking device files")
        has_device_files = check_step(
            "Device Files",
            success and stdout.strip(),
            f"Found device files:\n{stdout}",
            "No device files in sysfs",
            "Check if modules recognize your specific device model"
        )
        
        if not has_device_files:
            issues_found.append("Device files not created")
    
    # Step 5: Check daemon
    success, stdout, stderr = run_command("systemctl is-active openrazer-daemon", "Checking daemon status")
    daemon_running = check_step(
        "Daemon Status",
        success and "active" in stdout,
        "OpenRazer daemon is running",
        "OpenRazer daemon is not running",
        "Try: systemctl start openrazer-daemon"
    )
    
    if not daemon_running:
        issues_found.append("Daemon not running")
        
        # Check daemon logs
        success, stdout, stderr = run_command("journalctl -u openrazer-daemon --no-pager -n 10", "Checking daemon logs")
        if success and stdout.strip():
            print(f"Recent daemon logs:\n{stdout}")
    
    # Step 6: Check Python library
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    pylib_path = os.path.join(repo_root, 'pylib')
    
    # Set PYTHONPATH for local testing
    env = os.environ.copy()
    if os.path.exists(pylib_path):
        env['PYTHONPATH'] = pylib_path + ':' + env.get('PYTHONPATH', '')
    
    success, stdout, stderr = run_command("python3 -c 'from openrazer.client import DeviceManager; print(\"Import successful\")'", "Testing Python library import")
    python_works = check_step(
        "Python Library",
        success,
        "OpenRazer Python library imported successfully",
        f"Failed to import OpenRazer Python library:\n{stderr}",
        "Try: pip3 install openrazer"
    )
    
    if not python_works:
        issues_found.append("Python library import failed")
    
    # Step 7: Test device detection (if Python works)
    if python_works:
        test_script = """
import os, sys
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
pylib_path = os.path.join(repo_root, 'pylib')
if os.path.exists(pylib_path):
    sys.path.insert(0, pylib_path)

try:
    from openrazer.client import DeviceManager
    dm = DeviceManager()
    print(f'Found {len(dm.devices)} devices')
    for device in dm.devices:
        print(f'  - {device.name}')
except Exception as e:
    print(f'Error: {e}')
    exit(1)
"""
        with open('/tmp/test_devices.py', 'w') as f:
            f.write(test_script)
        
        success, stdout, stderr = run_command("python3 /tmp/test_devices.py", "Testing device detection")
        devices_detected = check_step(
            "Device Detection",
            success and "Found" in stdout,
            f"Device detection successful:\n{stdout}",
            f"Device detection failed:\n{stderr}",
            "Check hardware connection and permissions"
        )
        
        if not devices_detected:
            issues_found.append("Device detection failed")
        
        # Clean up
        try:
            os.remove('/tmp/test_devices.py')
        except:
            pass
    
    # Step 8: Check permissions
    success, stdout, stderr = run_command("groups | grep plugdev", "Checking user groups")
    has_plugdev = check_step(
        "User Permissions",
        success,
        "User is in 'plugdev' group",
        "User is not in 'plugdev' group",
        "Try: sudo usermod -a -G plugdev $USER (then logout/login)"
    )
    
    if not has_plugdev:
        issues_found.append("User not in plugdev group")
    
    # Summary
    print(f"\n{'='*60}")
    print("DEBUG SUMMARY")
    print('='*60)
    
    if not issues_found:
        print("🎉 No issues detected! OpenRazer should be working correctly.")
        print("\nIf you're still experiencing problems:")
        print("- Try running: python3 scripts/test_system.py")
        print("- Check device-specific issues with scripts in scripts/driver/")
        print("- Look for more help in DEBUGGING_AND_TESTING.md")
    else:
        print(f"❌ Found {len(issues_found)} issue(s):")
        for i, issue in enumerate(issues_found, 1):
            print(f"  {i}. {issue}")
        
        print("\nNEXT STEPS:")
        if "No hardware detected" in issues_found:
            print("1. Verify your Razer device is connected and powered on")
            print("2. Try a different USB port")
            print("3. Check if device is supported (see README.md)")
        
        if "Kernel modules not loaded" in issues_found or "Module files missing" in issues_found:
            print("1. Reinstall OpenRazer kernel modules")
            print("2. Check for secure boot issues")
            print("3. Verify kernel headers are installed")
        
        if "Daemon not running" in issues_found:
            print("1. Start daemon: systemctl start openrazer-daemon")
            print("2. Enable on boot: systemctl enable openrazer-daemon")
            print("3. Check daemon logs: journalctl -u openrazer-daemon")
        
        if "Python library import failed" in issues_found:
            print("1. Install Python library: pip3 install openrazer")
            print("2. Check dependencies are installed")
        
        if "User not in plugdev group" in issues_found:
            print("1. Add user to group: sudo usermod -a -G plugdev $USER")
            print("2. Logout and login again")
        
        print("\nFor detailed troubleshooting, see DEBUGGING_AND_TESTING.md")
    
    return len(issues_found)


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nDebugging interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)