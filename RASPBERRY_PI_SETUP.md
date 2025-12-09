# Raspberry Pi Setup Guide

This guide will walk you through setting up a Raspberry Pi running Raspberry Pi OS Lite to run the WLED Christmas Tree Controller.

## Prerequisites

- Raspberry Pi (3, 4, or 5 recommended)
- Fresh installation of **Raspberry Pi OS Lite** (latest version)
- Network connection (WiFi or Ethernet)
- SSH access to your Raspberry Pi

## Step 1: Update the System

First, update your Raspberry Pi to ensure all packages are current:

```bash
sudo apt update
sudo apt upgrade -y
```

This may take several minutes depending on how many updates are available.

## Step 2: Install Required System Packages

Install Python 3, pip, git, and other necessary dependencies:

```bash
sudo apt install -y python3 python3-pip python3-venv git
```

### Additional Required Packages

Install system libraries needed for the Python packages:

```bash
sudo apt install -y python3-dev python3-numpy
```

## Step 3: Verify Python Installation

Check that Python 3 and pip are installed correctly:

```bash
python3 --version
pip3 --version
```

You should see version numbers for both commands (Python 3.9+ and pip 20+).

## Step 4: Clone the Repository

Clone the WLED Christmas Tree Controller from GitHub:

```bash
cd ~
git clone https://github.com/Gravydigz/wled-christmas-tree.git
cd wled-christmas-tree
```

## Step 5: Create a Python Virtual Environment

It's best practice to use a virtual environment to avoid conflicts with system packages:

```bash
python3 -m venv venv
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

You should see `(venv)` appear at the beginning of your command prompt.

**Note:** You'll need to activate this virtual environment every time you run the program. To make it easier, you can add the activation command to your `.bashrc`:

```bash
echo "source ~/wled-christmas-tree/venv/bin/activate" >> ~/.bashrc
```

## Step 6: Install Python Dependencies

With the virtual environment activated, install the required Python packages:

```bash
pip install -r requirements.txt
```

This will install:
- requests (for HTTP API communication)
- websocket-client (for WebSocket support)
- numpy (for numerical operations)
- pyyaml (for configuration files)
- pillow (for image processing)

## Step 7: Verify Installation

Test that the packages are installed correctly:

```bash
python3 -c "import requests, yaml, numpy; print('All packages imported successfully!')"
```

If you see "All packages imported successfully!", everything is installed correctly.

## Step 8: Configure Your Setup

Now follow the instructions in `GETTING_STARTED.md` to:

1. Update `config/config.yaml` with your WLED device IP address
2. Add your LED coordinate CSV file
3. Test your coordinates
4. Run your first effect

```bash
# Quick link to getting started guide
cat GETTING_STARTED.md
```

## Optional: Set Up Auto-Start on Boot

If you want the program to start automatically when the Raspberry Pi boots:

### Create a systemd service file:

```bash
sudo nano /etc/systemd/system/wled-tree.service
```

Add the following content (adjust paths and effect as needed):

```ini
[Unit]
Description=WLED Christmas Tree Controller
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/wled-christmas-tree
Environment="PATH=/home/pi/wled-christmas-tree/venv/bin"
ExecStart=/home/pi/wled-christmas-tree/venv/bin/python3 /home/pi/wled-christmas-tree/main.py --coords /home/pi/wled-christmas-tree/config/tree_coordinates.csv --effect height_gradient
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save and exit (Ctrl+X, then Y, then Enter).

### Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable wled-tree.service
sudo systemctl start wled-tree.service
```

### Check service status:

```bash
sudo systemctl status wled-tree.service
```

### View logs:

```bash
journalctl -u wled-tree.service -f
```

## Optional: Set Static IP Address

For reliable connection to your WLED device, you may want to set a static IP for your Raspberry Pi:

```bash
sudo nano /etc/dhcpcd.conf
```

Add at the end (adjust for your network):

```
interface eth0
static ip_address=192.168.1.50/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8

# Or for WiFi:
interface wlan0
static ip_address=192.168.1.50/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

Reboot to apply:

```bash
sudo reboot
```

## Troubleshooting

### "Command not found" errors

Make sure you've activated the virtual environment:
```bash
source ~/wled-christmas-tree/venv/bin/activate
```

### Permission errors

If you get permission errors when installing packages, make sure you're using the virtual environment and NOT using `sudo pip`.

### Network connectivity issues

Check that both your Raspberry Pi and WLED device are on the same network:
```bash
ping <your-wled-ip>
```

### Memory issues on older Raspberry Pi models

If you have a Raspberry Pi Zero or older model with limited RAM:
- Lower the FPS in `config/config.yaml` (try 15-20)
- Use simpler effects like `rainbow` instead of complex 3D effects
- Consider upgrading to a Raspberry Pi 3 or 4

### Python package installation fails

If numpy or other packages fail to install, you may need additional development packages:
```bash
sudo apt install -y build-essential libatlas-base-dev gfortran
```

## Performance Tips

1. **Disable unnecessary services** to free up resources:
   ```bash
   sudo systemctl disable bluetooth
   sudo systemctl disable avahi-daemon
   ```

2. **Increase GPU memory** (optional, helps with calculations):
   ```bash
   sudo raspi-config
   ```
   Navigate to: Performance Options → GPU Memory → Set to 16 or 32

3. **Overclock** (Pi 3/4 only, optional):
   Use `sudo raspi-config` to access overclocking options

## Next Steps

Once your Raspberry Pi is set up, continue with `GETTING_STARTED.md` to configure your Christmas tree and run effects!

```bash
# View the getting started guide
cat GETTING_STARTED.md
```

## Summary of Commands

Quick reference for future use:

```bash
# Activate virtual environment
source ~/wled-christmas-tree/venv/bin/activate

# Update code from GitHub
cd ~/wled-christmas-tree
git pull

# Run an effect
python3 main.py --coords config/tree_coordinates.csv --effect height_gradient

# View logs (if using systemd service)
journalctl -u wled-tree.service -f
```

Happy coding! 🎄
