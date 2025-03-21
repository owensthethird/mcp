# MongoDB Toolset Documentation

## Overview
The MongoDB toolset provides a collection of utility functions for interacting with MongoDB databases in the MCP (Master Control Program) project. This toolset enables basic CRUD operations on nodes and edges, as well as database maintenance operations like creating snapshots and retrieving statistics.

## Connection Management

The toolset uses a custom wrapper class `DBConnection` to manage MongoDB connections properly. This class ensures that MongoDB client connections are always properly closed after each operation, preventing resource leaks.

### Usage:
```python
from mongo_tools.db_connect import get_db

# Get a database connection
db = get_db()  # Uses default 'test_db' database
# or
db = get_db('custom_db_name')

# Use the database
collection = db['collection_name']
result = collection.find_one({})

# Always close the connection when done
db.close()
```

## Command-Line Interface

The MongoDB toolset includes a command-line interface for easy access to common operations. The CLI script is located at `bin/mongo_tools_cli.py`.

### Basic Usage

```bash
# Show available commands
python bin/mongo_tools_cli.py --help

# Node operations
python bin/mongo_tools_cli.py node add --name "Test Node" --type "location"
python bin/mongo_tools_cli.py node get --name "Test Node"
python bin/mongo_tools_cli.py node list

# Edge operations
python bin/mongo_tools_cli.py edge add --from "Source Node" --to "Target Node"
python bin/mongo_tools_cli.py edge get --name "Source Node"

# Database operations
python bin/mongo_tools_cli.py stats
python bin/mongo_tools_cli.py snapshot create
python bin/mongo_tools_cli.py clear --collection nodes
```

For more detailed examples, see the [usage examples](../docs/usage_examples.md) documentation.

## Logging

The MongoDB toolset uses a standardized logging system that writes logs to console and files:

- `logs/mcp.log`: Contains all application logs
- `logs/mcp_errors.log`: Contains only error-level logs

To configure logging in your own scripts that use mongo_tools:

```python
from lib.logging_config import configure_logger

# Configure a logger for your module
logger = configure_logger("my_module")

# Use the logger
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

## Node Operations

Functions to manage nodes in the database:

### `add_node(node_data)`
Add a new node to the database.

```python
from mongo_tools.nodes import add_node

node = {
    "name": "character_name",
    "type": "character",
    "properties": {
        "description": "A description",
        "health": 100
    }
}

node_id = add_node(node)
```

### `get_node_by_name(name)`
Retrieve a node by its name.

```python
from mongo_tools.nodes import get_node_by_name

node = get_node_by_name("character_name")
```

### `get_node_by_id(node_id)`
Retrieve a node by its ID.

```python
from mongo_tools.nodes import get_node_by_id
from bson.objectid import ObjectId

node_id = ObjectId("5f7b1a2b3c4d5e6f7a8b9c0d")
node = get_node_by_id(node_id)
```

### `update_node(node_id, updates)`
Update a node with specified updates.

```python
from mongo_tools.nodes import update_node

updates = {
    "properties.health": 80,
    "properties.status": "injured"
}

update_node(node_id, updates)
```

### `delete_node_by_name(name)`
Delete a node by its name.

```python
from mongo_tools.nodes import delete_node_by_name

delete_node_by_name("character_name")
```

### `list_all_nodes(limit=None, sort_field=None, sort_direction=1)`
List all nodes in the database with optional sorting and limiting.

```python
from mongo_tools.nodes import list_all_nodes

# Get all nodes
all_nodes = list_all_nodes()

# Get top 10 nodes sorted by name
sorted_nodes = list_all_nodes(limit=10, sort_field="name", sort_direction=1)
```

## Edge Operations

Functions to manage connections between nodes:

### `add_edge(from_node_id, to_node_id, edge_data=None)`
Create a connection between two nodes.

```python
from mongo_tools.edges import add_edge

edge_data = {
    "type": "path",
    "distance": 5
}

add_edge(source_node_id, target_node_id, edge_data)
```

### `get_connections(node_id)`
Get all connections from a node.

```python
from mongo_tools.edges import get_connections

connections = get_connections(node_id)
```

### `remove_edge(from_node_id, to_node_id)`
Remove a connection between nodes.

```python
from mongo_tools.edges import remove_edge

remove_edge(source_node_id, target_node_id)
```

## Interaction Notes

Functions to manage interaction notes on nodes:

### `add_interaction_note(node_id, note)`
Add an interaction note to a node.

```python
from mongo_tools.notes import add_interaction_note

note = {
    "trigger": "conversation",
    "effect": "Reveals secret location",
    "clear_after_use": True
}

add_interaction_note(node_id, note)
```

### `process_and_clear_notes(node_id)`
Process notes and clear those marked for deletion.

```python
from mongo_tools.notes import process_and_clear_notes

process_and_clear_notes(node_id)
```

## Utility Functions

Database utility functions:

### `clear_collection(collection_name, db_name='test_db')`
Remove all documents from a collection.

```python
from mongo_tools.utility import clear_collection

clear_collection('nodes')
```

### `create_database_snapshot(directory='backups')`
Create a JSON snapshot of the entire database.

```python
from mongo_tools.utility import create_database_snapshot

snapshot_file = create_database_snapshot()
# or
snapshot_file = create_database_snapshot('custom_backup_dir')
```

### `restore_database_snapshot(filename)`
Restore database from a snapshot file.

```python
from mongo_tools.utility import restore_database_snapshot

success = restore_database_snapshot('backups/mongodb_snapshot_20250321_123456.json')
```

### `get_database_stats()`
Get statistics about the database.

```python
from mongo_tools.utility import get_database_stats

stats = get_database_stats()
```

## Best Practices

1. Always ensure that MongoDB connections are properly closed by using the `try-finally` pattern or the wrapper class's close method.
2. Use descriptive names for nodes and clear type categorization.
3. Create regular database snapshots to prevent data loss.
4. Consider performance implications for large collections and use appropriate indexes.
5. Use the standardized logging system for better debugging and error tracking.
6. Use the command-line interface for quick operations and testing.

## Troubleshooting

1. If MongoDB is not running, run `bin/mongodb_launcher.py` to start the service.
2. Resource warnings about unclosed connections indicate that `db.close()` was not called. Use the proper connection management pattern.
3. For large collections, consider using pagination in your queries to avoid memory issues.
4. If encountering errors, check the logs in the `logs/` directory for detailed information.
5. The CLI tool provides helpful error messages and can be used to diagnose common issues. 