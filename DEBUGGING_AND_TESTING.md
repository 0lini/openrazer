# Debugging and Testing OpenRazer

This guide provides comprehensive instructions for debugging and testing OpenRazer on your system, whether you have physical Razer devices or want to test without hardware.

## Quick Diagnostics

### Automated System Test

OpenRazer includes a comprehensive system test script:

```bash
python3 scripts/test_system.py
```

This script will:
- Check for connected Razer devices
- Verify kernel modules are loaded
- Test Python library import
- Validate device detection
- Check daemon status
- Test basic device functionality

### Quick Test Setup (No Hardware Required)

To quickly test OpenRazer without physical devices:

```bash
./scripts/quick_test_setup.sh
```

This will create fake devices and start a test daemon automatically.

### Legacy Troubleshooting Script

OpenRazer also includes an older troubleshooting script:

```bash
./scripts/troubleshoot.sh
```

This script will:
- Check if Razer devices are connected
- Verify kernel modules are loaded
- Test daemon permissions
- Validate the Python library can detect devices

### Manual System Check

If you prefer to diagnose issues manually, follow these steps:

#### 1. Check for Connected Razer Devices

```bash
# List all USB devices and filter for Razer (VID: 1532)
lsusb | grep 1532
```

Example output:
```
Bus 003 Device 012: ID 1532:0c05 Razer USA, Ltd Razer Strider Chroma
```

#### 2. Verify Kernel Modules

```bash
# Check if OpenRazer kernel modules are loaded
lsmod | grep razer

# Check specific modules
lsmod | grep -E "(razerkbd|razermouse|razeraccessory)"
```

#### 3. Check Driver Installation

```bash
# Check DKMS installation status
sudo dkms status openrazer-driver

# Manual module loading (if needed)
sudo modprobe razerkbd
sudo modprobe razermouse
sudo modprobe razeraccessory
```

#### 4. Verify Device Files

```bash
# Check if device files are created in sysfs
find /sys/bus/hid/drivers/razer* -name "*1532*" 2>/dev/null

# Example: Check specific device attributes
ls -la /sys/bus/hid/drivers/razerkbd/0003:1532:XXXX.*/
```

#### 5. Test Daemon

```bash
# Stop existing daemon
sudo systemctl stop openrazer-daemon

# Run daemon in foreground with verbose logging
openrazer-daemon -v -F

# Or with specific log directory
mkdir -p /tmp/razer_logs
openrazer-daemon -v -F --log-dir=/tmp/razer_logs
```

## Testing Without Physical Hardware

### Using Fake Devices

OpenRazer provides a sophisticated fake device system for testing without physical hardware:

#### GUI Setup (Recommended)

```bash
# Run the fake device setup script (requires zenity)
./scripts/setup_fake_devices.sh
```

This will:
1. Show a GUI to select which devices to simulate
2. Start fake devices in test directory
3. Launch daemon with test configuration

#### Manual Setup

```bash
# Create directories
mkdir -p /tmp/daemon_config/{data,logs}
mkdir -p /tmp/daemon_test

# Create fake devices (example: keyboard and mouse)
./scripts/create_fake_device.py --dest /tmp/daemon_test razer_blackwidow_chroma razer_deathadder_chroma

# Start daemon with test configuration
PYTHONPATH="pylib:daemon" python3 ./daemon/run_openrazer_daemon.py \
    -Fv --test-dir /tmp/daemon_test \
    --run-dir /tmp/daemon_config/data \
    --log-dir /tmp/daemon_config/logs
```

#### Available Fake Devices

```bash
# List all available fake device configurations
ls pylib/openrazer/_fake_driver/*.cfg
```

## Device-Specific Testing

### Driver-Level Testing

OpenRazer includes device-specific test scripts that directly interact with the kernel driver:

```bash
# Test specific device types (replace with your device)
python3 scripts/driver/goliathus/test.py
python3 scripts/driver/firefly/test.py
python3 scripts/driver/blackwidow_chroma_keyboard/test.py
python3 scripts/driver/mamba_chroma_wireless_mouse/test.py
```

These scripts will:
- Test device detection
- Verify driver communication
- Test lighting effects
- Check device-specific features

### Python Library Testing

#### Basic Device Detection

```python
#!/usr/bin/env python3
from openrazer.client import DeviceManager

# Create device manager
device_manager = DeviceManager()

print(f"Found {len(device_manager.devices)} Razer devices")

for device in device_manager.devices:
    print(f"Device: {device.name}")
    print(f"  Type: {device.type}")
    print(f"  Serial: {device.serial}")
    print(f"  Firmware: {device.firmware_version}")
    print(f"  Driver: {device.driver_version}")
    print()
```

#### Test Device Capabilities

```python
#!/usr/bin/env python3
from openrazer.client import DeviceManager
from openrazer.client.debug import print_attrs

device_manager = DeviceManager()

for device in device_manager.devices:
    print(f"=== {device.name} ===")
    
    # Print all available methods and properties
    print_attrs(device)
    
    # Test basic lighting (if supported)
    if device.fx.has('lighting_led_matrix'):
        print("Testing matrix lighting...")
        device.fx.lighting_led_matrix.brightness = 255
        device.fx.lighting_led_matrix.static(255, 0, 0)  # Red
```

#### Advanced Testing

```python
#!/usr/bin/env python3
from openrazer.client import DeviceManager
import time

device_manager = DeviceManager()

for device in device_manager.devices:
    print(f"Testing {device.name}...")
    
    # Test all available lighting effects
    if hasattr(device.fx, 'lighting_led_matrix'):
        matrix = device.fx.lighting_led_matrix
        
        # Test static colors
        matrix.static(255, 0, 0)  # Red
        time.sleep(1)
        matrix.static(0, 255, 0)  # Green
        time.sleep(1)
        matrix.static(0, 0, 255)  # Blue
        time.sleep(1)
        
        # Test breathing effect
        if hasattr(matrix, 'breath_random'):
            matrix.breath_random()
            time.sleep(3)
        
        # Test wave effect
        if hasattr(matrix, 'wave'):
            matrix.wave(1)  # Direction 1
            time.sleep(3)
```

#### Comprehensive Device Testing

For a complete test of device capabilities, use the provided example:

```bash
python3 examples/test_device_capabilities.py
```

This script will:
- Test all device information (serial, firmware, etc.)
- Test all lighting capabilities (matrix, logo, scroll wheel)
- Test device-specific features (DPI, battery, etc.)
- Provide detailed debugging output for unsupported features

## Debugging Common Issues

### Permission Problems

```bash
# Check user groups
groups $USER

# Add user to plugdev group (logout/login required)
sudo usermod -a -G plugdev $USER

# Check file permissions
ls -la /sys/bus/hid/drivers/razer*/*/

# Fix permissions (if needed)
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Secure Boot Issues

```bash
# Check if secure boot is causing module loading issues
sudo dmesg | grep -i "required key not available"

# If secure boot is enabled, you need to:
# 1. Disable secure boot in BIOS/UEFI, OR
# 2. Sign the kernel modules (advanced)
```

### Module Loading Issues

```bash
# Check module dependencies
modinfo razerkbd
modinfo razermouse
modinfo razeraccessory

# Force reload modules
sudo rmmod razerkbd razermouse razeraccessory
sudo modprobe razerkbd
sudo modprobe razermouse
sudo modprobe razeraccessory

# Check for errors
dmesg | tail -20
```

### Daemon Issues

```bash
# Check daemon status
systemctl status openrazer-daemon

# Check daemon logs
journalctl -u openrazer-daemon -f

# Manual daemon startup with debug
openrazer-daemon -v -F

# Check daemon socket
ls -la /run/openrazer-daemon/
```

## Log Analysis

### Kernel Module Logs

```bash
# Real-time kernel logs
sudo dmesg -w | grep -i razer

# Check for specific errors
dmesg | grep -E "(razer|1532)" | tail -20

# Module loading messages
dmesg | grep -E "(razerkbd|razermouse|razeraccessory)"
```

### Daemon Logs

```bash
# System daemon logs
journalctl -u openrazer-daemon --since "1 hour ago"

# Custom log directory
tail -f /tmp/razer_logs/razer.log

# Debug level logging
openrazer-daemon -v -F 2>&1 | tee debug.log
```

### USB Communication Logs

```bash
# Monitor USB traffic (requires root)
sudo modprobe usbmon
sudo tcpdump -i usbmon1 -w usb_capture.pcap

# Or use wireshark with USB capture
# See scripts/wireshark/ for protocol dissectors
```

## Development Testing

### Building and Testing Changes

```bash
# Build kernel modules
make driver

# Install modules for testing
sudo rmmod razerkbd razermouse razeraccessory
sudo insmod driver/razerkbd.ko
sudo insmod driver/razermouse.ko
sudo insmod driver/razeraccessory.ko

# Test daemon with local changes
PYTHONPATH="pylib:daemon" python3 ./daemon/run_openrazer_daemon.py -Fv
```

### Continuous Integration Tests

```bash
# Run the same tests as CI
./scripts/ci/test-daemon.sh
python3 scripts/ci/test-daemon.py
python3 scripts/ci/test-pids.py
```

## Advanced Debugging

### Using GDB with Daemon

```bash
# Install debug symbols (if available)
sudo apt install python3-dbg

# Run daemon under GDB
gdb --args python3 ./daemon/run_openrazer_daemon.py -Fv
```

### Kernel Module Debugging

```bash
# Enable dynamic debug for modules
echo 'module razerkbd +p' | sudo tee /sys/kernel/debug/dynamic_debug/control
echo 'module razermouse +p' | sudo tee /sys/kernel/debug/dynamic_debug/control

# Monitor with dmesg
sudo dmesg -w
```

### Network Debugging (for some devices)

```bash
# Some devices communicate over network protocols
# Monitor network traffic
sudo tcpdump -i any port 8080

# Or use netstat to check listening ports
netstat -tlnp | grep razer
```

## Performance Testing

### Latency Testing

```python
#!/usr/bin/env python3
import time
from openrazer.client import DeviceManager

device_manager = DeviceManager()
device = device_manager.devices[0]

# Test lighting change latency
start_time = time.time()
for i in range(100):
    device.fx.lighting_led_matrix.static(i % 255, 0, 0)
end_time = time.time()

print(f"100 lighting changes took {end_time - start_time:.2f} seconds")
print(f"Average latency: {(end_time - start_time) / 100 * 1000:.2f} ms")
```

### Memory Usage

```bash
# Monitor daemon memory usage
ps aux | grep openrazer-daemon

# Continuous monitoring
watch 'ps aux | grep openrazer-daemon'

# Detailed memory analysis
sudo pmap $(pgrep openrazer-daemon)
```

## Contributing Test Results

When reporting issues or contributing, please include:

1. Output of `./scripts/troubleshoot.sh`
2. `lsusb | grep 1532` output
3. `dmesg | grep -i razer` output
4. `journalctl -u openrazer-daemon --since "1 hour ago"` output
5. Your distribution and kernel version: `uname -a`
6. OpenRazer version: `pip3 show openrazer`

## Useful Commands Reference

```bash
# Quick system health check
python3 scripts/test_system.py

# Quick device check
lsusb | grep 1532 && echo "Razer device found" || echo "No Razer device found"

# Quick module check
lsmod | grep razer && echo "Modules loaded" || echo "Modules not loaded"

# Quick daemon check
systemctl is-active openrazer-daemon

# Test device capabilities (if devices available)
python3 examples/test_device_capabilities.py

# Set up fake devices for testing
./scripts/quick_test_setup.sh

# List available device test scripts
find scripts/driver -name "test.py" | sort

# Run example scripts
ls examples/*.py

# Check fake device configurations
ls pylib/openrazer/_fake_driver/*.cfg | wc -l
```

This guide should help you debug and test OpenRazer on your system. For additional help, please check the [GitHub issues](https://github.com/openrazer/openrazer/issues) or [wiki](https://github.com/openrazer/openrazer/wiki).