#!/bin/bash
#
# Quick setup script for testing OpenRazer without physical devices
# This is a simplified version of setup_fake_devices.sh that doesn't require GUI
#

set -e

SCRIPT_DIR="$(dirname "$0")"
CONFIG_DIR="/tmp/daemon_config"
TEST_DIR="/tmp/daemon_test"

echo "OpenRazer Quick Test Setup"
echo "=========================="

# Clean up previous test sessions
echo "Cleaning up previous test sessions..."
rm -rf "$CONFIG_DIR" "$TEST_DIR"
mkdir -p "$CONFIG_DIR"/{data,logs}
mkdir -p "$TEST_DIR"

# Kill existing daemon
echo "Stopping existing daemon..."
pkill openrazer-daemon 2>/dev/null || true
sleep 2

# Create some common fake devices for testing
echo "Creating fake devices..."
"$SCRIPT_DIR/create_fake_device.py" --dest "$TEST_DIR" \
    razer_blackwidow_chroma \
    razer_deathadder_chroma \
    razer_firefly \
    razer_goliathus_chroma

echo "Fake devices created in $TEST_DIR:"
ls -la "$TEST_DIR"

# Start daemon in background
echo "Starting daemon with fake devices..."
cd "$SCRIPT_DIR/.."
PYTHONPATH="pylib:daemon" python3 ./daemon/run_openrazer_daemon.py \
    --verbose -F \
    --run-dir "$CONFIG_DIR/data" \
    --log-dir "$CONFIG_DIR/logs" \
    --test-dir "$TEST_DIR" &

DAEMON_PID=$!
echo "Daemon started with PID: $DAEMON_PID"

# Wait a moment for daemon to start
sleep 3

# Test if daemon is working
echo "Testing daemon connection..."
if PYTHONPATH="pylib" python3 -c "
from openrazer.client import DeviceManager
dm = DeviceManager()
print(f'Found {len(dm.devices)} devices:')
for device in dm.devices:
    print(f'  - {device.name}')
" 2>/dev/null; then
    echo "✓ Success! Fake devices are working."
    echo ""
    echo "You can now test OpenRazer with:"
    echo "  python3 examples/list_devices.py"
    echo "  python3 examples/basic_effect.py"
    echo "  python3 scripts/test_system.py"
    echo ""
    echo "To stop the test environment:"
    echo "  kill $DAEMON_PID"
    echo "  rm -rf $CONFIG_DIR $TEST_DIR"
else
    echo "✗ Failed to connect to daemon"
    kill $DAEMON_PID 2>/dev/null || true
    exit 1
fi

# Keep the script running so daemon stays alive
echo "Test environment is ready. Press Ctrl+C to stop."
trap "echo 'Stopping daemon...'; kill $DAEMON_PID 2>/dev/null || true; rm -rf $CONFIG_DIR $TEST_DIR; exit 0" INT

# Wait for daemon to finish or user interrupt
wait $DAEMON_PID