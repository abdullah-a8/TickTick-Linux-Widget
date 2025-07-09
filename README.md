# TickTick Linux Widget

A modern desktop widget for Linux that displays your active TickTick tasks directly on your desktop. Built with Python and PyQt6, designed specifically for GNOME/Fedora environments with comprehensive support for Wayland and X11.

## Technical Overview

The TickTick Widget is a desktop application that provides real-time access to your TickTick tasks through a floating, always-available interface. The application employs a sophisticated architecture that balances performance, usability, and cross-platform compatibility. Recent enhancements include interactive task completion, position locking, enhanced timezone handling, and optimized startup performance.

### Core Architecture

The application uses a modular design with clear separation between backend API communication, GUI presentation, and configuration management:

- **Backend Layer**: Handles TickTick API communication using dual authentication (OAuth v1 + v2 credentials)
- **GUI Layer**: PyQt6-based interface with modern card design and responsive layouts
- **Configuration Layer**: JSON-based persistence for themes, positioning, and settings
- **Utility Layer**: Task processing, grouping, and timezone-aware date handling

### Authentication System

The widget uses a hybrid authentication approach leveraging the `pyticktick` library:

- **v1 API**: OAuth flow with client credentials for secure token-based access
- **v2 API**: Username/password authentication for additional API endpoints
- **Credential Management**: Environment variable-based configuration with `.env` support

Required environment variables:
```
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret  
ACCESS_TOKEN=your_oauth_token
EXPIRATION=token_expiration_timestamp
TT_USERNAME=your_ticktick_username
TT_PASSWORD=your_ticktick_password
```

### Task Processing Pipeline

The application implements intelligent task processing with timezone awareness:

1. **Data Retrieval**: Direct API calls to TickTick's batch endpoint (`/batch/check/0`)
2. **Task Filtering**: Extracts only TEXT-type tasks with active status (status=0)
3. **Data Sanitization**: Cleans and validates task data with safe defaults
4. **Enhanced Timezone Conversion**: Smart timezone detection from task data with system fallback
5. **Intelligent Grouping**: User timezone-aware categorization (overdue, today, tomorrow, later)
6. **Sorting Algorithm**: Priority-first sorting within groups, followed by due time or creation time
7. **Real-time Updates**: Automatic cache synchronization after task modifications

### Window Management and Display

The widget implements sophisticated window management to achieve desktop widget behavior:

**Cross-Platform Compatibility**:
- **GNOME Wayland**: Uses `SplashScreen` window type to avoid taskbar appearance
- **X11 Systems**: Uses `Tool` window type with proper window manager hints
- **Automatic Detection**: Environment-based detection (`XDG_CURRENT_DESKTOP`, `XDG_SESSION_TYPE`)

**Window Behavior**:
- Frameless design with custom drag-and-drop positioning
- Configurable always-on-top mode (Ctrl+T toggle)
- Position persistence across application restarts
- Fixed dimensions (460x680) optimized for task display

### Theme System

The application features a comprehensive theme system with QSS stylesheets:

**Theme Architecture**:
- **Base Template**: Unified styling structure with color token substitution
- **Typography Scale**: Inter font family with defined weight and size hierarchy
- **8px Grid System**: Consistent spacing and sizing throughout the interface
- **Dynamic Switching**: Runtime theme changes without application restart

**Available Themes**:
- Dark Mode (default)
- Catppuccin Mocha
- Dracula
- True Black

### Performance Optimizations

The widget implements multiple performance optimization strategies:

**Startup Optimization**:
- **Lazy Loading**: Heavy imports deferred until needed
- **Background Threading**: Task loading happens asynchronously via `QThread`
- **Deferred Operations**: UI setup completes before heavy operations begin
- **Process Identification**: Custom process title for better system integration
- **Autostart Delay**: Configurable 3-second delay for smoother system startup
- **Optimization Script**: Dedicated `optimize_startup.py` for performance tuning

**Runtime Performance**:
- **Efficient Refreshing**: 5-minute auto-refresh cycle with manual refresh option
- **Memory Management**: Proper Qt object lifecycle management
- **Event Optimization**: Debounced position saving to minimize file I/O

### Task Management and Completion

The widget implements comprehensive task interaction capabilities:

**Task Completion System**:
- **Interactive Checkboxes**: Priority-colored checkboxes for each task
- **Real-time Completion**: Click to complete tasks directly from the widget
- **Optimistic Updates**: Immediate UI feedback with rollback on failure
- **Background Processing**: Non-blocking task completion via threaded workers
- **Error Handling**: Visual feedback for completion failures with task restoration
- **API Integration**: Direct integration with TickTick's completion endpoints

**Enhanced User Experience**:
- **Visual Feedback**: Hover effects on checkboxes with semi-transparent highlighting
- **Priority Integration**: Checkbox colors match task priority (Red/Orange/Green/Gray)
- **Status Updates**: Real-time status messages during task operations
- **Batch Operations**: Support for multiple task completions

### Configuration Management

The application uses a sophisticated configuration system:

**Position Management**:
- Automatic position saving with 500ms debounce
- Position lock functionality with Ctrl+L toggle
- JSON persistence in `data/config/position_config.json`
- Default positioning at (100, 100) instead of screen corners
- Lock state persistence across application restarts

**Theme Management**:
- User preference persistence in `data/config/theme_config.json`
- Signal-based theme change propagation
- Fallback handling for missing theme configurations

### Task Organization and Display

The widget employs intelligent task organization:

**Time-Based Grouping**:
- **Overdue**: Tasks past their due date in user's timezone
- **Today**: Tasks due today in user's timezone
- **Tomorrow**: Tasks due tomorrow in user's timezone  
- **Later**: Tasks due after tomorrow or without due dates

**Visual Hierarchy**:
- **Modern Card Design**: Individual task cards with proper spacing
- **Priority Indicators**: Color-coded badges (High/Medium/Low/None) and interactive checkboxes
- **Metadata Display**: Due dates, content previews, and timestamps
- **Progressive Disclosure**: Content truncation for long descriptions
- **Interactive Elements**: Priority-colored checkboxes for task completion with hover feedback

### Autostart Integration

The application provides comprehensive autostart support:

**Desktop Entry Method**:
- Standard XDG autostart with `.desktop` files
- Compatible with GNOME, KDE, XFCE, and other desktop environments
- Configurable startup delays to minimize boot impact

**Systemd User Service**:
- Advanced service management with proper dependencies
- Automatic restart on failure with configurable delays
- Optional user linger support for persistence across logout
- Comprehensive logging and status monitoring

**Startup Optimization**:
- 3-second default delay to reduce system boot impact
- X11 mode enforcement for better Wayland compatibility
- Environment variable propagation for proper GUI initialization

## Installation and Setup

### Dependencies

```bash
pip install pyticktick click loguru pyperclip python-dotenv PyQt6 setproctitle
```

### Authentication Setup

1. Generate TickTick API credentials using the provided script:
```bash
python scripts/generate_v1_token.py
```

2. Create `.env` file with your credentials:
```bash
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
ACCESS_TOKEN=your_oauth_token
EXPIRATION=token_expiration_timestamp
TT_USERNAME=your_ticktick_username
TT_PASSWORD=your_ticktick_password
```

### Running the Widget

**GUI Mode (Primary)**:
```bash
python -m ticktick_widget
```

**CLI Mode (Fetch and Save)**:
```bash
python -m ticktick_widget --cli
```

**Autostart Setup**:
```bash
python -m ticktick_widget --setup-autostart
```

### Autostart Configuration

The widget supports multiple autostart methods:

**Desktop Entry (Recommended)**:
```bash
python scripts/setup_autostart.py --method desktop
```

**Systemd User Service**:
```bash
python scripts/setup_autostart.py --method systemd
```

**Status Check**:
```bash
python scripts/setup_autostart.py --status
```

**Remove Autostart**:
```bash
python scripts/setup_autostart.py --remove
```

## Usage and Controls

### Mouse Controls
- **Drag to Move**: Click and drag anywhere on the widget to reposition (unless position is locked)
- **Task Completion**: Click the priority-colored checkbox to mark tasks as completed
- **Theme Selection**: Use the dropdown in the header to change themes
- **Manual Refresh**: Click the refresh button (⟲) to update tasks immediately

### Keyboard Shortcuts
- **Ctrl+T**: Toggle always-on-top mode
- **Ctrl+L**: Toggle position lock (prevents widget movement)
- **Standard Navigation**: Tab, arrow keys for interface navigation

### Automatic Features
- **Auto-Refresh**: Tasks update every 5 minutes automatically
- **Position Memory**: Widget position is saved and restored on restart
- **Position Lock**: Position lock state persists across sessions (Ctrl+L to toggle)
- **Theme Persistence**: Selected theme is remembered across sessions
- **Task Completion**: Real-time task completion with optimistic UI updates and rollback on failure

## Platform Compatibility

### Desktop Environment Support

| Environment | Desktop Entry | Systemd Service | Window Behavior | Notes |
|-------------|---------------|-----------------|-----------------|-------|
| GNOME (Wayland) | ✅ | ✅ | Good | Uses SplashScreen type |
| GNOME (X11) | ✅ | ✅ | Excellent | Full window manager control |
| KDE Plasma | ✅ | ✅ | Excellent | Native Qt integration |
| XFCE | ✅ | ✅ | Excellent | Standard X11 behavior |
| i3/Sway | ⚠️ | ✅ | Good | Floating window support |
| MATE/Cinnamon | ✅ | ✅ | Excellent | Standard desktop behavior |

### Wayland vs X11 Differences

**X11 Advantages**:
- Complete window manager control
- Reliable taskbar hiding
- Precise window positioning
- Better drag-and-drop behavior

**Wayland Limitations**:
- Limited window management capabilities
- Compositor-dependent behavior
- Potential taskbar/dock appearance
- Reduced positioning control

**Recommendation**: Use X11 mode for optimal experience:
```bash
QT_QPA_PLATFORM=xcb python -m ticktick_widget
```

## Troubleshooting

### Common Issues

**Widget appears in taskbar/dock**:
- Use X11 mode: `QT_QPA_PLATFORM=xcb python -m ticktick_widget`
- Check desktop environment compatibility
- Verify window flags are properly applied

**Authentication failures**:
- Verify all environment variables are set correctly
- Check token expiration date
- Regenerate OAuth token if expired
- Ensure network connectivity to TickTick servers

**Autostart not working**:
- Check autostart status: `python scripts/setup_autostart.py --status`
- Verify desktop environment supports chosen method
- Check systemd service logs: `journalctl --user -u ticktick-widget`

**Performance issues**:
- Use startup optimization: `python scripts/optimize_startup.py`
- Increase autostart delay for slower systems
- Check system resources and Qt installation

**Widget positioning issues**:
- Check if position is locked: press Ctrl+L to toggle
- Reset position: manually edit `data/config/position_config.json`
- Unlock position: set `"locked": false` in position config file

### Debug Information

**Environment Variables**:
- `QT_QPA_PLATFORM=xcb`: Force X11 mode
- `QT_DEBUG_PLUGINS=1`: Debug Qt plugin loading
- `PYTHONPATH`: Ensure module can be found

**Log Locations**:
- Systemd service: `journalctl --user -u ticktick-widget`
- Application output: Console when running manually
- Position config: `data/config/position_config.json` (includes position and lock state)
- Theme config: `data/config/theme_config.json`

## Development

### Project Structure

```
src/ticktick_widget/
├── __main__.py              # Application entry point
├── backend/
│   ├── api.py              # TickTick API integration
│   └── auth.py             # Authentication management
├── config/
│   ├── position_manager.py # Window positioning
│   ├── theme_manager.py    # Theme system
│   ├── themes.py           # Theme definitions
│   └── settings.py         # Configuration handling
├── gui/
│   ├── main_widget.py        # Main application window
│   ├── task_group_widget.py  # Task group containers
│   ├── task_item_widget.py   # Individual task cards
│   └── priority_checkbox.py  # Interactive priority checkboxes
└── utils/
    └── task_grouping.py     # Task organization logic

scripts/
├── generate_v1_token.py    # OAuth token generation
├── setup_autostart.py     # Autostart configuration
└── optimize_startup.py    # Performance optimization

data/
├── config/                 # User configuration files
└── allActiveTasks.json    # Cached task data
```

### Technical Stack

- **GUI Framework**: PyQt6 with modern QSS styling
- **API Client**: pyticktick for TickTick integration  
- **Configuration**: JSON-based with pathlib filesystem handling
- **Threading**: QThread for asynchronous operations
- **Timezone**: zoneinfo for accurate time handling
- **Process Management**: setproctitle for system integration

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.