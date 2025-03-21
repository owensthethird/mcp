# MongoDB Tools Batch Operations Examples

This directory contains example files to demonstrate the batch operations functionality of the MongoDB CLI tools.

## Sample Files

- `sample_nodes.json`: Sample JSON file with location and character nodes
- `sample_nodes.csv`: Sample CSV file with various node types

## Usage Examples

### Importing Nodes

```bash
# Import nodes from JSON
python bin/mongo_tools_cli.py node import --file examples/sample_nodes.json

# Import nodes from CSV, updating any existing nodes
python bin/mongo_tools_cli.py node import --file examples/sample_nodes.csv --update

# Import from a file with explicit format specification
python bin/mongo_tools_cli.py node import --file examples/sample_nodes.json --format json
```

### Exporting Nodes

```bash
# Export all nodes to JSON
python bin/mongo_tools_cli.py node export --file export_all.json

# Export only character nodes
python bin/mongo_tools_cli.py node export --file characters.json --query '{"type": "character"}'

# Export locations with danger level greater than 3
python bin/mongo_tools_cli.py node export --file dangerous_locations.json --query '{"type": "location", "properties.danger_level": {"$gt": 3}}'

# Export specific fields to CSV
python bin/mongo_tools_cli.py node export --file characters.csv --format csv --fields "name,type,properties.health,properties.strength"

# Export with MongoDB ObjectIds included
python bin/mongo_tools_cli.py node export --file export_with_ids.json --include-ids
```

## Creating Connections Between Imported Nodes

After importing nodes, you might want to create connections between them:

```bash
# Create a connection from Town Square to Tavern
python bin/mongo_tools_cli.py edge add --from "Town Square" --to "Tavern" --data '{"type": "path", "distance": 1}'

# Create a connection from Tavern to Blacksmith
python bin/mongo_tools_cli.py edge add --from "Tavern" --to "Blacksmith" --data '{"type": "path", "distance": 2}'

# Create a connection from Town Square to Dark Forest
python bin/mongo_tools_cli.py edge add --from "Town Square" --to "Dark Forest" --data '{"type": "path", "distance": 3}'
```

## Checking the Results

After importing nodes and creating connections, you can check the results:

```bash
# List all nodes
python bin/mongo_tools_cli.py node list

# Get details for a specific node
python bin/mongo_tools_cli.py node get --name "Town Square"

# See connections from a node
python bin/mongo_tools_cli.py edge get --name "Town Square"
```

## Example Workflow

1. Import locations: `python bin/mongo_tools_cli.py node import --file examples/sample_nodes.json`
2. Import characters: `python bin/mongo_tools_cli.py node import --file examples/sample_nodes.csv --update`
3. Create connections: `python bin/mongo_tools_cli.py edge add --from "Town Square" --to "Tavern" --data '{"type": "path"}'`
4. View the database stats: `python bin/mongo_tools_cli.py stats`
5. Export all nodes: `python bin/mongo_tools_cli.py node export --file all_nodes.json` 