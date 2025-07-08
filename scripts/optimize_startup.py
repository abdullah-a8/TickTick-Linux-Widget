#!/usr/bin/env python3
"""
TickTick Widget Startup Optimization Script

This script optimizes existing autostart configurations to reduce startup slowdown.
It adds delays and other optimizations to minimize boot impact.

Usage:
    python scripts/optimize_startup.py
"""

import sys
import os
import subprocess
from pathlib import Path


class StartupOptimizer:
    def __init__(self):
        self.home = Path.home()
        self.project_root = Path(__file__).parent.parent.absolute()
        
        # Autostart paths
        self.desktop_autostart_dir = self.home / ".config" / "autostart"
        self.systemd_user_dir = self.home / ".config" / "systemd" / "user"
        
        # File names
        self.desktop_file = "ticktick-widget.desktop"
        self.service_file = "ticktick-widget.service"
    
    def optimize_desktop_entry(self):
        """Optimize existing desktop entry to include startup delay"""
        desktop_path = self.desktop_autostart_dir / self.desktop_file
        
        if not desktop_path.exists():
            print("❌ Desktop entry not found. No optimization needed.")
            return False
        
        try:
            # Read current content
            with open(desktop_path, 'r') as f:
                content = f.read()
            
            # Check if already optimized
            if 'sleep 3' in content:
                print("✅ Desktop entry already optimized.")
                return True
            
            # Add delay and optimization
            optimized_content = content.replace(
                'Exec=env QT_QPA_PLATFORM=xcb',
                'Exec=sh -c \'sleep 3 && env QT_QPA_PLATFORM=xcb'
            ).replace(
                'ticktick_widget\n',
                'ticktick_widget\'\nX-GNOME-Autostart-Delay=3\n'
            )
            
            # Write optimized content
            with open(desktop_path, 'w') as f:
                f.write(optimized_content)
            
            print(f"✅ Optimized desktop entry: {desktop_path}")
            print("   Added 3-second startup delay to reduce boot impact.")
            return True
            
        except Exception as e:
            print(f"❌ Error optimizing desktop entry: {e}")
            return False
    
    def optimize_systemd_service(self):
        """Optimize existing systemd service to include startup delay"""
        service_path = self.systemd_user_dir / self.service_file
        
        if not service_path.exists():
            print("❌ Systemd service not found. No optimization needed.")
            return False
        
        try:
            # Read current content
            with open(service_path, 'r') as f:
                content = f.read()
            
            # Check if already optimized
            if 'ExecStartPre=/bin/sleep 3' in content:
                print("✅ Systemd service already optimized.")
                return True
            
            # Add delay
            optimized_content = content.replace(
                'ExecStart=python -m ticktick_widget',
                'ExecStartPre=/bin/sleep 3\nExecStart=python -m ticktick_widget'
            )
            
            # Write optimized content
            with open(service_path, 'w') as f:
                f.write(optimized_content)
            
            # Reload systemd
            subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
            
            print(f"✅ Optimized systemd service: {service_path}")
            print("   Added 3-second startup delay to reduce boot impact.")
            return True
            
        except Exception as e:
            print(f"❌ Error optimizing systemd service: {e}")
            return False
    
    def show_additional_tips(self):
        """Show additional optimization tips"""
        print("\n🚀 Additional Optimization Tips:")
        print("=" * 50)
        print("1. The widget now uses lazy loading - imports happen only when needed")
        print("2. Position and theme loading are now deferred until after startup")
        print("3. Task loading happens in a background thread")
        print("4. Startup delays prevent system boot slowdown")
        print("\n💡 If startup is still slow, you can:")
        print("   • Increase the delay in autostart files (change 'sleep 3' to 'sleep 5')")
        print("   • Use only one autostart method (desktop entry OR systemd)")
        print("   • Consider manual startup for fastest boot times")


def main():
    print("TickTick Widget Startup Optimizer")
    print("=" * 40)
    print("This script optimizes your existing autostart configuration")
    print("to reduce system startup slowdown.\n")
    
    optimizer = StartupOptimizer()
    
    # Optimize existing configurations
    desktop_optimized = optimizer.optimize_desktop_entry()
    systemd_optimized = optimizer.optimize_systemd_service()
    
    if desktop_optimized or systemd_optimized:
        print("\n✅ Optimization complete!")
        print("   Your widget will now start with a delay to reduce boot impact.")
        optimizer.show_additional_tips()
    else:
        print("\n❌ No autostart configurations found to optimize.")
        print("   Run setup_autostart.py first to enable autostart.")


if __name__ == "__main__":
    main() 