# MCP - System Utilities and Automation

A collection of command-line utilities for system administration and automation. Currently in early development.

## Basic Usage

To start the MongoDB service:

```bash
python bin/mongodb_launcher.py
```

## Project Structure

- `bin/`: Executable scripts
- `lib/`: Shared functions and libraries
- `docs/`: Documentation files
- `mongo_tools/`: MongoDB utility modules
- `wiki/`: Additional documentation

## Requirements

- Python 3.9+
- MongoDB 4.0+
- pymongo library

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd mcp
```

2. Set up a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install pymongo
```

## License

[MIT License](LICENSE)

## Author

[Your Name] 