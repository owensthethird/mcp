# MCP - System Utilities and Automation

A collection of command-line utilities for system administration and automation. Currently in early development.

## Features

- **MongoDB Management**: Tools for launching, monitoring, and interacting with MongoDB
- **Node Operations**: Create, read, update, and delete operations for node documents
- **Edge Operations**: Tools for managing connections between nodes
- **Data Utilities**: Tools for database snapshots, restoration, and statistics

## Project Structure

- `bin/`: Executable scripts
- `lib/`: Shared functions and libraries
- `docs/`: Documentation files
- `mongo_tools/`: MongoDB utility modules
- `tests/`: Unit and integration tests
- `logs/`: Application logs
- `wiki/`: Additional documentation

## Requirements

- Python 3.9+
- MongoDB 4.0+
- Required Python packages:
  - pymongo
  - bson

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

## Basic Usage

### Starting MongoDB

The MongoDB launcher script provides a simple way to start a MongoDB server with proper configuration:

```bash
python bin/mongodb_launcher.py
```

With additional options:
```bash
# Start with custom config file and data directory
python bin/mongodb_launcher.py --config my_config.cfg --data-dir ./custom_data

# Start with verbose output and custom port
python bin/mongodb_launcher.py --verbose --port 27018
```

### Testing MongoDB Connection

To verify your MongoDB connection is working:

```bash
python tests/test_mongodb.py
```

### Working with MongoDB Data

Here's a simple example showing how to use the MongoDB tools to manage data:

```python
# Import MongoDB tools
from mongo_tools.db_connect import get_db
from mongo_tools.nodes import add_node, get_node_by_name, update_node
from mongo_tools.utility import create_database_snapshot

# Connect to the database
db = get_db('my_application')

try:
    # Add a new node
    character = {
        "name": "Player Character",
        "type": "character",
        "properties": {
            "health": 100,
            "level": 1,
            "inventory": ["health potion", "sword"]
        }
    }
    
    # Add the node to the database
    node_id = add_node(character)
    
    # Retrieve the node by name
    player = get_node_by_name("Player Character")
    print(f"Player Level: {player['properties']['level']}")
    
    # Update the player's level
    update_node(node_id, {"properties.level": 2})
    
    # Create a backup snapshot
    snapshot_file = create_database_snapshot()
    print(f"Database snapshot created: {snapshot_file}")
    
finally:
    # Always close the connection when done
    db.close()
```

## Development

### Running Tests

To run the test suite:

```bash
python tests/test_mongo_tools.py
```

### Logging

Logs are stored in the `logs/` directory:
- `mcp.log`: Contains all application logs
- `mcp_errors.log`: Contains only error-level logs

## Documentation

For more detailed documentation, see the [docs](docs/) directory or the [wiki](wiki/).

## License

[MIT License](LICENSE)

## Author

[Your Name] 