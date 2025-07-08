# TickTick Linux Widget

A modern desktop widget for Linux that displays your active TickTick tasks directly on your desktop. Built with Python and designed specifically for GNOME/Fedora environments.

## Features

- 📝 **Real-time Task Display**: Shows all your active TickTick tasks
- 🔄 **Auto-refresh**: Periodically updates tasks from TickTick API
- 🎨 **Native Look**: Integrates seamlessly with GNOME desktop
- ⚡ **Lightweight**: Minimal resource usage
- 🔒 **Secure**: Uses official TickTick API with secure authentication

## Screenshots

*Coming soon...*

## Installation

### Prerequisites

- Python 3.8+
- Linux (tested on Fedora 42 with GNOME)
- TickTick account

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/TickTick-Linux-Widget.git
cd TickTick-Linux-Widget
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your TickTick credentials:
```bash
cp .env.example .env
# Edit .env with your TickTick API credentials
```

4. Generate your TickTick token:
```bash
python scripts/generate_v1_token.py
```

## Usage

### Backend Only (Current Implementation)
```bash
python -m ticktick_widget.backend.api
```

### GUI Widget (Coming Soon)
```bash
python -m ticktick_widget
```

## Development

### Project Structure
```
ticktick-linux-widget/
├── src/ticktick_widget/          # Main package
│   ├── backend/                  # TickTick API integration
│   ├── gui/                     # Qt-based widget interface
│   ├── config/                  # Configuration management
│   └── utils/                   # Utility functions
├── scripts/                     # Utility scripts
├── tests/                       # Test suite
├── data/                        # Runtime data
└── docs/                        # Documentation
```

### Running Tests
```bash
python -m pytest tests/
```

### Code Formatting
```bash
black src/
isort src/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [TickTick](https://ticktick.com/) for their excellent task management service
- [pyticktick](https://github.com/lazeroffmichael/ticktick-py) for the Python API wrapper 