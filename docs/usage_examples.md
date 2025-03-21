# Usage Examples

This document provides detailed examples of how to use the MCP toolset in various scenarios.

## Basic MongoDB Operations

### Connecting to MongoDB

```python
from mongo_tools.db_connect import get_db

# Connect to default database
db = get_db()

# Connect to a specific database
custom_db = get_db('my_custom_db')

# Connect with non-default connection string and timeout
remote_db = get_db(
    db_name='production_db',
    connection_string='mongodb://user:password@remote-server:27017/',
    timeout=10000  # 10 seconds
)

# Always close connections when done
try:
    # Your database operations here
    collections = db.list_collection_names()
    print(f"Available collections: {collections}")
finally:
    db.close()
```

### Managing Nodes

```python
from mongo_tools.nodes import add_node, get_node_by_name, update_node, delete_node_by_name, list_all_nodes

# Create a node
location_node = {
    "name": "Forest Clearing",
    "type": "location",
    "properties": {
        "description": "A peaceful clearing in the forest",
        "danger_level": 1,
        "resources": ["berries", "herbs", "water"]
    }
}

# Add the node to the database
location_id = add_node(location_node)
print(f"Created location with ID: {location_id}")

# Retrieve the node
location = get_node_by_name("Forest Clearing")
print(f"Location description: {location['properties']['description']}")

# Update node properties
update_node(location_id, {
    "properties.danger_level": 2,
    "properties.resources": ["berries", "herbs", "water", "mushrooms"]
})

# Get all nodes sorted by name
all_locations = list_all_nodes(sort_field="name", sort_direction=1)
print(f"Found {len(all_locations)} nodes")

# Delete a node
delete_node_by_name("Forest Clearing")
```

### Managing Connections (Edges)

```python
from mongo_tools.nodes import add_node
from mongo_tools.edges import add_edge, get_connections, remove_edge

# Create two nodes
village = {
    "name": "Riverside Village",
    "type": "location"
}
forest = {
    "name": "Dark Forest",
    "type": "location"
}

village_id = add_node(village)
forest_id = add_node(forest)

# Create an edge (connection) between them
path_data = {
    "type": "path",
    "distance": 3,
    "difficulty": "easy"
}
add_edge(village_id, forest_id, path_data)

# Get all connections from the village
connections = get_connections(village_id)
for conn in connections:
    print(f"Connection to {conn['target_name']} - Distance: {conn['distance']}")

# Remove the connection
remove_edge(village_id, forest_id)
```

## Database Utilities

### Creating and Restoring Snapshots

```python
from mongo_tools.utility import create_database_snapshot, restore_database_snapshot

# Create a database snapshot with a custom directory
snapshot_file = create_database_snapshot(directory='my_backups')
print(f"Database snapshot created at: {snapshot_file}")

# Restore from a specific snapshot file
success = restore_database_snapshot('my_backups/mongodb_snapshot_20250321_123456.json')
if success:
    print("Database successfully restored from snapshot")
else:
    print("Failed to restore database")
```

### Database Maintenance

```python
from mongo_tools.utility import clear_collection, get_database_stats

# Clear a specific collection
cleared_count = clear_collection('temp_data')
print(f"Cleared {cleared_count} documents from temp_data collection")

# Get database statistics
stats = get_database_stats()
print(f"Database collections: {stats['collections']}")
print("Document counts by collection:")
for collection, count in stats['counts'].items():
    print(f"  - {collection}: {count} documents")
```

## Command-line Tools

### MongoDB Launcher

```bash
# Basic usage - start MongoDB with default settings
python bin/mongodb_launcher.py

# Start with custom configuration file
python bin/mongodb_launcher.py --config custom_mongo.cfg

# Start on a specific port with verbose output
python bin/mongodb_launcher.py --port 27018 --verbose

# Start with custom data directory
python bin/mongodb_launcher.py --data-dir D:/mongodb/data
```

### MongoDB Connection Test

```bash
# Basic usage - test local MongoDB connection
python tests/test_mongodb.py

# Test connection to a remote MongoDB server
python tests/test_mongodb.py --uri mongodb://remote-server:27017/

# Test with extended timeout
python tests/test_mongodb.py --timeout 5000
``` 