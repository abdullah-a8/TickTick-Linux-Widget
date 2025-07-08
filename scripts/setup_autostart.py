#!/usr/bin/env python3
"""
TickTick Widget Autostart Setup Script

This script helps set up autostart for the TickTick widget using two methods:
1. Desktop Entry (.desktop file in ~/.config/autostart/)
2. Systemd User Service (for advanced users)

Usage:
    python scripts/setup_autostart.py --method desktop
    python scripts/setup_autostart.py --method systemd
    python scripts/setup_autostart.py --method both
    python scripts/setup_autostart.py --remove
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path
import shutil


class AutostartSetup:
    def __init__(self):
        self.home = Path.home()
        self.project_root = Path(__file__).parent.parent.absolute()
        self.python_path = sys.executable
        
        # Use system python with PYTHONPATH for better compatibility
        # since the module may not be installed in all environments
        self.widget_command = f"env PYTHONPATH={self.project_root}/src python -m ticktick_widget"
        
        # Autostart paths
        self.desktop_autostart_dir = self.home / ".config" / "autostart"
        self.systemd_user_dir = self.home / ".config" / "systemd" / "user"
        
        # File names
        self.desktop_file = "ticktick-widget.desktop"
        self.service_file = "ticktick-widget.service"
    
    def setup_desktop_entry(self):
        """Set up desktop entry autostart method"""
        print("Setting up desktop entry autostart...")
        
        # Ensure autostart directory exists
        self.desktop_autostart_dir.mkdir(parents=True, exist_ok=True)
        
        # Create desktop entry content with X11 mode for better compatibility
        desktop_content = f"""[Desktop Entry]
Type=Application
Name=TickTick Widget
Comment=Desktop widget for TickTick tasks
Exec=env QT_QPA_PLATFORM=xcb {self.widget_command}
Icon=ticktick-widget
StartupNotify=false
NoDisplay=true
X-GNOME-Autostart-enabled=true
X-KDE-autostart-after=panel
X-MATE-Autostart-enabled=true
Categories=Utility;
"""
        
        # Write desktop file
        desktop_path = self.desktop_autostart_dir / self.desktop_file
        with open(desktop_path, 'w') as f:
            f.write(desktop_content)
        
        # Make executable
        desktop_path.chmod(0o755)
        
        print(f"✅ Desktop entry created: {desktop_path}")
        print("   The widget will start automatically on login.")
        
    def setup_systemd_service(self):
        """Set up systemd user service autostart method"""
        print("Setting up systemd user service autostart...")
        
        # Ensure systemd user directory exists
        self.systemd_user_dir.mkdir(parents=True, exist_ok=True)
        
        # Create systemd service content with X11 mode for better compatibility
        service_content = f"""[Unit]
Description=TickTick Desktop Widget
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
Environment=DISPLAY=:0
Environment=WAYLAND_DISPLAY=wayland-0
Environment=QT_QPA_PLATFORM=xcb
Environment=PYTHONPATH={self.project_root}/src
WorkingDirectory={self.project_root}
ExecStart=python -m ticktick_widget
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
"""
        
        # Write service file
        service_path = self.systemd_user_dir / self.service_file
        with open(service_path, 'w') as f:
            f.write(service_content)
        
        print(f"✅ Systemd service created: {service_path}")
        
        # Reload systemd and enable service
        try:
            subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
            subprocess.run(["systemctl", "--user", "enable", self.service_file.replace('.service', '')], check=True)
            print("✅ Systemd service enabled")
            
            # Check if linger is enabled (for persistence across logout)
            username = os.getenv("USER")
            if username:
                result = subprocess.run(["loginctl", "show-user", username], 
                                      capture_output=True, text=True)
                if "Linger=yes" not in result.stdout:
                    print("\n💡 Optional: To make the service persist across logout, run:")
                    print(f"   sudo loginctl enable-linger {username}")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error setting up systemd service: {e}")
            print("   Make sure systemd is available on your system.")
    
    def remove_autostart(self):
        """Remove all autostart configurations"""
        print("Removing autostart configurations...")
        
        removed_any = False
        
        # Remove desktop entry
        desktop_path = self.desktop_autostart_dir / self.desktop_file
        if desktop_path.exists():
            desktop_path.unlink()
            print(f"✅ Removed desktop entry: {desktop_path}")
            removed_any = True
        
        # Remove and disable systemd service
        service_path = self.systemd_user_dir / self.service_file
        if service_path.exists():
            try:
                # Disable and stop service
                subprocess.run(["systemctl", "--user", "disable", self.service_file.replace('.service', '')], 
                             check=False)  # Don't fail if not enabled
                subprocess.run(["systemctl", "--user", "stop", self.service_file.replace('.service', '')], 
                             check=False)  # Don't fail if not running
                
                # Remove service file
                service_path.unlink()
                subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
                
                print(f"✅ Removed systemd service: {service_path}")
                removed_any = True
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Error removing systemd service: {e}")
        
        if not removed_any:
            print("No autostart configurations found to remove.")
    
    def check_status(self):
        """Check current autostart status"""
        print("Autostart Status:")
        print("=" * 50)
        
        # Check desktop entry
        desktop_path = self.desktop_autostart_dir / self.desktop_file
        if desktop_path.exists():
            print("✅ Desktop entry: ENABLED")
            print(f"   Location: {desktop_path}")
        else:
            print("❌ Desktop entry: NOT FOUND")
        
        # Check systemd service
        service_path = self.systemd_user_dir / self.service_file
        if service_path.exists():
            print("✅ Systemd service: FILE EXISTS")
            print(f"   Location: {service_path}")
            
            # Check if enabled
            try:
                result = subprocess.run(["systemctl", "--user", "is-enabled", 
                                       self.service_file.replace('.service', '')], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Systemd service: ENABLED")
                else:
                    print("❌ Systemd service: NOT ENABLED")
            except FileNotFoundError:
                print("❓ Systemd service: CANNOT CHECK (systemctl not found)")
        else:
            print("❌ Systemd service: NOT FOUND")


def main():
    parser = argparse.ArgumentParser(description="Set up autostart for TickTick Widget")
    parser.add_argument('--method', choices=['desktop', 'systemd', 'both'], 
                       help='Autostart method to set up')
    parser.add_argument('--remove', action='store_true', 
                       help='Remove all autostart configurations')
    parser.add_argument('--status', action='store_true', 
                       help='Check current autostart status')
    
    args = parser.parse_args()
    
    setup = AutostartSetup()
    
    if args.remove:
        setup.remove_autostart()
    elif args.status:
        setup.check_status()
    elif args.method:
        if args.method == 'desktop':
            setup.setup_desktop_entry()
        elif args.method == 'systemd':
            setup.setup_systemd_service()
        elif args.method == 'both':
            setup.setup_desktop_entry()
            print()  # Empty line for separation
            setup.setup_systemd_service()
            print("\n💡 Note: Both methods are now active. You may want to choose only one.")
    else:
        # Interactive mode
        print("TickTick Widget Autostart Setup")
        print("=" * 40)
        print("Choose an autostart method:")
        print("1. Desktop Entry (recommended for most users)")
        print("2. Systemd Service (for advanced users)")
        print("3. Both methods")
        print("4. Check current status")
        print("5. Remove autostart")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            setup.setup_desktop_entry()
        elif choice == '2':
            setup.setup_systemd_service()
        elif choice == '3':
            setup.setup_desktop_entry()
            print()
            setup.setup_systemd_service()
        elif choice == '4':
            setup.check_status()
        elif choice == '5':
            setup.remove_autostart()
        else:
            print("Invalid choice. Exiting.")


if __name__ == "__main__":
    main() 