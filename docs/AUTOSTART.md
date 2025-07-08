# TickTick Widget Autostart Setup

This guide explains how to set up the TickTick widget to start automatically when you log into your Linux desktop.

## Quick Setup

The easiest way to set up autostart is using the built-in setup tool:

```bash
# Interactive setup (recommended)
python -m ticktick_widget --setup-autostart

# Or run the setup script directly
python scripts/setup_autostart.py
```

## Autostart Methods

### 1. Desktop Entry Method (Recommended)

This is the standard Linux method that works with most desktop environments (GNOME, KDE, XFCE, etc.).

**Advantages:**
- Works with all major desktop environments
- Easy to manage through system settings
- Standard Linux approach

**Setup:**
```bash
python scripts/setup_autostart.py --method desktop
```

This creates a `.desktop` file in `~/.config/autostart/` that tells your desktop environment to start the widget on login.

### 2. Systemd User Service Method

This is for advanced users who want more control over the service lifecycle.

**Advantages:**
- More robust restart handling
- Can persist across logout (with linger)
- Better logging and service management
- Works on headless systems

**Setup:**
```bash
python scripts/setup_autostart.py --method systemd
```

**Optional - Persist across logout:**
```bash
sudo loginctl enable-linger $USER
```

## Managing Autostart

### Check Status
```bash
python scripts/setup_autostart.py --status
```

### Remove Autostart
```bash
python scripts/setup_autostart.py --remove
```

### Manual Systemd Control
If you're using the systemd method, you can control the service manually:

```bash
# Start the service now
systemctl --user start ticktick-widget

# Stop the service
systemctl --user stop ticktick-widget

# Check service status
systemctl --user status ticktick-widget

# View logs
journalctl --user -u ticktick-widget -f
```

## Troubleshooting

### Widget doesn't start on login
1. Check if autostart is properly configured:
   ```bash
   python scripts/setup_autostart.py --status
   ```

2. For desktop entry method:
   - Check if the file exists: `ls ~/.config/autostart/ticktick-widget.desktop`
   - Verify desktop environment supports XDG autostart

3. For systemd method:
   - Check service status: `systemctl --user status ticktick-widget`
   - View logs: `journalctl --user -u ticktick-widget`

### Widget appears in taskbar/dock on GNOME Wayland
GNOME on Wayland has limited support for Qt window management flags. The autostart configuration now uses X11 mode by default (`QT_QPA_PLATFORM=xcb`) which provides better taskbar avoidance.

**Manual X11 mode:**
```bash
QT_QPA_PLATFORM=xcb python -m ticktick_widget
```

### Widget Controls and Features
- **Mouse Dragging**: Click and drag anywhere on the widget to move it
- **Always On Top Toggle**: Press `Ctrl+T` to toggle whether the widget stays on top
- **Default Position**: Widget starts at (100, 100) instead of corner
- **Better Window Behavior**: No longer aggressively stays on top by default

### Wayland vs X11 Differences
- **X11**: Full window manager control, reliable taskbar hiding, better dragging
- **Wayland**: Limited window management, may appear in dock depending on compositor
- **Recommendation**: Use X11 mode (`QT_QPA_PLATFORM=xcb`) for best experience

## Position Persistence

The widget automatically remembers its screen position and will restore it when restarted. This works both for manual launches and autostart.

**How it works:**
- Position is saved automatically when you drag the widget to a new location
- Position is also saved when the widget is moved by any other means
- The position is stored in `data/config/position_config.json`
- Default position is (100, 100) if no saved position exists
- Position saving has a 500ms delay to avoid excessive disk writes during dragging

**Configuration file example:**
```json
{
  "x": 159,
  "y": 49,
  "version": "1.0"
}
```

**To reset position to default:**
You can either:
1. Delete the config file: `rm data/config/position_config.json`
2. Edit the file manually to set desired x,y coordinates

This ensures your widget appears in the same location every time, whether started manually or through autostart.

## Platform Support

| Desktop Environment | Desktop Entry | Systemd Service | Notes |
|-------------------|---------------|-----------------|-------|
| GNOME (X11/Wayland) | ✅ | ✅ | Full support |
| KDE Plasma | ✅ | ✅ | Full support |
| XFCE | ✅ | ✅ | Full support |
| i3/Sway | ⚠️ | ✅ | Systemd recommended |
| MATE/Cinnamon | ✅ | ✅ | Full support |

## Security Considerations

- The widget requires your TickTick API credentials to function
- Credentials are stored in your home directory
- Autostart services run with your user permissions
- No elevation or special permissions required 