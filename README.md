# MongoDB Python Toolset

A Python utility library for MongoDB operations, designed to provide a clean interface for database interactions in the MCP (Master Control Program) project.

## Features

- **Connection Management**: Secure and efficient MongoDB connection handling
- **Node Operations**: Create, read, update, and delete nodes with arbitrary properties
- **Edge Operations**: Manage connections between nodes to build graph-like structures
- **Interaction Notes**: Support for stateful interactions with nodes
- **Utility Functions**: Database statistics, snapshots, and maintenance tools

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

## Usage

### Starting MongoDB

Run the MongoDB launcher script to ensure the database is running:

```bash
python mongodb_launcher.py
```

### Basic Operations

```python
# Import necessary modules
from mongo_tools.db_connect import get_db
from mongo_tools.nodes import add_node, get_node_by_name

# Connect to the database
db = get_db()

# Add a node
node_data = {
    "name": "example_node",
    "type": "character",
    "properties": {
        "description": "An example character"
    }
}
node_id = add_node(node_data)

# Retrieve a node
node = get_node_by_name("example_node")

# Always close the connection when done
db.close()
```

For more detailed usage examples, see the [wiki documentation](wiki/mongodb_tools.md).

## Testing

Run the test suite to verify functionality:

```bash
python test_mongo_tools.py
```

## Project Structure

- `mongo_tools/`: Main package containing MongoDB utility modules
- `venv/`: Python virtual environment (not tracked in Git)
- `mongo_data/`: MongoDB data files (not tracked in Git)
- `mongodb_launcher.py`: Script to start MongoDB service
- `test_mongo_tools.py`: Unit tests for the MongoDB toolset
- `wiki/`: Documentation folder

## License

[MIT License](LICENSE)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request 